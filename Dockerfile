FROM python:3.11-slim

LABEL maintainer="GhostRoute Contributors"
LABEL version="2.0.0"
LABEL description="GhostRoute Pro - Endpoint Resurrection Scanner"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ghostroute.py .

ENTRYPOINT ["python", "ghostroute.py"]
CMD ["--help"]