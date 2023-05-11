#!/usr/bin/env bash

sudo sed -i "s/127.0.0.1 /127.0.0.1 $HOSTNAME /" /etc/hosts
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
 curl \
 docker.io \
 git

cat << EOF | sudo tee /etc/rc.local
#!/bin/sh -e
iptables -I DOCKER-USER -j ACCEPT
EOF
sudo chmod +x /etc/rc.local

sudo usermod -aG docker ${USER}

# sudo snap install code --classic
sudo snap install charmcraft --classic
sudo snap install jq openstackclients yq
