#!/usr/bin/env bash
set -euo pipefail

SECRETS_DIR="$HOME/secrets"
INTAKE_ENV="$SECRETS_DIR/signal-to-lead-intake.env"
DISCORD_ENV="$SECRETS_DIR/discord-fleet.env"

mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

touch "$INTAKE_ENV" "$DISCORD_ENV"
chmod 600 "$INTAKE_ENV" "$DISCORD_ENV"

cp "$INTAKE_ENV" "${INTAKE_ENV}.bak.$(date +%Y%m%d_%H%M%S)"
cp "$DISCORD_ENV" "${DISCORD_ENV}.bak.$(date +%Y%m%d_%H%M%S)"

OPERATOR_AUTH_SECRET="$(openssl rand -hex 32)"
OPERATOR_AUTH_TOKEN="$(openssl rand -hex 24)"

upsert_env() {
    local file="$1"
    local key="$2"
    local value="$3"
    local temp

    temp="$(mktemp)"

    awk -v key="$key" -v value="$value" '
        BEGIN { replaced = 0 }
        $0 ~ "^" key "=" {
            print key "=" value
            replaced = 1
            next
        }
        { print }
        END {
            if (!replaced) {
                print key "=" value
            }
        }
    ' "$file" > "$temp"

    mv "$temp" "$file"
    chmod 600 "$file"
}

upsert_env "$INTAKE_ENV" "OPERATOR_AUTH_SECRET" "$OPERATOR_AUTH_SECRET"
upsert_env "$INTAKE_ENV" "OPERATOR_AUTH_TOKEN" "$OPERATOR_AUTH_TOKEN"

echo
echo "INTAKE_SECRETS=GENERATED_AND_WRITTEN"
echo "FILE=$INTAKE_ENV"
echo
echo "Nano will open the intake file."
echo "Review it, then press Ctrl+O, Enter, Ctrl+X."
read -r -p "Press Enter to open Nano..."

nano "$INTAKE_ENV"

echo
echo "Nano will now open the Discord fleet file."
echo "Set these two lines:"
echo "DISCORD_BOT_TOKEN=<Commander token>"
echo "DREAMOSARCHITECT_BOT_TOKEN=<Architect token>"
echo
echo "Then press Ctrl+O, Enter, Ctrl+X."
read -r -p "Press Enter to open Nano..."

nano "$DISCORD_ENV"

check_key() {
    local file="$1"
    local key="$2"

    if grep -Eq "^${key}=.+" "$file"; then
        echo "${key}=SET"
    else
        echo "${key}=MISSING"
    fi
}

echo
echo "VERIFY"
echo "------"
check_key "$INTAKE_ENV" "OPERATOR_AUTH_SECRET"
check_key "$INTAKE_ENV" "OPERATOR_AUTH_TOKEN"
check_key "$DISCORD_ENV" "DISCORD_BOT_TOKEN"
check_key "$DISCORD_ENV" "DREAMOSARCHITECT_BOT_TOKEN"

echo
echo "STATUS=ENV_FILES_UPDATED"
echo "SECRETS_PRINTED=0"
