FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN <<EOF
chmod +x /app/*.sh

pip install uv
cd /app
uv sync --no-cache
EOF

EXPOSE 9021 9022

CMD ["/app/entrypoint.sh"]
