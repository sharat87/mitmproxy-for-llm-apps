main: deps
	HTTP_PROXY=http://localhost:9020 \
		HTTPS_PROXY=http://localhost:9020 \
		uv run python main.py

mitm:
	test -n "$$MITM_PASSWORD" || (echo "MITM_PASSWORD is not set" && exit 1)
	uv run \
		mitmweb \
		--listen-port 9020 \
		--web-port 9021 \
		--set web_password=$$MITM_PASSWORD \
		--script llm_commenter.py \
		--script mitmproxy_ssl_clear.py

serve: deps
	HTTP_PROXY=http://localhost:9020 \
		HTTPS_PROXY=http://localhost:9020 \
		uv run python server.py

deps:
	uv sync
	@test -n "$$OPENAI_API_KEY" || (echo "OPENAI_API_KEY is not set" && exit 1)

.PHONY: deps main mitm serve
