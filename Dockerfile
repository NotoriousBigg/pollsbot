FROM python:3.10-slim


WORKDIR /app
RUN apt-get update && apt-get install -y curl wget

COPY . .

COPY requirements.txt /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "main.py"]