FROM python:3.11-slim-buster

ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1:$LD_PRELOAD
ENV LD_PRELOAD=/usr/local/lib/python3.11/site-packages/torch/lib/../../torch.libs/libgomp-d22c30c5.so.1.0.0:$LD_PRELOAD

WORKDIR /

ENV HNSWLIB_NO_NATIVE=1

COPY . .

RUN apt-get update && apt-get install build-essential -y
RUN pip3 install --upgrade pip
RUN pip3 install -r promptflow/requirements-no-nvidia.txt


# CMD ["celery", "-A", "promptflow.src.tasks", "worker", "-l", "info"]
# CMD ["uvicorn", "promptflow.src.app:app", "--host", "0.0.0.0", "--port", "8000"]
