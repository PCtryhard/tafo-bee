# bee: hosting on tafo.ch

What tafo.ch itself runs on is not known yet. The site embeds a TutorBird widget and carries a noindex tag, which points at a hosted site builder rather than a server the boss administers. The plan below works in either case: the game runs as its own small service on a **subdomain**, `bee.tafo.ch`, and the main site links to it or embeds it.

## what the app needs

- Python 3.12, `pip install -r requirements.txt`, then `gunicorn -b 0.0.0.0:$PORT app:app`.
- One writable directory for `data/bee.db` (sqlite). That is the only state.
- Environment: `SECRET_KEY` (random string), `ADMIN_PASSWORD`, optional `DB_PATH`, `MIN_WORDS`, `MAX_WORDS`, `ALLOW_S`, `PORT` (default 8000).
- Memory well under 100 MB, single process is enough for the expected traffic. Use `--workers 1` with sqlite; more workers are fine too since writes are tiny, but one keeps it simple.

## option A, a small VPS (recommended, about 5 CHF a month)

Any Debian or Ubuntu VPS (Hetzner, Infomaniak, DigitalOcean) with Docker.

1. DNS: at the tafo.ch registrar add an `A` record `bee` pointing at the VPS IP (and `AAAA` if it has IPv6).
2. On the VPS: `git clone <repo> && cd bee && cp .env.example .env`, fill in the two secrets.
3. `docker compose up -d`. The compose file runs the app and a Caddy reverse proxy; Caddy obtains and renews the TLS certificate for `bee.tafo.ch` automatically.
4. Check `https://bee.tafo.ch` and `https://bee.tafo.ch/admin`.
5. Backups: the whole state is `data/bee.db`. A nightly `cp` to another location is sufficient.

Files the repo must contain for this: `Dockerfile`, `compose.yaml` (app + caddy, named volume for `data`), `Caddyfile` (two lines: the host and `reverse_proxy app:8000`), `.env.example`.

## option B, a PaaS

Fly.io or Render, both run the Dockerfile as is. Attach a persistent volume mounted at `/app/data` so the sqlite file survives deploys, set the env vars in their dashboard, add `bee.tafo.ch` as a custom domain and create the CNAME they give you at the registrar. Slightly more per month than a VPS, no server to maintain.

## option C, the boss already has a server

If tafo.ch turns out to run on a machine he controls (nginx or Apache), run the app there with gunicorn under systemd on port 8000 and add a reverse proxy block for `bee.tafo.ch` (or a path such as `tafo.ch/bee`, in which case Flask needs `APPLICATION_ROOT=/bee` and the proxy must set `X-Forwarded-Prefix`). A subdomain avoids all of that and is the default.

## putting it on the main site

Once the subdomain is live, the main site needs one of:

- a menu link or button to `https://bee.tafo.ch`, simplest and best on mobile;
- an embed: `<iframe src="https://bee.tafo.ch" style="width:100%;height:720px;border:0" title="Spelling bee"></iframe>`. The app must not send `X-Frame-Options: DENY`; set `Content-Security-Policy: frame-ancestors 'self' https://tafo.ch https://www.tafo.ch` instead so only tafo.ch may embed it.

## local run

```
pip install -r requirements.txt
ADMIN_PASSWORD=x SECRET_KEY=dev flask --app app run --debug
```
