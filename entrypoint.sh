#!/bin/bash

set -ue

test -n "$MITM_PASSWORD" || {
    echo MITM_PASSWORD is not set. Exiting.
    exit 1
}

uv run \
	mitmweb \
	--listen-port 9020 \
	--web-host 0.0.0.0 \
	--web-port 9021 \
	--set web_password="$MITM_PASSWORD" \
	--script llm_commenter.py \
	--script mitmproxy_ssl_clear.py \
	&

export HTTP_PROXY=http://localhost:9020
export HTTPS_PROXY=http://localhost:9020

export PORT=8080
exec uv run python server.py
