#!/bin/bash
# Docker setup script for Ubuntu 22.04 (AWS EC2)
set -euo pipefail

# Configuration
DOCKER_COMPOSE_VERSION="v2.23.0"
LOG_FILE="/var/log/docker-setup.log"

# Initialize logging
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== Starting Docker Setup $(date) ==="

# Update system
echo "Updating package index..."
sudo apt-get update -y

# Install prerequisites
echo "Installing required packages..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https

# Add Docker's official GPG key
echo "Adding Docker GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
echo "Installing Docker..."
sudo apt-get update -y
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin

# Install Docker Compose
echo "Installing Docker Compose v2..."
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Configure Docker
echo "Configuring Docker..."
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

# Add user to docker group
echo "Adding $USER user to docker group..."
sudo usermod -aG docker $USER

# Start and enable services
echo "Starting Docker..."
sudo systemctl enable docker
sudo systemctl restart docker

# Verification
echo "Verifying installation..."
docker --version
docker-compose --version

echo "=== Setup completed successfully ==="
echo "You may need to logout and login again for group changes to take effect"
echo "Test with: docker run hello-world"