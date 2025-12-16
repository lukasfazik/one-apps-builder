# Copyright 2025 Lukáš Fázik
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get install -y --no-install-recommends curl ca-certificates gnupg lsb-release && \
    curl -fsSL https://apt.releases.hashicorp.com/gpg | \
    gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    make cloud-utils qemu-utils qemu-system-x86 ovmf \
    libguestfs-tools linux-image-amd64 packer && \
    apt-get purge --auto-remove -y lsb-release && \
    apt-get clean && \
    useradd -m -s /bin/bash user && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/*

USER user

WORKDIR /home/user
