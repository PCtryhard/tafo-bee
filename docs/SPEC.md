# bee: functional specification

Everything here is a requirement unless marked *default* (a chosen value the agent may keep without asking) or *stylistic* (confirm with Max).

## 1. the puzzle

- Seven distinct letters a to z. One is the **centre** letter, six are **outer** letters.
- A puzzle is identified by its **code**: 7 lowercase letters, centre first, the six outer letters sorted. Example: centre `b` with `l,i,n,k,e,d` gives `bdeikln` (43 words with the shipped dictionary, pangram `blinked`). Codes are canonical, so the same puzzle always has the same URL `/play/bdeikln`.
- Valid words for a puzzle: every dictionary word that
  1. is 4 or more letters long (the dictionary is already filtered, still check),
  2. uses only the seven letters (letters may repeat any number of times),
  3. contains the centre letter at least once.
- A **pangram** is a valid word that uses all seven letters.
- A puzzle is **acceptable** when its valid word count lies within `[MIN_WORDS, MAX_WORDS]` (*default* 20 and 80) and it has at least one pangram.
- *Default*: the letter `s` is excluded from generated puzzles (`ALLOW_S=0`) to avoid trivial plurals. Manual puzzles may include `s`.

## 2. creating puzzles

Three entry points, all landing on `/play/<code>`:

1. **random**: pick a random pangram candidate (dictionary word with exactly 7 distinct letters), pick a random one of its letters as centre, accept if acceptable, otherwise retry. Cap retries at 200 then relax to any candidate with >= 10 words. Must finish in well under a second.
2. **daily**: same as random but seeded with the ISO date (`random.Random("2026-09-05")`). Deterministic per day, unlimited replays.
3. **manual**: a form on `/` with two fields, the seven letters and the centre letter (must be one of the seven). Validation errors shown inline: not 7 letters, duplicate letters, non a to z, fewer than 5 valid words. Manual puzzles skip the MIN/MAX check apart from the >= 5 floor, so the boss can set up anything he likes.

Puzzle solving (`words_for(code)`) is a filter over the loaded word set and is cached with `lru_cache`.

## 3. dictionary

- `data/words.txt`: SCOWL British English (size 50, the Debian `wbritish` package, release 2020.12.07), filtered to `^[a-z]{4,}$`, sorted, deduplicated. 62 700 words. Regenerate with `tools/build_dict.sh`. Attribution and licence in `data/README.md`.
- `data/exclude.txt` (optional, one word per line): subtracted at load. Empty in the repo. This is where offensive or unwanted words go later.
- Loading is a single function in `game.py` returning a `frozenset`. Swapping in a licensed Oxford list later means replacing `data/words.txt` and nothing else.

## 4. play

- `GET /`: if no `name` cookie, a name field (required, 1 to 24 characters, trimmed). Then three actions: random puzzle, today's puzzle, manual letters form. Theme selector (section 7). Optional list of the player's unfinished games from the cookie session to resume.
- `GET /play/<code>`: renders the board. Creates a game row for (session, code) if there is no unfinished one, otherwise resumes it. 404 with a plain message on an invalid code.
- Board: the honeycomb of 7 hexagons, centre highlighted, outer six around it. Below or beside it: the current input line, buttons **delete**, **shuffle** (reorders the six outer letters), **enter**, plus **finish**. Score, rank, word count `n / total`, and a live timer.
- Input: clicking a hexagon appends its letter; typing on the keyboard does the same; Backspace deletes; Enter submits. Only letters of the puzzle are accepted into the input; others are ignored.
- `POST /guess` JSON `{game, word}` responds `{ok, msg, points, score, rank, found, elapsed}`. Rejection messages, in this priority order: `too short`, `missing centre letter`, `bad letters`, `already found`, `not in word list`. Acceptance messages: `pangram!` for pangrams, otherwise `good` / `nice` / `great` by points (*stylistic* copy).
- Found words are listed alphabetically, pangrams marked.
- `POST /finish` marks the game finished and redirects to `/done/<game_id>`.
- `GET /done/<game_id>`: summary. Words found, score, rank, time, number missed. A **reveal** toggle shows the missed words (*default* on, the boss may want it for teaching). Buttons: play again (same code, new game), new random, home.
- Reaching all words auto finishes.

## 5. scoring and ranks

- 4 letter word: 1 point. Longer word: 1 point per letter. Pangram: +7 bonus.
- Max score = sum over all valid words.
- Rank thresholds as a percentage of max score, *default*: 0, 2, 5, 8, 15, 25, 40, 50, 70, 100. Ten ranks.
- Rank names are *stylistic*. Default set, in order: `start, warming up, rolling, sharp, strong, brilliant, expert, master, genius, perfect`. Do not copy the NYT names.

## 6. activity and performance tracking (boss requirement)

Table `games` in sqlite (`DB_PATH`, *default* `data/bee.db`):

| column | type | meaning |
|---|---|---|
| id | text pk | 12 char random token, used in URLs |
| session | text | random cookie token identifying the browser |
| name | text | player name from the cookie |
| code | text | puzzle code |
| theme | text | theme active when the game started |
| started | real | unix time the board was first opened |
| last | real | unix time of the last accepted word |
| finished | real or null | unix time of finish |
| words | text | json list of found words |
| score | int | current score |

Derived, computed in Python, never stored: `elapsed = (finished or last) - started` in seconds (time spent), `found = len(words)`, `total = len(words_for(code))`, `pct = score / max_score`.

Timer shown to the player counts from `started` live in the browser; the authoritative value is the server one.

`GET /admin`, protected by HTTP basic auth (any user, password `ADMIN_PASSWORD` env; 503 with a plain message if the variable is unset):

- One table, newest first: name, puzzle code (link to play it), started (local time, Europe/Zurich), finished yes/no, words found / total, score / max, rank, time spent `mm:ss`.
- Above it, a per player summary: games, finished games, total words, average pct, total time.
- `GET /admin.csv`: the same rows as CSV for spreadsheets.
- Filters: `?name=` and `?code=` query params, exact match. Nothing fancier.

Sessions and names are cookies, `SameSite=Lax`, 1 year. No accounts, no passwords for players.

## 7. themes

Eight themes selectable from a dropdown on `/` and from a small control on the board, stored in a `theme` cookie, applied as `<body data-theme="...">`. Each theme is a block of CSS custom properties in `static/style.css`, nothing else changes between themes. Palettes and details are in `docs/THEMES.md` and are *stylistic*. Names, fixed: `classic, loveydovey, midnight, forest, ocean, terminal, newsprint, candy`.

The centre hexagon is yellow in `classic` and *default* yellow family in all themes; `THEMES.md` lists the proposed exceptions for confirmation.

## 8. non functional

- Everything server side is Python. The browser gets rendered HTML, one CSS file, and one inline script of at most 60 lines handling: hex clicks, keyboard input, shuffle, delete, submit via `fetch`, updating the score line and found list from the JSON response, and the ticking timer.
- Works without cookies enabled for playing a single game (name defaults to `anon`), degrades gracefully.
- Mobile first: the board fits a 360 px wide screen, hexagons are touch targets of at least 48 px.
- Config via environment: `SECRET_KEY`, `ADMIN_PASSWORD`, `DB_PATH`, `MIN_WORDS`, `MAX_WORDS`, `ALLOW_S`, `PORT`.
- `pytest -q` passes. Tests cover: code canonicalisation, word validation rules in priority order, scoring including pangram bonus, rank thresholds, random and daily generation producing acceptable puzzles, daily determinism.
- Startup under one second, `/guess` under 20 ms after warmup.
