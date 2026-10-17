#!/usr/bin/env bash
# One-time setup of the Thunderbot worker on a fresh Ubuntu 22.04/24.04 VPS (Mumbai, static IP).
#
#   curl -fsSL https://raw.githubusercontent.com/Thunderk3g/thunderbot/<branch>/worker/deploy/bootstrap.sh | sudo bash
#   (private repo: copy this file over with scp and run `sudo bash bootstrap.sh`)
#
# It installs the worker, systemd units and a locked-down env file, but does NOT start trading:
# fill in /etc/thunderbot.env first, then follow the "Next steps" it prints.
set -euo pipefail

BRANCH="${THUNDERBOT_BRANCH:-claude/groww-llm-trading-research-odqbtn}"
REPO="${THUNDERBOT_REPO:-https://github.com/Thunderk3g/thunderbot.git}"
APP=/opt/thunderbot
STATE=/var/lib/thunderbot
ENV_FILE=/etc/thunderbot.env

[ "$(id -u)" -eq 0 ] || { echo "Run as root (sudo)."; exit 1; }

echo "==> System packages and exchange timezone"
timedatectl set-timezone Asia/Kolkata || true
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3 python3-venv python3-pip git ufw curl >/dev/null

echo "==> Service user"
id thunderbot >/dev/null 2>&1 || useradd --system --home-dir "$STATE" --create-home --shell /usr/sbin/nologin thunderbot

echo "==> Code ($BRANCH)"
if [ -d "$APP/.git" ]; then
  git -C "$APP" fetch -q origin "$BRANCH" && git -C "$APP" checkout -q "$BRANCH" && git -C "$APP" pull -q --ff-only origin "$BRANCH"
else
  git clone -q --branch "$BRANCH" "$REPO" "$APP"
fi
python3 -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q --upgrade pip
"$APP/venv/bin/pip" install -q -e "$APP/worker[all]"
mkdir -p "$APP/worker/data" "$STATE"
chown -R thunderbot:thunderbot "$APP/worker/data" "$STATE"

echo "==> Environment file"
if [ ! -f "$ENV_FILE" ]; then
  install -m 640 -o root -g thunderbot "$APP/worker/.env.example" "$ENV_FILE"
  sed -i "s#^TB_HOLIDAYS_FILE=.*#TB_HOLIDAYS_FILE=$APP/worker/deploy/nse_holidays.txt#" "$ENV_FILE"
  echo "    created $ENV_FILE (fill it in)"
else
  echo "    kept existing $ENV_FILE"
fi

echo "==> systemd units (installed, not started)"
install -m 644 "$APP/worker/deploy/thunderbot.service" /etc/systemd/system/thunderbot.service
install -m 644 "$APP/worker/deploy/thunderbot-jobs.service" /etc/systemd/system/thunderbot-jobs.service
systemctl daemon-reload

echo "==> Firewall: SSH only (the worker makes outbound connections; nothing listens publicly)"
ufw allow OpenSSH >/dev/null
ufw --force enable >/dev/null

IP="$(curl -fsS --max-time 5 https://api.ipify.org || echo unknown)"
cat <<EOF

Done. This server's public IP is: $IP

Next steps
  1. On groww.in/trade-api/api-keys, whitelist $IP and create a TOTP key.
  2. sudo nano $ENV_FILE
       GROWW_API_KEY, GROWW_TOTP_SECRET, TB_EXPECTED_STATIC_IP=$IP,
       SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and NSE holidays in $APP/worker/deploy/nse_holidays.txt
  3. sudo -u thunderbot TB_ENV_FILE=$ENV_FILE $APP/venv/bin/thunderbot login-check
     sudo -u thunderbot TB_ENV_FILE=$ENV_FILE $APP/venv/bin/thunderbot check-ip
  4. sudo systemctl enable --now thunderbot thunderbot-jobs     # PAPER mode, waiting for Start
     journalctl -u thunderbot -f
  5. Press "Start paper trading" on the dashboard. Paper trades use live Groww prices; orders are simulated.
Live trading stays off until you set TB_LIVE_TRADING_ENABLED=true and change the unit to
'thunderbot live --i-understand-the-risks' (see docs/runbook.md, Stage 3).
EOF
