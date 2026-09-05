# hand-off prompt for claude code (fable 5.1)

Paste everything below the line into Claude Code, started inside this folder.

---

You are building `bee`, a spelling bee web game for my boss, to be hosted at bee.tafo.ch. This folder already contains the specification and conventions. Nothing else exists yet. Your job is to implement it end to end in one session, step by step, verifying each step by running it, and to push the result to a new public GitHub repository.

## before writing any code

1. Read `CLAUDE.md` in full. It fixes the stack, the file layout, the line budgets and the comment style (all comments fully lowercase and very brief). It wins over any habit you have.
2. Read `docs/SPEC.md`, `docs/THEMES.md`, `docs/DEPLOY.md`, `data/README.md`. The spec marks values as *default* (keep them, no need to ask) or *stylistic* (ask me).
3. Do not look at, search for, or reuse any existing spelling bee implementation. Write everything from scratch.

## how to work

- Go through the steps below in order. A step is done when its "verify" line passes. Commit after each step with a one line lowercase message.
- Do not ask me questions except at the two stylistic checkpoints marked **STOP**. For any other open point choose the simplest option that satisfies `docs/SPEC.md` and log it as one line under "decisions" in `README.md`.
- Keep the code compact. If a file goes over its budget in `CLAUDE.md`, simplify rather than split.
- Every function that can fail on user input returns a message, it does not raise.
- British spelling in identifiers and copy. No em dashes anywhere.

## steps

### 0. scaffold
Create `requirements.txt` (flask, gunicorn; pytest under a `# dev` comment), `LICENSE` (MIT, copyright holder "tafo.ch"), `.env.example` with the variables from SPEC section 8, and empty `app.py`, `game.py`, `store.py`, `tests/test_game.py`. `git init`, first commit.
Verify: `python -c "import flask"` works in a fresh venv.

### 1. game.py, the pure logic
Implement, with no Flask imports:
- `load_words() -> frozenset[str]` from `data/words.txt` minus `data/exclude.txt`, cached.
- `canon(letters: str, centre: str) -> str | None` returning the canonical code (centre first, six outer sorted) or None if invalid (not 7 distinct a to z letters, centre not among them).
- `words_for(code) -> list[str]` cached, sorted, with the three validity rules from SPEC 1.
- `is_pangram(word, code)`, `points(word, code)`, `max_score(code)`.
- `check(word, code, found) -> tuple[bool, str, int]` returning ok, message, points, with the rejection priority order from SPEC 4.
- `rank(score, code) -> str` using the thresholds and default names from SPEC 5 (names in one list at the top of the file so they are easy to change).
- `random_code(rng=None) -> str` and `daily_code(day: date) -> str` per SPEC 2, honouring `MIN_WORDS`, `MAX_WORDS`, `ALLOW_S` from the environment with the spec defaults.
Then write `tests/test_game.py` covering everything SPEC 8 lists. Use small hand built cases for validation and scoring, and property style checks for generation (100 random codes are all acceptable and each has a pangram; `daily_code` is stable for a fixed date).
Verify: `pytest -q` green, and `python -c "import game, time; t=time.time(); [game.random_code() for _ in range(20)]; print(time.time()-t)"` prints under 1.0.

### 2. store.py, sqlite
Schema from SPEC 6 as one `CREATE TABLE IF NOT EXISTS`. Functions: `init()`, `new_game(session, name, code, theme) -> id`, `get(id)`, `open_game(session, code)` (unfinished game for this browser and puzzle or None), `add_word(id, word, points)`, `finish(id)`, `games(name=None, code=None)` newest first, `by_session(session)` unfinished games. Row factory to dicts. `DB_PATH` from the environment, default `data/bee.db`. WAL mode.
Verify: a five line python snippet in the terminal that creates a game, adds two words, finishes it and prints `games()`.

