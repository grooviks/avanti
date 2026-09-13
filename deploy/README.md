# Production deployment on one VM

Avanti starts two containers: `web` (proxied by Nginx) and `api` (available only
to `web` on the Compose network). PostgreSQL remains installed on the VM.
The public deployment uses Nginx and TLS; see [nginx/README.md](nginx/README.md).

## One-time VM setup

1. Install Docker Engine with the Compose plugin, PostgreSQL client tools (`pg_dump`)
   and `curl`.
2. Attach a service account with the `container-registry.images.puller` role to
   the VM. `deploy.sh` obtains an IAM token from VM metadata; no registry key is
   stored on the server.
   The GitHub runner publishes `linux/amd64` images, so choose an x86_64 VM.
3. Copy `compose.prod.yaml`, `deploy/deploy.sh` and this directory's
   `.env.example` to `/opt/avanti`. Rename `.env.example` to `.env` and replace
   `<registry-id>`.
4. Create `/opt/avanti/secrets` with permissions `0700` and files with
   permissions `0600`:

   - `database_url` — `postgresql+asyncpg://avanti:<password>@host.docker.internal:5432/avanti`;
   - `secret_key` — a random JWT signing key of at least 32 bytes;
   - `database_backup_url` (optional) — same connection but with host `localhost`
     and scheme `postgresql://`; it enables a `pg_dump` before every deploy.

   Do not put these values in `.env` or git.

5. Let PostgreSQL accept connections from Docker but not from the Internet. The
   exact bridge subnet is shown by `docker network inspect bridge`. Add its
   gateway address to `listen_addresses` in `postgresql.conf`, and add a narrow
   rule such as this to `pg_hba.conf` (adjust subnet and database/user):

   ```text
   host    avanti    avanti    172.17.0.0/16    scram-sha-256
   ```

   Reload PostgreSQL afterwards. Keep the firewall closed for port 5432.

6. Copy the initial catalogue/media through the migration procedure before the
   first public deploy. Uploaded media is persisted in the `avanti_media` Docker
   volume; include it in backups until the planned S3 migration.
7. Configure Nginx, DNS and TLS using [nginx/README.md](nginx/README.md).

## CI configuration

In GitHub repository settings create:

- variable `YC_REGISTRY_ID` — Yandex Container Registry ID;
- secret `YC_REGISTRY_JSON_KEY` — JSON key of a service account allowed to push
  into that registry.

The workflow checks backend (`ruff`, migrations, `pytest`) against an isolated
PostgreSQL service and frontend (`npm run build`) on every PR. A push to `main`
additionally publishes `avanti-api` and `avanti-web` with the commit SHA and
`latest` tags.

## Deploy and rollback

On the VM, run an immutable version from the Actions log:

```sh
chmod +x /opt/avanti/deploy.sh
/opt/avanti/deploy.sh <commit-sha>
```

The script pulls both images, optionally makes a PostgreSQL backup, applies
Alembic migrations, starts the containers and checks the public Next.js port.
To roll back application code, rerun it with a previous SHA. Database migration
rollbacks are intentionally not automatic and should be reviewed separately.
