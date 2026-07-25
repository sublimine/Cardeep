#!/usr/bin/env bash
# Cardeep VM bootstrap — PHASE 2 of 2. Run AFTER vm_bootstrap_phase1.sh has rebooted
# the VM and you've reconnected with a FRESH SSH session (the reboot is what makes
# the `docker` group membership from Phase 1 actually apply — see phase1's own
# comment for why a plain reconnect isn't reliably enough on Ubuntu 24.04).
#
# Run as: ssh -i cardeep_vm_key ubuntu@<PUBLIC_IP> 'bash -s' -- <domain> <acme-email> \
#         <admin-name> <admin-email> <admin-password> < vm_bootstrap_phase2.sh
set -euo pipefail

PUBLIC_DOMAIN="${1:?uso: vm_bootstrap_phase2.sh <dominio> <acme-email> <admin-name> <admin-email> <admin-password>}"
ACME_EMAIL="${2:?falta acme-email}"
ADMIN_NAME="${3:?falta admin-name}"
ADMIN_EMAIL="${4:?falta admin-email}"
ADMIN_PASSWORD="${5:?falta admin-password}"

echo "=== 0. Confirmar que el grupo docker aplico de verdad tras el reboot ==="
if ! id -nG "$USER" | grep -qw docker; then
  echo "ERROR: '$USER' no esta en el grupo 'docker' todavia. Reconecta por SSH" >&2
  echo "       (nueva sesion) o revisa que la Fase 1 completo el usermod." >&2
  exit 1
fi
docker ps >/dev/null || { echo "ERROR: docker ps fallo pese a estar en el grupo — revisar dockerd." >&2; exit 1; }
echo "OK: '$USER' pertenece a 'docker' y el daemon responde."

echo "=== 1. Node.js 22 (for a reliable, non-bun, non-shell-script Openship CLI install) ==="
if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

echo "=== 2. Openship CLI via npm (get.openship.io's bun-based shell installer has reported ==="
echo "===    breakages as of Jul 2026 + a PATH-propagation footgun in non-interactive shells) ==="
sudo npm install -g openship
command -v openship >/dev/null 2>&1 || { echo "ERROR: openship no quedo en PATH tras npm install -g" >&2; exit 1; }
openship --version

echo "=== 3. Start Openship (Compose mode auto-selected: Linux+Docker) with managed TLS edge ==="
# --managed-edge installs OpenResty + Let's Encrypt for $PUBLIC_DOMAIN automatically.
# Persistent background service (systemd --user, boots + auto-restarts) — this is the
# documented "for CI / headless boxes, skip the wizard" path.
openship up --public-url "https://${PUBLIC_DOMAIN}" --managed-edge --acme-email "${ACME_EMAIL}"

echo "=== 4. Wait for the API, then bootstrap the first admin (non-interactive) ==="
# Same one-shot POST /api/system/bootstrap-admin the interactive `openship` wizard makes
# itself, authenticated with the same locally-generated INTERNAL_TOKEN (~/.openship/internal-token).
API_UP=false
for i in $(seq 1 30); do
  if curl -sf http://localhost:4000/api/health >/dev/null 2>&1; then
    API_UP=true
    break
  fi
  echo "  esperando a la API (intento $i/30)..."
  sleep 5
done
if [ "$API_UP" != true ]; then
  echo "ERROR: la API de Openship no respondio tras 150s. Revisar: journalctl --user -u openship" >&2
  exit 1
fi

INTERNAL_TOKEN="$(cat "$HOME/.openship/internal-token")"
BOOTSTRAP_RESPONSE="$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:4000/api/system/bootstrap-admin \
  -H "X-Internal-Token: ${INTERNAL_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${ADMIN_NAME}\",\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}" || echo "000")"
case "$BOOTSTRAP_RESPONSE" in
  200) echo "Admin creado: ${ADMIN_EMAIL}" ;;
  409) echo "Ya existia un admin (re-ejecucion idempotente del script) — sin cambios." ;;
  000) echo "ERROR: no se pudo conectar a la API para bootstrap-admin (curl fallo)." >&2; exit 1 ;;
  *) echo "ERROR: bootstrap-admin devolvio HTTP ${BOOTSTRAP_RESPONSE}" >&2; exit 1 ;;
esac

echo ""
echo "=== BOOTSTRAP COMPLETO ==="
echo "Docker version: $(docker --version)"
echo "Openship version: $(openship --version)"
openship status || true
echo ""
echo "Dashboard: https://${PUBLIC_DOMAIN}  (login: ${ADMIN_EMAIL})"
echo ""
echo "PENDIENTE DE VERIFICAR DESDE FUERA (no basta con confiar en localhost):"
echo "  curl -m10 -o /dev/null -w '%{http_code}\n' https://${PUBLIC_DOMAIN}"
echo "  Si ufw se comporta de forma inconsistente en esta imagen de OCI (reportado en la"
echo "  comunidad para Oracle Cloud), el plan B documentado es firewalld: 'sudo apt remove"
echo "  ufw && sudo apt install firewalld' — la Security List de la VCN sigue siendo la"
echo "  capa autoritativa en cualquier caso."
echo ""
echo "SIGUIENTE PASO OBLIGATORIO antes de 'openship init'/'openship deploy':"
echo "  fijar los secretos reales de Cardeep vía 'openship service env set' — ver"
echo "  docs/runbook/DEPLOY_OPENSHIP.md §2. NO desplegar con los placeholders del repo."
