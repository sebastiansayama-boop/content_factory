FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=10000
ENV FACTORY_DATA_DIR=/data

RUN useradd --create-home --uid 10001 factory \
    && mkdir -p /data \
    && chown -R factory:factory /app /data
USER factory

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10000/health', timeout=3).read()"

CMD ["python", "-m", "content_factory.product_http"]
