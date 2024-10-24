FROM python:3.10
ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd postgresql-client && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env .

COPY wait-for-it.sh /app/wait-for-it.sh
COPY init_db.sh /app/init_db.sh
RUN chmod +x /app/wait-for-it.sh /app/init_db.sh

CMD ["/app/init_db.sh"]
