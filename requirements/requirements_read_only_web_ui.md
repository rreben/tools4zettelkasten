# Requirements: Read-only mode for the Flask web UI

**Component:** Flask web UI (`tools4zettelkasten/flask_views.py`, templates)
**Type:** Feature / deployment hardening
**Created:** 2026-10-05

## What and why

The web UI (`start`) shall also run on the VPS so the Zettelkasten can be read
from iPhone/iPad over the Tailscale tailnet. On the VPS the Zettelkasten is a
one-way rclone mirror of the Dropbox folder, mounted read-only. Editing there
is impossible by design: a write would fail on the read-only mount, and even on
a writable mount the next `rclone sync` would silently overwrite it.

The UI therefore needs a read-only mode. The edit function must stay visible
but greyed out, so the user sees that editing exists but is unavailable in this
deployment.

Running behind a production WSGI server (gunicorn) also requires that the Flask
`SECRET_KEY` can be configured, because `run_flask_server()` is not called
there and sessions (chat) and CSRF (edit form) need a stable key across
workers.

While touching the templates: `polyfill.io` is removed. The domain changed
owners in 2024 and served malicious code; MathJax 3 does not need the polyfill.

## Acceptance criteria

1. New setting `READ_ONLY` (env/`.env`), default `false`. Accepted true values:
   `1`, `true`, `yes`, `on` (case-insensitive).
2. With `READ_ONLY=true`:
   - The note view shows the Edit button **disabled and greyed out**
     (`btn btn-outline-secondary`, `disabled`), with a tooltip explaining
     read-only mode; it does not link to `/edit/...`.
   - The keyboard shortcut `E` does not navigate to the edit view.
   - `GET` and `POST` on `/edit/<filename>` return HTTP 403 and do not write
     any file.
3. With `READ_ONLY=false` the behaviour is unchanged (active Edit button,
   shortcut `E`, saving works).
4. New setting `FLASK_SECRET_KEY` (env/`.env`). If set it is used as
   `app.config['SECRET_KEY']`; otherwise a random key is generated at import
   time (previous behaviour). `run_flask_server()` no longer overwrites a
   configured key.
5. The `settings` command shows `READ_ONLY` and whether `FLASK_SECRET_KEY` is
   set (never its value).
6. No template references `polyfill.io`.
7. Configuration only via `settings.py` / `os.environ.get()`; the views read
   `st.READ_ONLY` at request time (so tests can toggle it).

## Affected files

- `tools4zettelkasten/settings.py` — `READ_ONLY`, `FLASK_SECRET_KEY`
- `tools4zettelkasten/flask_views.py` — secret key at import, context
  processor for `read_only`, 403 guard in `edit()`
- `tools4zettelkasten/flask_frontend/templates/mainpage.html` — disabled Edit
  button, shortcut guard, remove polyfill.io
- `tools4zettelkasten/flask_frontend/templates/edit.html` — remove polyfill.io
- `tools4zettelkasten/cli.py` — settings output
- `.env.example`, `README.rst` — documentation
- `tests/test_flask_views.py`, `tests/test_settings_read_only.py` — tests

## Test plan

- Parsing of `READ_ONLY` values (true variants, false, unset).
- Read-only: note view contains a disabled Edit button and no `/edit/` link.
- Read-only: `GET /edit/<file>` → 403.
- Read-only: `POST /edit/<file>` → 403, file content unchanged.
- Read-write: note view contains active `/edit/` link; POST saves content.
- Templates contain no `polyfill.io`.
- Full suite (`pytest tests/ -v`) stays green.
