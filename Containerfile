FROM ubuntu:22.04
# Update system
RUN apt-get update && apt-get full-upgrade -y
# Install dependencies
RUN apt-get update && apt-get install -y \
    gnupg curl git make ruby wixl msitools \
    dpkg rpm genisoimage cloud-utils qemu-utils \
    qemu-system guestfs-tools lsb-release && \
    gem install fpm
# Install packer
RUN curl -s https://apt.releases.hashicorp.com/gpg | \
    gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y packer
# Install Opennebula tools
RUN curl -s https://downloads.opennebula.io/repo/repo2.key | \
    gpg --dearmor --yes --output /etc/apt/keyrings/opennebula.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/opennebula.gpg] https://downloads.opennebula.io/repo/6.10/$(lsb_release -is)/$(lsb_release -rs) stable opennebula" > /etc/apt/sources.list.d/opennebula.list && \
    apt-get update && apt-get install -y opennebula-tools