#!/usr/bin/env bash
# Prepare Nginx and the directories used to deploy AirBnB static pages.

if ! command -v nginx >/dev/null 2>&1; then
    apt-get update
    apt-get install -y nginx
fi

mkdir -p /data/web_static/releases/test /data/web_static/shared

cat > /data/web_static/releases/test/index.html <<'HTML'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>AirBnB static test</title>
  </head>
  <body>
    Holberton School
  </body>
</html>
HTML

ln -sfn /data/web_static/releases/test /data/web_static/current
chown -R ubuntu:ubuntu /data/

cat > /etc/nginx/hbnb_static.conf <<'NGINX'
location = /hbnb_static {
    return 301 /hbnb_static/;
}

location ^~ /hbnb_static/ {
    alias /data/web_static/current/;
    index index.html;
}
NGINX

for site in /etc/nginx/sites-available/default /etc/nginx/sites-enabled/*; do
    [ -f "$site" ] || continue
    site=$(readlink -f "$site")
    if ! grep -q 'include /etc/nginx/hbnb_static.conf;' "$site"; then
        sed -i '/^[[:space:]]*server[[:space:]]*{/a\    include /etc/nginx/hbnb_static.conf;' "$site"
    fi
done

if nginx -t; then
    service nginx restart
fi

exit 0
