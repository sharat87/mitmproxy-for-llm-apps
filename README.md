# Use mitmproxy when working with LLM APIs

This repo is code from [the article on this topic](https://sharats.me/posts/use-proxy-for-llm-app-dev/).

1. Give a password to `mitmproxy`'s web UI. Run `export MITM_PASSWORD=carpets-on-swimming-pools`.

2. Start `mitmproxy`'s web UI with `make mitm`. Let it run and open a new Terminal session.

3. There's an example LLM application in `main.py`, that uses a whole bunch of LLM APIs. Run it with `make main`.


To build and run as a Docker continer:

```bash
docker build -t mapp . && {
    docker rm -f mapp
    docker run --name mapp -d -p 5021:9021 -p 5022:9022 -e MITM_PASSWORD= -e OPENAI_API_KEY= mapp
}
```
