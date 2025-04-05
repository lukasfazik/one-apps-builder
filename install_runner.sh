#!/bin/sh

READY_FILE="/root/.runner_ready"
CI_USER="gitlab-runner"

if [ ! -f "$READY_FILE" ]; then
    # Touch ready file
    sudo -i touch "$READY_FILE"
    # Update the system and install dependencies
    apt-get update
    apt full-upgrade -y
    apt install ca-certificates curl -y
    # Add Gitlab repo
    curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | bash
    # Install gitlab runner
    apt-get update && apt-get install gitlab-runner -y
    # Remove the default service
    gitlab-runner stop
    gitlab-runner uninstall
    # Install container engine
    if [ "$CONTAINER_ENGINE" = "docker" ];then
        # Add Docker's official GPG key:
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
        chmod a+r /etc/apt/keyrings/docker.asc
        # Add the Docker repository to Apt sources
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null
        # Remove non official docker packages
        for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do apt-get purge $pkg -y; done
        # Install docker
        apt-get update && apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
        # Register the runner
        gitlab-runner register --non-interactive --executor docker --docker-image alpine:latest --docker-devices "/dev/kvm"
        gitlab-runner install --user "$CI_USER"
        gitlab-runner start
    else
        # Install podman
        apt-get update && apt-get install podman podman-compose -y
        # Register the rootless runner
        usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$CI_USER"
        loginctl enable-linger "$CI_USER"
        systemctl -M "$CI_USER@" --user enable --now podman.socket
        sudo -i -u "$CI_USER" CI_SERVER_TOKEN="$CI_SERVER_TOKEN" CI_SERVER_URL="$CI_SERVER_URL" \
            gitlab-runner register --non-interactive --executor "docker" --docker-image alpine:latest --docker-devices "/dev/kvm" --docker-host "unix:///run/user/$(id -u $CI_USER)/podman/podman.sock"
        gitlab-runner install --working-directory "/home/$CI_USER" --config "/home/$CI_USER/.gitlab-runner/config.toml" --init-user "$CI_USER"
        gitlab-runner start
    fi
fi