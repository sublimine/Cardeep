#!/usr/bin/env bash
# Cardeep VM bootstrap — PHASE 1 of 2. Oracle Ampere A1, Ubuntu 24.04 aarch64.
# Run as: ssh -i cardeep_vm_key ubuntu@<PUBLIC_IP> 'bash -s' < vm_bootstrap_phase1.sh
#
# Does everything that does NOT need the "ubuntu" user's new `docker` group
# membership to actually take effect, then REBOOTS. This is deliberate, not
# an oversight: `sudo usermod -aG docker "$USER"` only updates /etc/group — the
# running login session's process tree (including systemd's PER-USER manager,
# which Phase 2's `openship up` runs under and which is what actually talks to
# the Docker socket to deploy Cardeep's containers) does NOT pick up a new
# supplementary group without a FRESH login. On Ubuntu 24.04's default
# pam_systemd setup that user-manager is created at first SSH login and stays
# alive across reconnects — a plain "open a new SSH session" is NOT guaranteed
# to be fresh enough. A full reboot is the simplest reliable way to guarantee
# Phase 2 starts under a manager that sees the group correctly (verified
# 2026-07-25 against the actual installed Openship CLI bundle: openship up's
# Compose-mode control plane and its Docker-backed deploy engine both run
# under that per-user systemd manager, not root, when invoked as "ubuntu").
set -euo pipefail

echo "=== 1. System update ==="
sudo apt-get update -y
sudo apt-get upgrade -y

echo "=== 2. Docker (official repo, ARM64) — installed BEFORE ufw so ufw-docker has something to patch ==="
sudo apt-get install -y ca-certificates curl gnupg openssl
sudo install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
fi
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"

echo "=== 3. Host firewall (ufw + ufw-docker) — defense in depth alongside the OCI Security List ==="
sudo apt-get install -y ufw fail2ban
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo curl -fsSL https://github.com/chaifeng/ufw-docker/raw/master/ufw-docker -o /usr/local/bin/ufw-docker
sudo chmod +x /usr/local/bin/ufw-docker
sudo ufw-docker install
sudo ufw --force enable
sudo systemctl restart ufw
sudo systemctl enable fail2ban --now

echo "=== 4. Unattended security upgrades (idempotent) ==="
sudo apt-get install -y unattended-upgrades
grep -qxF 'Unattended-Upgrade::Automatic-Reboot "false";' /etc/apt/apt.conf.d/50unattended-upgrades 2>/dev/null || \
  echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades >/dev/null
sudo tee /etc/apt/apt.conf.d/20auto-upgrades >/dev/null <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
sudo systemctl enable unattended-upgrades --now

echo "=== 5. Swap (Ampere A1 free tier has 12GB RAM — cheap insurance under memory pressure) ==="
if ! sudo swapon --show=NAME --noheadings | grep -qx /swapfile; then
  if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
  fi
  sudo swapon /swapfile
  grep -qxF '/swapfile none swap sw 0 0' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

echo "=== 6. SSH hardening: disable password auth — the REAL winning file on Ubuntu 24.04 ==="
# Doesn't depend on the docker group, safe to do in phase 1. Ubuntu 24.04's cloud-init
# ships /etc/ssh/sshd_config.d/50-cloud-init.conf with "PasswordAuthentication yes",
# which wins over any later edit to the main sshd_config (Canonical: Launchpad #2088207,
# closed "not planned"). Fix: write the drop-in directly, verify EFFECTIVE config.
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
printf 'PasswordAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/50-cloud-init.conf >/dev/null
sudo systemctl restart ssh
if ! sudo sshd -T | grep -qi '^passwordauthentication no$'; then
  echo "ERROR: password authentication SIGUE activo tras el hardening — abortando." >&2
  exit 1
fi
echo "Verificado: password authentication realmente desactivado (sshd -T)."

echo ""
echo "=== FASE 1 COMPLETA — reiniciando para que el grupo 'docker' aplique a un ==="
echo "=== manager systemd-user COMPLETAMENTE NUEVO antes de la Fase 2.        ==="
echo "Espera ~30-60s tras esto y reconecta por SSH para lanzar vm_bootstrap_phase2.sh."
sudo reboot
