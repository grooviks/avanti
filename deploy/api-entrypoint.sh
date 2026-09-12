#!/bin/sh
set -eu

# Docker secrets stay outside the image and repository. Export them only for
# the process being started below, so Pydantic reads its usual AVANTI_* vars.
if [ -f /run/secrets/database_url ]; then
  export AVANTI_DATABASE_URL="$(cat /run/secrets/database_url)"
fi

if [ -f /run/secrets/secret_key ]; then
  export AVANTI_SECRET_KEY="$(cat /run/secrets/secret_key)"
fi

exec "$@"
