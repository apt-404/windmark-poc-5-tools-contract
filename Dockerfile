FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nmap gobuster iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv --no-cache-dir

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV WORDLIST_PATH=/usr/share/wordlists/dirb/common.txt
ENV MCP_SERVER_TIMEOUT=10
