FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get full-upgrade -y && apt-get install -y --no-install-recommends \
make ruby rpm binutils wixl genisoimage xz-utils && \
gem install --no-document fpm && \
apt-get purge -y --auto-remove && \
apt-get clean && \
useradd -m -s /bin/bash user && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/*

USER user

WORKDIR /home/user
