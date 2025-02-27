FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app

# Install project dependencies, in a separate layer
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-install-project

# Install the project itself
COPY . /app
RUN uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "yuri", "serve", "--host", "0.0.0.0", "--port", "8000"]
