import os
import textwrap
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.agents import tool, initialize_agent, AgentType
import base64
import boto3
import certifi
import httpx
import kubernetes
import openai
from eks_token import get_token

functions = []


def banner(title: str, message: str):
    print("-" * 80)
    print(title.strip())
    print(textwrap.indent(message.strip(), " " * 4))
    print("-" * 80)


def ensure_mitmproxy_ca_cert_to_certifi():
    # Backup the original certifi file
    certifi_orig_path = Path(certifi.where() + ".original")
    if not certifi_orig_path.exists():
        certifi_orig_path.write_text(Path(certifi.where()).read_text())

    # Add mitmproxy's CA cert to the certifi bundle
    Path(certifi.where()).write_text(
        certifi_orig_path.read_text()
        + "\n\n# mitmproxy-ca-cert.pem\n"
        + (Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem").read_text()
    )

    clear_mitmproxy_ssl_context_cache()


def clear_mitmproxy_ssl_context_cache():
    # Clear mitmproxy SSL context cache to ensure clean state
    with httpx.Client(base_url="http://localhost:9021", cookies={"_xsrf": "dummy"}) as client:
        client.post(
            "",
            data={
                "token": os.environ["MITM_PASSWORD"],
                "_xsrf": "dummy",
            },
        ).raise_for_status()
        client.post(
            "/commands/ssl.clear",
            headers={"X-XSRFToken": "dummy"},
            json={"arguments": []},
        ).raise_for_status()


@functions.append
def langchain_tool_call():
    """
    Use LangChain to call an LLM and get it to do a tool call.
    """

    @tool
    def add(a: int, b: int) -> int:
        """Adds two integers."""
        return a + b

    llm = ChatOpenAI()

    agent = initialize_agent(
        tools=[add],
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )

    agent.run("Please add 20 to the answer to life, the universe, and everything else.")


@functions.append
def openai_sdk_completions():
    """
    Use the OpenAI SDK to call the completions API.
    """
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "I'm a little teapot!"}],
    )

    print(response.choices[0].message.content)


@functions.append
def openai_sdk_responses():
    """
    Use the OpenAI SDK to call the responses API.
    """
    client = openai.OpenAI()
    response = client.responses.create(
        model="gpt-4o-mini",
        input="You're Alice, who just met the Mad Hatter, me. What do you say?",
    )

    print(response.output_text)


@functions.append
def kubernetes_list_pods():
    """
    Use LangChain to call an LLM and get it to do a tool call.
    """
    region = os.environ["AWS_REGION"]
    assert region, "AWS_REGION is not set"

    cluster_name = "uatx-cluster"

    eks_client = boto3.client("eks", region_name=region)

    cluster_info = eks_client.describe_cluster(name=cluster_name)
    cluster_endpoint = cluster_info["cluster"]["endpoint"]
    cluster_ca = cluster_info["cluster"]["certificateAuthority"]["data"]

    # Configure kubernetes client
    configuration = kubernetes.client.Configuration()
    configuration.host = cluster_endpoint
    configuration.verify_ssl = True
    configuration.proxy = os.getenv("HTTP_PROXY")  # Set proxy from environment variable

    # Append EKS cluster CA cert to certifi bundle for {region}/{cluster_name}
    ca_cert_data = (
        f"\n# EKS cluster CA certificate for {region}/{cluster_name}\n".encode()
        + base64.b64decode(cluster_ca)
    )
    if ca_cert_data not in Path(certifi.where()).read_bytes():
        with open(certifi.where(), "ab") as certifi_bundle:
            certifi_bundle.write(ca_cert_data)

    clear_mitmproxy_ssl_context_cache()

    # Get token for authentication
    token = get_token(cluster_name=cluster_name)["status"]["token"]
    configuration.api_key = {"authorization": f"Bearer {token}"}

    # Create API client
    api_client = kubernetes.client.ApiClient(configuration)
    v1 = kubernetes.client.CoreV1Api(api_client)

    result = v1.list_namespaced_pod(namespace="default")

    print("Pods:")
    for pod in result.items:
        print(pod.metadata.name)


def main():
    ensure_mitmproxy_ca_cert_to_certifi()

    for fn in functions:
        banner(f"Running {fn.__name__}", fn.__doc__)
        fn()


if __name__ == "__main__":
    main()
