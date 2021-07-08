Docker setup
============

Build the image:
----------------
From the root of the `vallenato.fr` folder:

`docker build -f bin/Dockerfile -t e2jk/vallenato.fr_bin --rm .`

To force building without cached intermediate containers:

`docker build -f bin/Dockerfile -t e2jk/vallenato.fr_bin --rm --no-cache .`

Run the script:
---------------
`$ docker run --rm -it e2jk/vallenato.fr_bin:latest`

When updating the website or creating a new tutorial, the `website/` folder needs to be mapped as a volume so that the changes are kept after the container is stopped:

`$ docker run --rm -it --volume ~/devel/vallenato.fr/website:/app/website --user "$(id -u):$(id -g)" e2jk/vallenato.fr_bin:latest --aprender`

In addition, when developing the script within the Docker container, the `bin/` folder also needs to be mapped:

`$ docker run --rm -it --volume ~/devel/vallenato.fr/website:/app/website --volume ~/devel/vallenato.fr/bin:/app/bin --user "$(id -u):$(id -g)" e2jk/vallenato.fr_bin:latest --help`

Log into the image to get shell access:
---------------------------------------
`$ docker run --rm -it --entrypoint /bin/bash e2jk/vallenato.fr_bin:latest`

Run the test suite:
-------------------
`$ docker run --rm -it --entrypoint sh e2jk/vallenato.fr_bin:latest test.sh`
