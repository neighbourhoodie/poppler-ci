#!/bin/bash

# exit if any command fails
set -e

if [ ! -f .env ]; then
  echo "Exiting: could not find .env file!"
  exit 1
fi

set -a
source .env
set +a

sudo docker run  --rm \
  -e DOMAIN="${DOMAIN}" \
  -e CERTBOT_EMAIL="${CERTBOT_EMAIL}" \
  -v "$PWD/etc/letsencrypt:/etc/letsencrypt" \
  --name cert-renew \
  certbot/certbot \
  certonly --webroot --webroot-path=/etc/letsencrypt --non-interactive --agree-tos -d "${DOMAIN}" --email "${CERTBOT_EMAIL}"

# Restart nginx container
docker-compose restart nginx
