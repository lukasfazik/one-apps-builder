FROM debian:stable-slim

# Update system and install dependencies
RUN apt-get update && apt-get full-upgrade -y && apt-get install -y make ruby rpm binutils wixl genisoimage xz-utils && gem install --no-document fpm