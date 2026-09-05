# bee: project conventions

Read this before touching any file. It overrides your defaults.

## what this is
A spelling bee web game (hexagon of 7 letters, mandatory centre letter) to be hosted under tafo.ch. Full spec in `docs/SPEC.md`, themes in `docs/THEMES.md`, hosting in `docs/DEPLOY.md`. The hand-off prompt that drives the build is `PROMPT.md`.

## stack, fixed
- Python 3.12, Flask, Jinja2, sqlite3 (stdlib), gunicorn for serving. Nothing else at runtime. pytest for tests only.
- No JS frameworks, no build step, no npm, no CDN assets, no web fonts. One small vanilla `<script>` block in `templates/play.html`, hard cap 60 lines.
- One CSS file, `static/style.css`, hard cap 220 lines including all 8 themes.
- Dictionary is the plain text file `data/words.txt` (one lowercase word per line, already 4+ letters). Load it, never fetch anything at runtime.

## layout, fixed
```
app.py            routes, cookies, admin auth
game.py           puzzle codes, generation, validation, scoring, ranks
store.py          sqlite schema + queries
templates/        base.html index.html play.html done.html admin.html
static/style.css
data/words.txt    dictionary (do not edit by hand)
data/exclude.txt  optional, words to remove at load
tools/build_dict.sh
tests/test_game.py
docs/             SPEC THEMES DEPLOY
Dockerfile  compose.yaml  requirements.txt  README.md  LICENSE
```
Do not add files outside this list without a reason written in README "decisions".

## code style, non-negotiable
- Compact. Prefer comprehensions, dict lookups, `dataclass`, early returns, `functools.lru_cache`. No classes where a function does. No ORM, no blueprints, no config classes.
- Budgets: `app.py` <= 140 lines, `game.py` <= 90, `store.py` <= 70. If you exceed one, simplify, do not split into more files.
- Comments: fully lowercase, very brief, only where the code is not self explanatory. No docstrings longer than one line. No section banners.
- Names: short but real words (`words`, `centre`, `code`, `found`). British spelling in identifiers and copy (`centre`, `colour`).
- Type hints on function signatures, nowhere else.
- Errors: return a message string, never raise into the user's face. `/guess` always answers JSON.
- No `print`. Flask's logger only if needed.
- f-strings everywhere. No `%` or `.format`.
- No em dashes anywhere in code, comments, templates or docs. Use commas or full stops.

## behaviour rules for the agent
- Follow `PROMPT.md` step order. Finish and verify a step before starting the next.
- Only stop to ask about stylistic matters (palettes, layout, fonts, rank names, copy). For everything else pick the simplest option that meets `docs/SPEC.md`, and log the choice under "decisions" in README.md.
- Verify every step by running it: `pytest -q`, then `flask --app app run` and hit the routes with `curl`. A step is not done until it runs.
- Commit after every step with a one line lowercase message.
