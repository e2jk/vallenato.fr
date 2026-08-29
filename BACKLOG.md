# Backlog

Open topics only. When an item is done, delete it from this file rather than
checking it off — this file should always reflect what's left, not history
(that's what git log is for).

Prerequisite for everything below: the current Docker image/build/CI effort
needs to land first. This backlog is the plan for the phase after that.

## 1. Migrate from the static-site generator to a Flask app

The current pipeline (`bin/website.py`) doesn't really template anything: it
duplicates `website/src/index.html` into ~120+ near-identical files via raw
`str.replace()` (no escaping), and ships the entire site's data (`data.js`,
~120KB) to the browser on every single page so client-side JS (`script.js`)
can pick out the one location/video that page is "about". Move to Flask +
Jinja instead:

- Load the existing location/video JSON at app startup (no database —
  the data is small and this stays a read-only, unauthenticated site).
- Replace the file-duplication + placeholder-replace hack with real Jinja
  templates/includes; this also fixes the unescaped-title issue for free
  via autoescaping.
- Replace the manual CDN-swap `.replace()` calls (Bootstrap/jQuery/Leaflet/
  bootstrap4-toggle, src vs prod) with proper Jinja-templated asset refs.
- Keep `bin/aprender.py`/`youtube.py` as the offline data-refresh pipeline —
  they keep writing the JSON data file, they just stop generating HTML.
- Keep the Leaflet map + click-to-overlay UX as-is; only the page
  generation/routing plumbing around it changes.
- Update/rewrite `tests/test_website.py` accordingly.

## 2. Replace the hand-rolled SPA routing JS with HTMX

`script.js` reimplements `pushState`/history-based navigation and video/
location overlays (~200 of its 346 lines) on top of the single-page shell.
Once routes are server-rendered (item 1), replace that with `hx-boost` +
Jinja partials: full SSR page on direct hit/crawler/no-JS, HTMX swaps in
partials for in-page nav clicks. Leaflet itself is untouched — this only
replaces the navigation/overlay wiring around it. Not a performance
project (pages are already tiny); the point is deleting bespoke JS.

## 3. Add i18n / multi-language support

Once on Jinja, add `Flask-Babel`, wrap the (currently Spanish-only) UI
strings in `_()`, add locale directories. Do this after items 1 and 2 so
there's only one set of templates to wrap, not two.

## 4. New hosting: Docker Compose + Traefik, drop nginx and the old VPS

Old VPS (`pascal.klein.st`, referenced in `upload.sh`) is dead; no reason to
resurrect the rsync/SSH deploy flow. Follow OpenHangar's pattern, scaled
down for a stateless read-only site (no DB, no auth, no socket-proxy needed):

- Single Dockerfile: `python:alpine` + gunicorn, non-root user,
  `read_only` rootfs, `cap_drop: ALL`, `no-new-privileges`, healthcheck.
  Replaces the current `linuxserver/baseimage-alpine-nginx` image and its
  Dockerfile entirely, and folds today's two Dockerfiles/two compose
  services (`vallenato.fr` nginx + `vallenato.fr_bin` generator) into one.
- **Open question to resolve before writing the compose file**: will this
  run on the same host as OpenHangar? If yes, join its existing Traefik
  `frontend` network with router labels for `vallenato.fr` — no new
  reverse proxy needed. If not, it needs its own minimal Traefik (or to
  point at whatever reverse proxy that host already runs).
- Retire `upload.sh` and the SSH/rsync deploy step once the new container
  is live.
