#!/usr/bin/env bash
set -euo pipefail

# Архивная SQL-копия старой базы. Пароль хранится в MYSQL_DEFAULTS_FILE
# (например, /root/.my.cnf с правами 600), поэтому не попадает в историю shell.
: "${MYSQL_DEFAULTS_FILE:?Set path to a MySQL defaults file}"
: "${LEGACY_MYSQL_DATABASE:?Set legacy database name}"
: "${EXPORT_DIR:?Set output directory}"

mkdir -p "$EXPORT_DIR"
mysqldump --defaults-extra-file="$MYSQL_DEFAULTS_FILE" --single-transaction \
  --routines --events --hex-blob --default-character-set=utf8mb4 \
  "$LEGACY_MYSQL_DATABASE" | gzip -9 > "$EXPORT_DIR/legacy-mysql.sql.gz"
printf 'Created %s\n' "$EXPORT_DIR/legacy-mysql.sql.gz"
