#!/bin/sh

READY_FILE="/root/.runner_ready"
CI_USER="gitlab-runner"

if [ ! -f "$READY_FILE" ]; then
    # Touch ready file
    sudo -i touch "$READY_FILE"
    # Update the system and install dependencies
    sudo apt-get update
    sudo apt full-upgrade -y
    # Install container engine
    if [ "$CONTAINER_ENGINE" = "docker" ];then
        # Install dependencies
        sudo apt install ca-certificates curl -y
        # Add Docker's official GPG key:
        sudo install -m 0755 -d /etc/apt/keyrings
        sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc
        # Add the Docker repository to Apt sources
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        # Install docker
        sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
        # Disable the rootful mode
        sudo systemctl disable --now docker.service docker.socket
        sudo rm /var/run/docker.sock
    else
        # Install podman
        sudo apt-get update && sudo apt-get install podman podman-compose -y
    fi
    # Add Gitlab repo
    curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | bash
    # Install gitlab runner
    sudo apt-get update && sudo apt-get install gitlab-runner -y
    # Stop and remove the default service
    sudo gitlab-runner stop
    sudo gitlab-runner uninstall
    # Set /dev/kvm permissions via udev rule (applies after reboot)
    sudo echo 'KERNEL=="kvm", MODE="0666"' > /etc/udev/rules.d/99-kvm.rules
    # Prepare the user
    sudo apt-get install -y uidmap
    sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$CI_USER"
    sudo loginctl enable-linger "$CI_USER"
    if [ "$CONTAINER_ENGINE" = "docker" ];then
        # Enable the rootless Docker mode
        sudo -i -u gitlab-runner dockerd-rootless-setuptool.sh install
        export DOCKER_HOST="unix:///run/user/$(id -u $CI_USER)/docker.sock"
    else
        # Enable the rootless Podman mode
        sudo systemctl -M "$CI_USER@" --user enable --now podman.socket
        export DOCKER_HOST="unix:///run/user/$(id -u $CI_USER)/podman/podman.sock"
    fi
    # Configure the runner
    sudo -i -u "$CI_USER" DOCKER_HOST="$DOCKER_HOST" CI_SERVER_TOKEN="$CI_SERVER_TOKEN" CI_SERVER_URL="$CI_SERVER_URL" \
            gitlab-runner register --non-interactive --executor "docker" --docker-image alpine:latest --docker-devices "/dev/kvm"  --env "VM_ID=$VM_ID" --docker-volumes "runner-cache:/cache"
    sudo gitlab-runner install --working-directory "/home/$CI_USER" --config "/home/$CI_USER/.gitlab-runner/config.toml" --init-user "$CI_USER"
    # Reset the runner token because original token is visible in the VM configuration
    sudo -i -u "$CI_USER" gitlab-runner reset-token --all-runners
    # restart the server in one minute
    sudo shutdown -r +1
fi