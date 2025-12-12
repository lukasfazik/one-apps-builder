#!/bin/sh

READY_FILE="/root/.runner_ready"
CI_USER="gitlab-runner"

if [ ! -f "$READY_FILE" ]; then
    # Touch ready file
    sudo -i touch "$READY_FILE"
    # Update the system and install dependencies
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get full-upgrade -y
    # Install and configure unattended-upgrades
    sudo DEBIAN_FRONTEND=noninteractive apt-get install unattended-upgrades -y
    sudo tee /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
    sudo tee /etc/apt/apt.conf.d/52unattended-upgrades-local <<EOF
Unattended-Upgrade::Origins-Pattern {
        "origin=Debian,codename=${distro_codename},label=Debian";
        "origin=Debian,codename=${distro_codename},label=Debian-Security";
        "origin=Debian,codename=${distro_codename}-security,label=Debian-Security";
        "origin=packages.gitlab.com/runner/gitlab-runner,label=gitlab-runner";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-WithUsers "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:00";
EOF
    sudo systemctl restart unattended-upgrades
    # Install container engine
    if [ "$CONTAINER_ENGINE" = "docker" ];then
        # Install dependencies
        sudo DEBIAN_FRONTEND=noninteractive apt-get install ca-certificates curl -y
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
        sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
        # Disable the rootful mode
        sudo systemctl disable --now docker.service docker.socket
        sudo rm /var/run/docker.sock
    else
        # Install podman
        sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install podman podman-compose -y
    fi
    # Add Gitlab repo
    curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | bash
    # Install gitlab runner
    sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install gitlab-runner -y
    # Stop and remove the default service
    sudo gitlab-runner stop
    sudo gitlab-runner uninstall
    sudo systemctl mask gitlab-runner
    # Set /dev/kvm permissions via udev rule (applies after reboot)
    echo 'KERNEL=="kvm", MODE="0666"' | sudo tee /etc/udev/rules.d/999-gitlab-runner.rules
    # Set disk permissions via udev rule (applies after reboot)
    echo 'SUBSYSTEM=="block", KERNEL=="sd[b-z]*", GROUP="gitlab-runner", MODE="0660"' | sudo tee -a /etc/udev/rules.d/999-gitlab-runner.rules
    echo 'SUBSYSTEM=="block", KERNEL=="sd[a-z][a-z]*", GROUP="gitlab-runner", MODE="0660"' | sudo tee -a /etc/udev/rules.d/999-gitlab-runner.rules
    # Prepare the user
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y uidmap
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
    # Create the runner data direcotry
    sudo -i -u "$CI_USER" mkdir -p '$HOME/runner-data'
    sudo -i -u "$CI_USER" chmod 1777 '$HOME'/runner-data
    sudo -i -u "$CI_USER" mkdir -p '$HOME/runner-cache'
    # Configure the runner
    sudo -i -u "$CI_USER" DOCKER_HOST="$DOCKER_HOST" CI_SERVER_TOKEN="$CI_SERVER_TOKEN" CI_SERVER_URL="$CI_SERVER_URL" \
            gitlab-runner register --non-interactive --executor "docker" --docker-image alpine:latest --docker-devices "/dev/kvm"  --env "VM_ID=$VM_ID" --docker-volumes "/dev/:/host_dev/" --docker-volumes '$HOME/runner-cache:/cache' --docker-volumes '$HOME/runner-data:/mnt/data'
    sudo gitlab-runner install --service gitlab-runner-custom --working-directory "/home/$CI_USER" --config "/home/$CI_USER/.gitlab-runner/config.toml" --init-user "$CI_USER"
    # Reset the runner token because original token is visible in the VM configuration
    sudo -i -u "$CI_USER" gitlab-runner reset-token --all-runners
    # Set the number of concurrent jobs
    if [ -n "$CONCURRENT_JOBS" ]; then
        sudo -i -u "$CI_USER" sed -i "s/^concurrent = [0-9]*$/concurrent = $CONCURRENT_JOBS/" '$HOME/.gitlab-runner/config.toml'
    fi
    # restart the server in one minute
    sudo shutdown -r +1
fi