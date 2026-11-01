FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS core
WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE THIRD_PARTY_NOTICES.md ./
COPY server.py web_app.py py.typed ./
COPY openhook ./openhook
COPY web ./web
RUN uv sync --frozen --no-dev && useradd --system --uid 10001 openhook && mkdir /data && chown openhook /data
ENV PYTHONUNBUFFERED=1 OPENHOOK_DATABASE=/data/openhook.sqlite3
EXPOSE 8788
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8788/health', timeout=3)"]
USER openhook
CMD ["/app/.venv/bin/openhook", "--http", "--host", "0.0.0.0", "--port", "8788"]
