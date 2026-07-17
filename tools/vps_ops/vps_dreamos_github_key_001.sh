#!/usr/bin/env bash
set -euo pipefail

VPS_HOST="${VPS_HOST:-2.25.64.233}"
VPS_USER="${VPS_USER:-dreamos}"

ssh "$VPS_USER@$VPS_HOST" 'bash -s' <<'REMOTE'
set -euo pipefail

echo "== DREAMOS VPS VERIFY =="
echo "USER=$(whoami)"
echo "HOST=$(hostname)"
echo "HOME=$HOME"
echo "PWD=$PWD"

test "$(whoami)" = "dreamos"
test -d /opt/dreamos
test -w /opt/dreamos

mkdir -p "$HOME/.ssh" /opt/dreamos/{repos,bin,reports}
chmod 700 "$HOME/.ssh"

KEY="$HOME/.ssh/id_ed25519_github_dreamos_vps"

echo
echo "== GITHUB SSH KEY =="
if [ ! -f "$KEY" ]; then
  ssh-keygen -t ed25519 -C "dreamos-vps-github" -f "$KEY" -N ""
  echo "CREATED=$KEY"
else
  echo "EXISTS=$KEY"
fi

chmod 600 "$KEY"
chmod 644 "$KEY.pub"

cat > "$HOME/.ssh/config" << SSHCONF
Host github.com
  HostName github.com
  User git
  IdentityFile $KEY
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
SSHCONF
chmod 600 "$HOME/.ssh/config"

cat > /opt/dreamos/bin/clone_private_repos_001.sh << 'CLONE'
#!/usr/bin/env bash
set -euo pipefail

cd /opt/dreamos
mkdir -p repos reports

REPORT="/opt/dreamos/reports/private_repo_clone_$(date +%Y%m%d_%H%M%S).txt"

{
  echo "== DREAMOS PRIVATE REPO CLONE =="
  echo "USER=$(whoami)"
  echo "HOST=$(hostname)"
  echo "PWD=$(pwd)"
  echo "DATE=$(date -Is)"
  echo

  echo "== SSH AUTH TEST =="
  set +e
  AUTH_OUT="$(ssh -T git@github.com 2>&1)"
  AUTH_CODE=$?
  set -e
  echo "$AUTH_OUT"
  echo "SSH_AUTH_EXIT=$AUTH_CODE"

  if ! echo "$AUTH_OUT" | grep -qi "successfully authenticated"; then
    echo
    echo "VERIFY=FAIL_GITHUB_SSH_AUTH"
    echo "NEXT=add the printed public key to GitHub SSH keys, then rerun this script"
    exit 1
  fi

  echo
  echo "VERIFY=PASS_GITHUB_SSH_AUTH"

  echo
  echo "== CLONE / UPDATE REPOS =="

  REPOS=(
    "Victor-Dixon/DreamOS"
    "Victor-Dixon/websites"
    "Victor-Dixon/dreamos-brain"
    "Victor-Dixon/AgentTools"
    "Victor-Dixon/projectscanner"
  )

  cd /opt/dreamos/repos

  for repo in "${REPOS[@]}"; do
    name="${repo##*/}"
    url="git@github.com:${repo}.git"

    echo
    echo "--- $repo ---"

    if [ -d "$name/.git" ]; then
      echo "ACTION=FETCH_EXISTING"
      git -C "$name" remote -v | head -n 2
      git -C "$name" fetch --all --prune
      git -C "$name" status -sb
    else
      echo "ACTION=CLONE_NEW"
      git clone "$url" "$name"
      git -C "$name" status -sb
    fi
  done

  echo
  echo "== FINAL VERIFY =="
  find /opt/dreamos/repos -maxdepth 2 -name .git -type d | sed 's#/.git$##' | sort

  echo
  echo "VERIFY=PASS_PRIVATE_REPO_CLONE_LANE"
} | tee "$REPORT"

echo
echo "REPORT=$REPORT"
CLONE

chmod +x /opt/dreamos/bin/clone_private_repos_001.sh

echo
echo "== ADD THIS PUBLIC KEY TO GITHUB =="
echo "GitHub  Settings  SSH and GPG keys  New SSH key"
echo "Title: dreamos-vps"
echo
cat "$KEY.pub"

echo
echo "== NEXT AFTER ADDING KEY =="
echo "ssh dreamos@2.25.64.233 '/opt/dreamos/bin/clone_private_repos_001.sh'"
REMOTE
