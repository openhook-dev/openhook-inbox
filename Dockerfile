FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base
WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE THIRD_PARTY_NOTICES.md ./
COPY server.py web_app.py py.typed ./
COPY openhook ./openhook
# Workspace metadata is needed for the shared lockfile, not hosted source.
COPY hosted/pyproject.toml hosted/README.md ./hosted/
COPY web ./web
RUN useradd --system --uid 10001 openhook && mkdir /data && chown openhook /data
ENV PYTHONUNBUFFERED=1 OPENHOOK_DATABASE=/data/openhook.sqlite3
EXPOSE 8788 2525 5353/tcp 5353/udp
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8788/health', timeout=3)"]

FROM base AS hosted
COPY hosted ./hosted
RUN uv sync --frozen --no-dev --package openhook-hosted
USER openhook
CMD ["/app/.venv/bin/openhook-hosted", "--host", "0.0.0.0", "--port", "8788"]

FROM base AS core
RUN uv sync --frozen --no-dev
USER openhook
CMD ["/app/.venv/bin/openhook", "--http", "--host", "0.0.0.0", "--port", "8788"]
