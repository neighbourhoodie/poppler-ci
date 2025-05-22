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

echo "Setting up Letsencrypt…"
mkdir -p ./etc/letsencrypt
mkdir -p ./var/lib/letsencrypt

mkdir -p ./etc/nginx/conf.d

sudo docker run -it --rm \
 -p 80:80 -p 443:443 \
 --name certbot \
 -v "$PWD/etc/letsencrypt:/etc/letsencrypt" \
 -v "$PWD/var/lib/letsencrypt:/var/lib/letsencrypt" \
 certbot/certbot certonly \
 --standalone -d "$DOMAIN" --email "$CERTBOT_EMAIL" \
 --agree-tos --keep --non-interactive

cp ./renew_certificate_job /etc/cron.d/renew_certificate_job
chmod +x ./renew-certificate.sh

echo "All Done!"
