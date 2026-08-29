# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Report vulnerabilities privately using GitHub's built-in security advisory feature:

**[Report a vulnerability](https://github.com/e2jk/vallenato.fr/security/advisories/new)**

## What to Include

- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- Affected versions/commit (if known)
- Any suggested mitigations

## Disclosure Policy

- We will acknowledge receipt within **5 business days**.
- We aim to release a fix within **90 days** of the initial report.
- We will coordinate public disclosure with the reporter and publish a GitHub Security Advisory once a fix is available.
- If a fix cannot be delivered within 90 days, we will notify the reporter and agree on an extended timeline.

## Scope

vallenato.fr is a static site generator: `bin/` builds a static HTML/JS/CSS
site (`website/prod`) from YouTube metadata, published behind nginx with no
server-side application logic, user accounts, or database. In scope:

- Cross-site scripting (XSS) in the generated site
- Supply-chain issues in `bin/requirements*.txt` or the published Docker
  images (`ghcr.io/e2jk/vallenato.fr`, `ghcr.io/e2jk/vallenato.fr_bin`)
- Exposure of credentials or secrets (e.g. YouTube API credentials) through
  the build pipeline or published artifacts
- Vulnerabilities in the CI/CD pipeline (GitHub Actions workflows) that
  could allow unauthorized code execution or publishing

Out of scope:

- The YouTube-hosted video content itself
- Third-party CDN assets (Mapbox, Bootstrap, jQuery, Leaflet) loaded by the
  generated site