### 3. app.py and templates, playable
Routes exactly as SPEC 4 and 6: `/`, `POST /new`, `/play/<code>`, `POST /guess`, `POST /finish`, `/done/<id>`, `/theme/<name>`, `/admin`, `/admin.csv`. Cookies `session`, `name`, `theme`. Basic auth helper for admin using `ADMIN_PASSWORD`; 503 with a one sentence message when unset. Add the `Content-Security-Policy: frame-ancestors` header from `docs/DEPLOY.md`.
Templates: `base.html` (head, theme attribute on body, nav with theme dropdown), `index.html`, `play.html`, `done.html`, `admin.html`. Render the honeycomb as seven `<button>` elements inside a `.hive` div, the centre with class `centre`, letters as data attributes. Found words as a `<ul>`, score line as a `<p id=score>`, timer as `<span id=timer>` with `data-start` in unix ms.
The one inline script in `play.html`, max 60 lines: click and keyboard input restricted to the puzzle letters, backspace, enter posts to `/guess` with fetch and applies the JSON (message flash, score line, rank, append found word, reset input), shuffle reorders the six outer buttons in place, finish submits a form, timer ticks every second from `data-start`. No other JS anywhere.
Verify: `ADMIN_PASSWORD=x SECRET_KEY=dev flask --app app run` in the background, then with curl: `/` returns 200, `POST /new` with letters redirects to a `/play/` URL, `POST /guess` with a bad word returns JSON with `ok: false` and the right message, with a good word returns `ok: true` and points, `/admin` returns 401 without the password and 200 with it, `/admin.csv` has a header line. Kill the server.

### 4. style.css, layout only, classic theme
The honeycomb with `clip-path` hexagons in three rows (2, 3, 2 with the centre in the middle row), touch targets at least 48 px, board fitting 360 px wide screens, found words beside the board on wide screens and below it on narrow ones, buttons, the rank bar, the admin table. Only the `classic` variables for now, defined on `:root`.
Verify: if a headless browser is available (playwright or chromium), screenshot `/play/<code>` at 390 px and 1200 px widths and look at both. If not, open the page yourself with `python -m webbrowser` and state that you did.

**STOP 1, stylistic checkpoint.** Show me the screenshots or describe the layout, then ask the four questions at the end of `docs/THEMES.md` (centre colour in non classic themes, the set of eight, rank names and messages, board layout). Wait for my answers. Apply them.

### 5. the eight themes
Add the seven remaining `[data-theme]` blocks from `docs/THEMES.md` (as amended by my answers) plus the tiny theme specific touches listed there, all inside the 220 line CSS budget. Theme dropdown on `/` and on the board, persisted in the cookie.
Verify: `wc -l static/style.css` <= 220, each theme renders (screenshots of loveydovey and terminal at least, or a description), `grep -c "data-theme=" static/style.css` is at least 7.

**STOP 2, stylistic checkpoint.** Show the theme screenshots. Ask whether any palette or touch should change. Wait, apply, continue.

### 6. done page and admin polish
`/done/<id>` per SPEC 4 including the reveal toggle (a `<details>` element, no JS). `/admin` per SPEC 6 including the per player summary, filters, Zurich local times, `mm:ss`. `/admin.csv`.
Verify: play a game to completion with curl against a tiny manual puzzle, open `/done/<id>` and `/admin`, check every column has a sensible value.

### 7. docker and deploy files
`Dockerfile` (python:3.12-slim, non root user, gunicorn, `PORT` default 8000), `compose.yaml` (app + caddy, named volume for `data`, env from `.env`), `Caddyfile` for `bee.tafo.ch`. Follow `docs/DEPLOY.md` option A exactly.
Verify: `docker build .` succeeds if docker is available; otherwise `python -c "import yaml"` style syntax check is not needed, just re-read the files carefully and say so.

### 8. readme and final checks
Fill every TODO in `README.md` (short), make sure "decisions" lists all choices you made. Run `pytest -q` once more. Check every budget in `CLAUDE.md` with `wc -l` and paste the numbers into your final message. Grep the whole repo for uppercase letters at the start of comments (`grep -rn "# [A-Z]" --include=*.py`) and for em dashes; fix any hit.

### 9. publish
`gh auth status` must succeed, otherwise stop and tell me how to log in. Then `gh repo create tafo-bee --public --source=. --push --description "spelling bee word game for tafo.ch"`. Print the repository URL, the line counts, and a three line summary of how to run it locally and deploy it.

## defaults you should keep without asking

MIN_WORDS 20, MAX_WORDS 80, ALLOW_S 0, reveal of missed words on, rank thresholds 0 2 5 8 15 25 40 50 70 100, default rank names from SPEC 5 until I change them at STOP 1, repo name `tafo-bee`, licence MIT, admin auth basic with a single password, sqlite at `data/bee.db`, port 8000.
