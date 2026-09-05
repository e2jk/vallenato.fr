# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim-bookworm@sha256:0f5b26b9518d002b6173fd61daad821fa340635ebfec5bba471013f9ca114579

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# APT_CACHE_BUST: mirror of APK_CACHE_BUST in the top-level Dockerfile -- CI
# passes the current date here so this layer never replays a stale registry
# build-cache hit and silently skips OS security patches published since the
# base image digest above was pinned (bit us with libpcre2-8-0, fixed in
# 10.42-1+deb12u1, see run https://github.com/e2jk/vallenato.fr/actions/runs/33957089637).
ARG APT_CACHE_BUST=0
# DL3008: Debian package versions are already pinned by the base image's own
# bookworm release; pinning apt versions individually is high-maintenance and
# old versions get purged from the mirror once superseded by a security update.
# hadolint ignore=DL3008
RUN echo "cache bust: ${APT_CACHE_BUST}" && \
    apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Install pip requirements
# The base image's own bundled pip (25.0.1) carries known CVEs (needs 26.2+
# to clear) - upgrade it, hash-pinned, before using it to install anything.
COPY bin/requirements-pip-bootstrap.txt /app/bin/requirements-pip-bootstrap.txt
COPY bin/requirements.txt /app/bin/requirements.txt
# pip itself is only a build-time tool - the entrypoint below never imports
# or shells out to it. Uninstall it once it's done its job: it also takes its
# own vendored copies of setuptools/msgpack/etc. with it, so CVEs against
# those (which track pip's release cadence, not ours) can't show up in a
# published image that no longer contains them.
RUN python -m pip install --no-cache-dir --require-hashes -r /app/bin/requirements-pip-bootstrap.txt && \
    python -m pip install --no-cache-dir --require-hashes -r /app/bin/requirements.txt && \
    python -m pip uninstall -y pip

WORKDIR /app/bin
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER 5678

ENTRYPOINT ["python", "vallenato_fr.py"]
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["--help"]
