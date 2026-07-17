#!/usr/bin/env bash
set -euo pipefail

VPS_HOST="${VPS_HOST:-2.25.64.233}"

ssh root@"$VPS_HOST" 'bash -s' <<'REMOTE'
set -euo pipefail

echo "== VERIFY ROOT =="
whoami
hostname

echo
echo "== FIND DREAMOS HOME =="
DREAMOS_HOME="$(getent passwd dreamos | cut -d: -f6)"
if [ -z "$DREAMOS_HOME" ]; then
  echo "FAIL: dreamos user not found"
  exit 1
fi
echo "DREAMOS_HOME=$DREAMOS_HOME"

echo
echo "== INSTALL AUTHORIZED_KEYS =="
install -d -m 700 -o dreamos -g dreamos "$DREAMOS_HOME/.ssh"

if [ ! -f /root/.ssh/authorized_keys ]; then
  echo "FAIL: /root/.ssh/authorized_keys missing"
  exit 1
fi

cat /root/.ssh/authorized_keys > "$DREAMOS_HOME/.ssh/authorized_keys"
chown dreamos:dreamos "$DREAMOS_HOME/.ssh/authorized_keys"
chmod 600 "$DREAMOS_HOME/.ssh/authorized_keys"

echo
echo "== VERIFY OWNERSHIP =="
ls -ld "$DREAMOS_HOME/.ssh"
ls -l "$DREAMOS_HOME/.ssh/authorized_keys"
ls -ld /opt/dreamos

echo
echo "VERIFY=PASS_DREAMOS_AUTHORIZED_KEYS_INSTALLED"
REMOTE

echo
echo "Now test:"
echo "ssh dreamos@$VPS_HOST"
