#!/usr/bin/env bash
set -euo pipefail
umask 077

SECRETS="${SECRETS_DIR:-$HOME/secrets}"
STAMP="${ARCHIVE_STAMP:-$(date -u +%Y-%m-%d)}"
ARCHIVE="$SECRETS/archive/${STAMP}"
MANIFEST="$ARCHIVE/manifest.txt"

cd "$SECRETS"

mkdir -p "$ARCHIVE"
chmod 700 "$SECRETS" "$SECRETS/archive" "$ARCHIVE"

echo "=== BEFORE ==="
find "$SECRETS" -maxdepth 1 -type f -printf '%f\t%M\t%s bytes\n' | sort

mapfile -t HISTORICAL < <(
    find "$SECRETS" -maxdepth 1 -type f \
        \( -name '*.bak.*' -o -name '*.save' -o -name '*.old' \) \
        -printf '%f\n' |
    sort
)

{
    echo "DREAMOS_VPS_SECRET_ARCHIVE"
    echo "CREATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "SOURCE=$SECRETS"
    echo "ARCHIVE=$ARCHIVE"
    echo
    echo "FILES:"
} > "$MANIFEST"

for name in "${HISTORICAL[@]}"; do
    path="$SECRETS/$name"

    printf '%s\t%s\t%s\n' \
        "$name" \
        "$(sha256sum "$path" | awk '{print $1}')" \
        "$(stat -c '%a' "$path")" \
        >> "$MANIFEST"

    mv -- "$path" "$ARCHIVE/$name"
    chmod 600 "$ARCHIVE/$name"
done

chmod 600 "$MANIFEST"

echo
echo "=== ACTIVE SECRET FILES ==="
find "$SECRETS" -maxdepth 1 -type f -printf '%f\t%M\t%s bytes\n' | sort

echo
echo "=== ARCHIVED FILES ==="
find "$ARCHIVE" -maxdepth 1 -type f -printf '%f\t%M\t%s bytes\n' | sort

echo
echo "=== PERMISSION GATE ==="
bad=0

while IFS= read -r file; do
    mode="$(stat -c '%a' "$file")"

    if [ "$mode" != "600" ]; then
        echo "BAD_MODE=$mode FILE=$file"
        bad=1
    fi
done < <(find "$SECRETS" -maxdepth 1 -type f)

if [ "$bad" -ne 0 ]; then
    echo "STATUS=FAIL_SECRET_FILE_PERMISSIONS"
    exit 1
fi

echo "STATUS=PASS_VPS_SECRETS_ORGANIZED"
echo "ACTIVE_FILES=$(find "$SECRETS" -maxdepth 1 -type f | wc -l)"
echo "ARCHIVED_FILES=${#HISTORICAL[@]}"
echo "MANIFEST=$MANIFEST"
echo "DELETIONS=0"
