FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get install -y --no-install-recommends curl ca-certificates gnupg lsb-release && \
    curl -fsSL https://apt.releases.hashicorp.com/gpg | \
    gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    make qemu-utils qemu-system-x86 ovmf packer && \
    apt-get purge --auto-remove -y lsb-release curl gnupg && \
    apt-get clean && \
    useradd -m -s /bin/bash user && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/*

USER user

WORKDIR /home/user
