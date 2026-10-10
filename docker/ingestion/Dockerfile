# 1. Base image: Linux + Python 3.12
FROM python:3.12-slim

# 2. Bring in the uv binary from its official image (pinned version)
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/

# 3. Settings
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# 4. Install dependencies ONLY (cached until pyproject.toml or uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# 5. Copy our code and install our package on top
COPY src/ ./src/
RUN uv sync --locked

# 6. Use the project's virtual environment by default
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "nyc_mobility.ingestion.main"]