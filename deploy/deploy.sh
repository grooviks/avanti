#!/usr/bin/env sh
set -eu

APP_DIR=${APP_DIR:-/opt/avanti}
COMPOSE_FILE=${COMPOSE_FILE:-$APP_DIR/compose.prod.yaml}
IMAGE_TAG=${1:-}

if [ -z "$IMAGE_TAG" ]; then
  echo "Usage: $0 <immutable-image-tag>" >&2
  exit 2
fi

case "$IMAGE_TAG" in
  *[!0-9a-f]*)
    echo "Image tag must be a commit SHA." >&2
    exit 2
    ;;
esac

cd "$APP_DIR"
[ -f .env ] || { echo "Missing $APP_DIR/.env" >&2; exit 1; }
set -a
. ./.env
set +a

[ -f "$SECRETS_DIR/database_url" ] || { echo "Missing database_url secret." >&2; exit 1; }
[ -f "$SECRETS_DIR/secret_key" ] || { echo "Missing secret_key secret." >&2; exit 1; }

if grep -q '^IMAGE_TAG=' .env; then
  sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=$IMAGE_TAG/" .env
else
  printf '\nIMAGE_TAG=%s\n' "$IMAGE_TAG" >> .env
fi
export IMAGE_TAG

iam_token=$(curl --fail --silent --header Metadata-Flavor:Google \
  http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token \
  | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
[ -n "$iam_token" ] || { echo "Could not obtain an IAM token from VM metadata." >&2; exit 1; }
printf '%s' "$iam_token" | docker login --username iam --password-stdin cr.yandex >/dev/null

mkdir -p backups
if [ -f "$SECRETS_DIR/database_backup_url" ]; then
  backup_url=$(tr -d '\n' < "$SECRETS_DIR/database_backup_url")
  backup_url=$(printf '%s' "$backup_url" | sed 's#^postgresql+asyncpg:#postgresql:#')
  pg_dump --format=custom --file "backups/pre-deploy-$(date +%Y%m%d-%H%M%S).dump" "$backup_url"
fi

docker compose -f "$COMPOSE_FILE" pull
docker compose -f "$COMPOSE_FILE" run --rm api alembic upgrade head
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

attempt=0
until curl --fail --silent "http://127.0.0.1:${AVANTI_WEB_PORT:-3001}/" >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "Web health check failed." >&2
    docker compose -f "$COMPOSE_FILE" ps
    exit 1
  fi
  sleep 2
done

docker image prune -f
echo "Deployed Avanti images with tag $IMAGE_TAG"
