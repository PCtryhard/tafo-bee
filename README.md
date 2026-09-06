# bee

A spelling bee word game for tafo.ch. Seven letters in a honeycomb, the centre one is mandatory, words are four letters or longer, as many puzzles as you like.

## play

Pick a random puzzle, today's puzzle (the same for everyone on a given day) or type your own seven letters and a centre letter. Every word must be four letters or longer, use only the seven letters (repeats allowed) and contain the centre letter. A four letter word scores 1 point, longer words score one point per letter, and a pangram (all seven letters) earns 7 extra. Your rank climbs from start to perfect as your score approaches the puzzle maximum: start, warming up, rolling, sharp, strong, brilliant, expert, master, genius, perfect. Finish a game to see the missed words.

## boards

The theme dropdown picks one of five boards, each with its own layout or mechanics (see `docs/THEMES.md`):

- **classic**: the plain honeycomb, the default.
- **world**: a 3D field of hexagon blocks; walk with wasd or the arrows, jump with space, land on a block to add its letter, jump on ok to send. Trees, bushes, foxes and a lake around it. Touch screens get a d-pad and a jump button.
- **tome**: a pixel art boss fight against an evil dictionary. Steer onto letter tiles and select them with z or space while dodging pages, ink and stray letters. Five hit points, zero ends the game.
- **terminal**: a console. Type a word and press enter, rejected words come back as red error blocks, `Get-Help` lists the commands.
- **loveydovey**: the classic board with pixel 3D hearts laid out as a heart.

## run locally

```
pip install -r requirements.txt
ADMIN_PASSWORD=x SECRET_KEY=dev flask --app app run --debug
```

## deploy

See `docs/DEPLOY.md`. Short version: `docker compose up -d` on a VPS with `bee.tafo.ch` pointed at it.

## stats

`/stats` is public. It lists the best attempt on every puzzle (most words, then fastest), sortable by words or time, and opens to show every attempt with the player names. The section at the top is personal: the games played in this browser, the dailies played and the current daily streak, all found through the session cookie.

## admin

`/admin` (basic auth, password from `ADMIN_PASSWORD`) lists every game with player name, puzzle, words found, score, rank and time spent. `/admin.csv` exports the same.

## dictionary

SCOWL British English, see `data/README.md`. Replace `data/words.txt` to change it. Put unwanted words (the list includes oddities such as `viii`) in `data/exclude.txt`, one per line.

## decisions

- `tzdata` added to `requirements.txt`: Python's zoneinfo needs it for `Europe/Zurich` on Windows and in slim Docker images.
- The theme selector is a `<details>` menu of links to `/theme/<name>`, so it needs no script outside `play.html`.
- The name field is always shown on `/`, prefilled from the cookie, so a player can change their name.
- `/guess` returns an extra `done` flag so the board can redirect to the summary when the last word is found.
- Acceptance copy thresholds: `good` under 5 points, `nice` 5 to 7, `great` 8 and up, `pangram!` for pangrams.
- Hexagon fill is painted by a pseudo element inset by 1 px so a theme can set `--edge` for a visible border (terminal).
- Shuffle swaps the letters between the six outer buttons instead of moving DOM nodes, as the honeycomb is positioned by child index.
- Words are stored sorted in the database so the list is alphabetical without sorting at read time.
- `/done/<id>` of an unfinished game redirects to the board instead of finishing it.
- `/theme/<name>` returns to the `next` query path only when it is a local path.
- The manual letters field accepts spaces and any case, cleaned before validation.
- Puzzle solving groups the dictionary by letter set once, so `words_for` is 64 dictionary lookups rather than a scan.
- The sqlite volume is mounted at `/data` with `DB_PATH=/data/bee.db` so it does not hide `data/words.txt` inside the image.
- `.dockerignore` added to keep the venv, git history, tests and local databases out of the image.
- `pytest` is cut from the image install by dropping everything below the `# dev` marker in `requirements.txt`.
- `templates/stats.html` added for the public leaderboard and personal history page, requested after the first release.
- Personal history on `/stats` is keyed on the session cookie, not the name, so two players with the same nickname stay apart; clearing cookies starts a fresh history.
- A daily streak counts consecutive days with a game on that day's daily code, and survives until the end of the next day.
- The daily puzzle now uses the Zurich date rather than the server's local date.
- Themes became modes: every mode owns `templates/play_<mode>.html` and `static/<mode>.css`, selected by name in `play()`; the six palette themes were deleted and `classic` stays the default and fallback.
- world: only a jump produces a landing event, and the gaps between letter blocks are bridged in the hit test (each hexagon counts 7 px wider), so walking across the honeycomb never drops or adds letters; walking off the outer edge still drops.
- tome: the book uses a little yellow for the gilt page edges and red for the ribbon, on top of the palette rule, because an old bible needs both; every face change, the opening of an attack and the slam draw four ghost copies for a smear frame.
- world: hexagon tops and the lake are inline SVG polygons, not `clip-path`, because Chrome drops clipped faces from 3D depth sorting and the centre's walls were painting over its neighbours.
- world: blocks keep a 7 px gap so their walls read as separate prisms; a tree is three stacked prisms, a fox three small ones on a keyframe path.
- world: the camera is a plain 56 degree tilt with no turn, the ground is finite at about 920 by 570 world px with the horizon a little below the HUD, as chosen at the checkpoint.
- tome: the open book rows are generated by four lines of script instead of typed out, and the face is drawn with rectangles on top; the other sprites are literal string arrays.
- tome: touch controls sit in a bar under the canvas rather than over it, so the whole box stays visible on a phone.
- terminal: the prompt accepts every letter plus the hyphen, because commands need letters outside the puzzle; the server still answers `bad letters` with a red block for guesses.
- loveydovey: hearts are pixel polygons with a darker offset copy behind them for the 3D look; the floating hearts replay only when the message state changes.
- Chrome cannot render a headless window under about 500 px, so the 390 px layout was checked in an emulated mobile viewport instead.

## licence

MIT for the code (see `LICENSE`). Word list under the SCOWL licence, see `data/README.md`.
