#!/bin/bash
# Docker setup script for Ubuntu 22.04 (AWS EC2)

# Convert line endings to LF and remove control characters
# This should be done as early as possible to avoid issues with CRLF

sed -i 's/\r$//' "$0"

set -euo pipefail

# Configuration
DOCKER_COMPOSE_VERSION="v2.23.0"
LOG_FILE="/var/log/docker-setup.log"


# Initialize logging
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== Starting Docker Setup $(date) ==="

# System updates
echo "Updating packages..."
sudo apt-get update -y

# Install prerequisites
echo "Installing dependencies..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https

# Docker repository setup
echo "Configuring Docker repository..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) \
    signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker components
echo "Installing Docker Engine..."
sudo apt-get update -y
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Docker configuration
echo "Configuring Docker daemon..."
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF

# User permissions
echo "Configuring user permissions..."
sudo usermod -aG docker "$USER"

# Service management
echo "Starting Docker service..."
sudo systemctl enable docker
sudo systemctl restart docker

# Verification
echo "Verifying installations:"
docker --version || { echo "Docker verification failed"; exit 1; }
docker-compose --version || { echo "Docker Compose verification failed"; exit 1; }

echo "=== Setup completed successfully ==="
echo "Note: You may need to reconnect for group changes to take effect"
echo "Test with: docker run --rm hello-world"