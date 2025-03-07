FROM python:3.10-slim


WORKDIR /app
RUN apt-get update && apt-get install -y curl wget

COPY . .

COPY requirements.txt /app
RUN mkdir -p /app/data
VOLUME /app/data

RUN if [ -f "/app/prime.db" ]; then mv /app/prime.db /app/data/; fi

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "main.py"]