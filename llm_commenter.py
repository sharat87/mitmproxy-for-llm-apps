import mitmproxy

def response(flow):
    if flow.request.pretty_url == "https://api.openai.com/v1/chat/completions":
        body = flow.request.json()
        lines = []

        for msg in body["messages"]:
            lines.append(f"{msg['role'].title()}: {msg['content']}")

        try:
            lines.append("Assistant: " + flow.response.json()["choices"][0]["message"]["content"])
        except Exception as e:
            lines.append("Assistant: " + str(e))

        flow.comment = "\n".join(lines)
