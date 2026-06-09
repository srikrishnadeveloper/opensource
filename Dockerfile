# Wiki Brain — production image for Render (and any Docker host)
# LEARN: This copies server code + demo wiki into a container and runs HTTP mode.

FROM python:3.12-slim

WORKDIR /app

COPY mcp-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp-server/*.py .
COPY wiki/ ./wiki/

ENV WIKI_BRAIN_DIR=/app/wiki
ENV MCP_TRANSPORT=streamable-http
ENV PORT=8000

EXPOSE 8000

CMD ["python", "server.py"]
