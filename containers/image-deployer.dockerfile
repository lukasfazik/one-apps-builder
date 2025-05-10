FROM python:3-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN pip install --no-cache-dir pyone && \
    apt-get update && apt-get install -y --no-install-recommends \
    qemu-utils && \
    useradd -m -s /bin/bash user && \
    apt-get purge --auto-remove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/*

USER user

WORKDIR /home/user

CMD [ "bash" ]