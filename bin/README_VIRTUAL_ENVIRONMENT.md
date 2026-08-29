Virtual environment setup
=========================

Create the environment:
-----------------------
```bash
$ cd devel/vallenato.fr/
$ python3 -m venv .venv-vallenato_fr
$ source .venv-vallenato_fr/bin/activate
$ pip install --require-hashes -r bin/requirements-pip-bootstrap.txt
$ pip install --require-hashes -r bin/requirements.txt
$ pip install --require-hashes -r bin/requirements-dev.txt
```

The first `pip install` upgrades pip itself before it's used to install
anything else - `python -m venv` bundles whatever pip version ships with
that Python build's `ensurepip`, which isn't necessarily current or free of
known CVEs. All three files are hash-pinned - `bin/requirements-dev.txt`
(linting/testing tools) isn't part of the production image, but is pinned
the same way regardless, since it also fixes a real false-positive:
OSV-Scanner falls back to a stale bundled transitive-dependency guess for
an unpinned requirements.txt line and gets it wrong otherwise.

Activate the virtual environment:
---------------------------------
`$ source ~/devel/vallenato.fr/.venv-vallenato_fr/bin/activate`

When done:
----------
`$ deactivate`

Update the dependencies:
------------------------
`$ pip install --require-hashes -r bin/requirements.txt && pip install --require-hashes -r bin/requirements-dev.txt`

Renovate manages `bin/requirements*.txt` automatically (see the repo root
`renovate.json`) - manual bumps are only needed between its scheduled runs.
