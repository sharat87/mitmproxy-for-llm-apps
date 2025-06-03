from flask import Flask, render_template, request
from openai import OpenAI
import os

from main import ensure_mitmproxy_ca_cert_to_certifi

app = Flask(__name__)
client = OpenAI()


@app.get('/')
def index_get():
    return render_template("index.html")


@app.post('/')
def index_post():
    content = request.form["content"]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": content},
            ],
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = f"Error: {str(e)}"

    return render_template("index.html", result=result, content=content)


if __name__ == "__main__":
    ensure_mitmproxy_ca_cert_to_certifi()
    app.run(debug=True, port=9022, host="0.0.0.0")
