El Vallenatero Francés
======================

[![CI](https://github.com/e2jk/vallenato.fr/actions/workflows/ci.yml/badge.svg)](https://github.com/e2jk/vallenato.fr/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/e2jk/vallenato.fr/badge)](https://securityscorecards.dev/viewer/?uri=github.com/e2jk/vallenato.fr)
[![Coverage](https://e2jk.github.io/vallenato.fr/coverage/badge.svg)](https://e2jk.github.io/vallenato.fr/coverage/)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue)](https://github.com/e2jk/vallenato.fr/blob/master/LICENSE)
[![Docker (site)](https://img.shields.io/badge/docker-ghcr.io%2Fe2jk%2Fvallenato.fr-blue?logo=docker)](https://github.com/e2jk/vallenato.fr/pkgs/container/vallenato.fr)
[![Docker (bin)](https://img.shields.io/badge/docker-ghcr.io%2Fe2jk%2Fvallenato.fr__bin-blue?logo=docker)](https://github.com/e2jk/vallenato.fr/pkgs/container/vallenato.fr_bin)
[![Last commit](https://img.shields.io/github/last-commit/e2jk/vallenato.fr)](https://github.com/e2jk/vallenato.fr/commits/master)

Tutoriales videos para aprender a tocar el Acordeón Vallenato

Donde ver los tutoriales
------------------------

https://vallenato.fr - https://vallenato.fr/aprender/

Estructura de este Repository
-----------------------------

* [`./bin`](../../tree/master/bin): Script para gestionar el sitio: meter al dia la lista de videos en el sition, crear nuevos tutoriales.
* [`./website`](../../tree/master/website/src): El sitio https://vallenato.fr/, incluyendo los tutoriales de [`/aprender`](../../tree/master/website/src/aprender)
* [`./scripts`](../../tree/master/scripts): Herramientas del pipeline (`ship.sh`, el generador del badge de cobertura, etc.) - ver más abajo.

Landing changes on master
--------------------------

Every push/PR runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml): lint,
type-check, security scans, the full `bin/` test suite (100% coverage
required), and a build+smoke-test of both Docker images (the nginx site
image and the `bin/` CLI tool image).

For the repo owner's own solo commits, `scripts/ship.sh` skips the normal
fork-and-PR dance: it rebases the current branch onto `origin/master` and
pushes to a `ship` branch, which `auto-pr-merge.yml` picks up to open (or
reuse) a PR into `master` with GitHub's native auto-merge armed - it lands
on its own once CI is green. Requires a `PAT_AUTO_PR_MERGE` repository
secret (see that workflow's own comments for why and how to create one).
External contributors should keep using the normal fork-and-PR flow
straight into `master`, which `ship.sh` has no part in.

Dependency updates are split between [Renovate](renovate.json) (pip,
Docker) and [Dependabot](.github/dependabot.yml) (GitHub Actions only -
the two are configured not to compete for the same ecosystem). Both
auto-merge once CI passes.

Before pushing, install the pre-push hook once per clone:

```
git config core.hooksPath .githooks
```

It runs the same lint/type/security checks as CI, locally, before you push.

<!-- CI validation test PR, safe to ignore -->
