FROM python:3-slim

RUN pip install --no-cache-dir pyone

RUN apt-get update && apt-get install qemu-utils -y

CMD [ "bash" ]