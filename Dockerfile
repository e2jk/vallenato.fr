# Based on https://github.com/linuxserver/docker-baseimage-alpine-nginx/blob/master/Dockerfile
# except without:
# * PHP
# * git
# * apache2-utils
# * SSL support (will be run behind a reverse proxy that will handle SSL)
#
# Needs the files in ./root from https://github.com/linuxserver/docker-baseimage-alpine-nginx/tree/master/root
# but remove the following folders and files:
# * ./root/etc/services.d/php-fpm/
# * ./root/etc/logrotate.d/php-fpm7
# * ./root/etc/cont-init.d/30-keygen
# And comment all mentions to PHP in ./root/etc/cont-init.d/20-config

FROM ghcr.io/linuxserver/baseimage-alpine:3.24@sha256:34c19f3f2345f1d231784e78db95e330ce198c267b10fe8daa88b6bded30636b
LABEL org.opencontainers.image.title="vallenato.fr"

# install packages
# DL3018: Alpine package versions are already pinned by the base image's
# own Alpine release (3.24 above); pinning apk versions individually is
# high-maintenance and old versions get purged from the mirror.
# SC2016: the single quotes below are intentional -- the nginx variable
# syntax must reach the config file literally, not get shell-expanded.
# hadolint ignore=DL3018,SC2016
RUN \
 echo "**** drop the community repo -- logrotate/nano/nginx all live in main, and apk refuses to proceed if ANY configured repo's index is unreachable, even for a package that lives entirely in main (the community mirror intermittently serves a corrupt index) ****" && \
 sed -i "/community/d" /etc/apk/repositories && \
 echo "**** apply security patches not yet in the pinned base image digest ****" && \
 apk upgrade --no-cache && \
 echo "**** install build packages ****" && \
 apk add --no-cache \
#	apache2-utils \
#	git \
#	libressl3.1-libssl \
	logrotate \
	nano \
	nginx \
#	openssl \
#	php7 \
#	php7-fileinfo \
#	php7-fpm \
#	php7-json \
#	php7-mbstring \
#	php7-openssl \
#	php7-session \
#	php7-simplexml \
#	php7-xml \
#	php7-xmlwriter \
#	php7-zlib && \
 && \
 echo "**** configure nginx ****" && \
 echo 'fastcgi_param  SCRIPT_FILENAME $document_root$fastcgi_script_name;' >> \
	/etc/nginx/fastcgi_params && \
 rm -f /etc/nginx/conf.d/default.conf && \
 echo "**** fix logrotate ****" && \
 sed -i "s#/var/log/messages {}.*# #g" /etc/logrotate.conf && \
 sed -i 's#/usr/sbin/logrotate /etc/logrotate.conf#/usr/sbin/logrotate /etc/logrotate.conf -s /config/log/logrotate.status#g' \
	/etc/periodic/daily/logrotate

# add local files
COPY website/root/ /

# ports and volumes
#EXPOSE 80 443
EXPOSE 80
VOLUME /config


# End of docker-baseimage-alpine-nginx


# Include the production website files
COPY ./website/prod /config/www

# The nginx config file
COPY ./website/nginx-config/production /config/nginx/site-confs/default
