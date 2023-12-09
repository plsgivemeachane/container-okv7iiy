FROM python:3.10.13-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Flask app so need expose 8080
EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
