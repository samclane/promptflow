FROM python:3.11-slim-buster

WORKDIR /worker

ENV HNSWLIB_NO_NATIVE=1


COPY requirements.txt /worker/requirements.txt
RUN apt-get update && apt-get install build-essential -y
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /worker

CMD ["celery", "-A", "promptflow.src.tasks", "worker", "-l", "info"]