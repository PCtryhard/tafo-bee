FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
# runtime deps only, everything below the dev marker is for tests
RUN sed '/# dev/,$d' requirements.txt > /tmp/req.txt && pip install --no-cache-dir -r /tmp/req.txt
COPY . .
RUN useradd -r bee && mkdir -p /data && chown bee /data
USER bee
ENV PORT=8000 DB_PATH=/data/bee.db
EXPOSE 8000
CMD gunicorn -b 0.0.0.0:$PORT --workers 1 app:app
