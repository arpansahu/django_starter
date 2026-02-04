# ================= SERVICE PROXY TEMPLATE =================

# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;

    server_name [DOMAIN_NAME];
    return 301 https://$host$request_uri;
}

# HTTPS reverse proxy
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name [DOMAIN_NAME];

    # 🔐 Wildcard SSL (acme.sh + Namecheap DNS-01)
    ssl_certificate     /etc/nginx/ssl/arpansahu.space/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/arpansahu.space/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://0.0.0.0:[PROJECT_DOCKER_PORT];

        proxy_http_version 1.1;

        # Required headers
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        # WebSocket support (safe for all services)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}