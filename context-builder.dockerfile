FROM debian:stable-slim

RUN apt-get update && apt-get full-upgrade -y && apt-get install -y make ruby rpm binutils wixl genisoimage xz-utils && gem install --no-document fpm

RUN useradd -m -s /bin/bash user

USER user

WORKDIR /home/user
