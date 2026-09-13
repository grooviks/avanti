# Nginx and TLS

These configs assume that Nginx and the Compose stack run on the same VM. The
public site is `https://avantistyle.ru`; `www` redirects to it.

Nginx is installed directly on the VM; it is not a Docker container. It can
serve this and other sites through separate files in `/etc/nginx/conf.d/`.

The final config uses the existing certificate files from the prior site:

```text
/etc/nginx/ssl/avantistyle_ru.crt
/etc/nginx/ssl/avantistyle_ru.key
```

Change those two paths in `avantistyle.conf` if the files are stored elsewhere.
The certificate must contain both `avantistyle.ru` and `www.avantistyle.ru`,
because the `www` host is redirected only after the TLS handshake. Verify this
once on the VM:

```sh
sudo openssl x509 -in /etc/nginx/ssl/avantistyle_ru.crt -noout -text | grep -A1 "Subject Alternative Name"
```

## Installation

1. Point both `avantistyle.ru` and `www.avantistyle.ru` DNS records to the VM
   and open TCP 80/443 in the firewall.
2. In `/opt/avanti/.env` set:

   ```dotenv
   AVANTI_WEB_BIND_ADDRESS=127.0.0.1
   AVANTI_WEB_PORT=3001
   AVANTI_SITE_URL=https://avantistyle.ru
   ```

   Redeploy the stack after changing these values. Port 3001 will then not be
   reachable from the Internet.
3. Copy the final site config without replacing Nginx's main `nginx.conf` or
   configurations of other sites:

   ```sh
   sudo cp /opt/avanti/deploy/nginx/avantistyle.conf /etc/nginx/conf.d/avantistyle.conf
   sudo nginx -t && sudo systemctl reload nginx
   ```

The file `avantistyle.http.conf` is retained only for a future certificate
issuance or renewal through ACME. It is not needed with the current certificate.

## Nginx on a separate VM

Set `AVANTI_WEB_BIND_ADDRESS` to the Docker VM's private IP (not `127.0.0.1`),
replace `127.0.0.1:3001` in the final config with that private IP, and permit
port 3001 only from the Nginx VM's private IP in the Docker VM firewall.
