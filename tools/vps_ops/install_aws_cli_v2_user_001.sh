#!/usr/bin/env bash
set -euo pipefail

echo "TARGET=INSTALL_AWS_CLI_V2_USER_LOCAL"

ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64)
    AWS_ARCH="x86_64"
    ;;
  aarch64|arm64)
    AWS_ARCH="aarch64"
    ;;
  *)
    echo "VERIFY=FAIL_UNSUPPORTED_ARCH arch=$ARCH"
    exit 2
    ;;
esac

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

mkdir -p "$HOME/.local/bin"

echo
echo "== DOWNLOAD AWS CLI V2 =="
cd "$WORKDIR"
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o awscliv2.zip

echo
echo "== EXTRACT =="
if command -v unzip >/dev/null 2>&1; then
  unzip -q awscliv2.zip
else
  python3 - << 'PY'
import zipfile
with zipfile.ZipFile("awscliv2.zip") as z:
    z.extractall(".")
PY
fi

echo
echo "== INSTALL USER-LOCAL =="
rm -rf "$HOME/.local/aws-cli" "$HOME/.local/bin/aws" "$HOME/.local/bin/aws_completer"
./aws/install -i "$HOME/.local/aws-cli" -b "$HOME/.local/bin"

echo
echo "== PATH SETUP =="
if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

export PATH="$HOME/.local/bin:$PATH"
hash -r

echo
echo "== AWS VERSION =="
aws --version

echo
echo "VERIFY=PASS_AWS_CLI_V2_USER_READY"
