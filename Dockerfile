FROM python:3.13-alpine@sha256:18159b2be11db91f84b8f8f655cd860f805dbd9e49a583ddaac8ab39bf4fe1a7
COPY --from=ghcr.io/astral-sh/uv:0.5.18 /uv /uvx /bin/

ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml uv.lock ./
RUN uv pip install -r pyproject.toml

COPY . /app

ENTRYPOINT ["sh", "/app/scripts/entrypoint.sh"]

WORKDIR /app/src

CMD [ "python3 run.py web" ]