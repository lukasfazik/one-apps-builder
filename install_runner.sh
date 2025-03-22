#!/bin/sh

READY_FILE="/root/.runner_ready"

if [ ! -f "$READY_FILE" ]; then
    # Update the system and install dependencies
    sudo apt-get update
    sudo apt full-upgrade -y
    sudo apt install ca-certificates curl -y
    # Add Gitlab repo
    curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
    # Add Docker's official GPG key:
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    # Add the Docker repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    # Remove non official packages
    for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get purge $pkg -y; done
    # Install docker and gitlab runner
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin gitlab-runner -y
    # Register the runner
    gitlab-runner register --non-interactive --executor "docker" --docker-image alpine:latest
    gitlab-runner install
    # Touch ready file
    sudo touch "$READY_FILE"
    # Reboot in one minute
    sudo shutdown -r +1
fi