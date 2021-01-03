El Vallenatero Francés
======================

## Development server:

### Production-like, with the actual Nginx server configuration:

* Build the Docker image (first two steps listed below)
* Run ``docker run -it --rm -p 8080:80 -e PUID=1000 -e PGID=1000 --name vallenato.fr -v `pwd`/src/:/config/www/ -v `pwd`/nginx-config/development:/config/nginx/site-confs/default e2jk/vallenato.fr`` from the `website` folder and access from your browser at http://localhost:8080/

### Quick and dirty:

Run `$ python3 -m http.server 8000 --bind 127.0.0.1` in the `website/src` folder

## Create the Docker image and publish it to Docker Hub

Run:

* `cd bin/ && python vallenato_fr.py --website && cd ..` to build the production website files
* `cd website/ && docker build -t e2jk/vallenato.fr:latest --rm .` to build the Docker image.
* ``docker run -it --rm -p 8080:80 -e PUID=1000 -e PGID=1000 --name vallenato.fr -v `pwd`/prod/aprender/videos/:/config/www/aprender/videos e2jk/vallenato.fr`` to test the Docker image locally at address http://localhost:8080/
* `docker push e2jk/vallenato.fr:latest` to push the Docker image to Docker Hub.
