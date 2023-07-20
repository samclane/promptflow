FROM python:3.11-slim-buster

WORKDIR /app

ENV HNSWLIB_NO_NATIVE=1
ENV PYTHONPATH=/app/promptflow/src

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install build-essential -y
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .


CMD ["uvicorn", "promptflow.src.app:app", "--host", "0.0.0.0", "--port", "8000"]