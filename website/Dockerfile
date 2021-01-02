# Base on https://docs.linuxserver.io/images/docker-nginx
FROM ghcr.io/linuxserver/nginx:latest

# Include the production website files
COPY ./prod /config/www

# The nginx config file
COPY ./nginx-config/default /config/nginx/site-confs/
