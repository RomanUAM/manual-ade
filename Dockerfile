FROM python:3.13-slim

WORKDIR /app

COPY hag ./hag
COPY scripts ./scripts
COPY config ./config
COPY tests ./tests
COPY docs ./docs
COPY practicas ./practicas
COPY site ./site

ENV PYTHONPATH=/app

CMD ["python", "scripts/hag.py", "audit"]
