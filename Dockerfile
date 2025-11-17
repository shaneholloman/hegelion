FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HEGELION_CACHE=/data/cache \
    HEGELION_CACHE_DIR=/data/cache

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip \
    && pip install . \
    && mkdir -p /data/cache

ENTRYPOINT ["hegelion"]
CMD ["--help"]
