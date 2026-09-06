# bee: themes are modes

Rule: a new theme must change the layout or the mechanics of the board. A palette swap is not a theme and will not be accepted.

## how a mode is wired

- `app.py` keeps the list `THEMES`. The theme cookie selects one, unknown values fall back to `classic`.
- `/play/<code>` renders `templates/play_<theme>.html` if it exists, otherwise `templates/play.html` (the classic board).
- `base.html` links `static/style.css` and, for every mode except classic, `static/<theme>.css` after it.
- Every mode keeps the same ids so the shared pieces work unchanged: `word`, `msg`, `score`, `fill`, `timer`, `found`, and `data-game` on the wrapper. Every mode talks to the same `POST /guess` and gets the same answer `{ok, msg, points, score, rank, found, elapsed, done}`.
- `game.py`, `store.py`, the stats and the admin pages know nothing about modes. The theme name is stored with the game for the admin table only.

## the six boards

| mode | what changes | files |
|---|---|---|
| classic | the plain honeycomb, the default and the fallback | `play.html`, `style.css` |
| world | a 3D field of hexagon blocks seen from the front, a small character walks and jumps, landing on a block adds its letter, trees, bushes, two foxes and a lake around it, d-pad and jump button on touch screens | `play_world.html`, `world.css` |
| tome | a pixel art boss fight on one canvas: a scowling open dictionary throws pages, ink and stray letters into a box while you steer onto letter tiles, five hit points, zero ends the game | `play_tome.html`, `tome.css` |
| terminal | the whole board is a console: a prompt, PowerShell style red error blocks for rejected words, verb-noun commands (`Get-Found`, `Clear-Host`, `Shuffle-Hive`, `Exit-Game`, `Get-Help`), a rain of glyphs behind the panel | `play_terminal.html`, `terminal.css` |
| loveydovey | the classic mechanics with pixel 3D hearts laid out as one big heart, a rose centre, hearts that beat when pressed and float up on an accepted word | `play_loveydovey.html`, `loveydovey.css` |
| zen | the classic layout in grey with stepped pixel hexagons over a full screen pixel canvas of the steppe: a deep blue sky, a bank of cumulus along the horizon, a bright meadow with pale patches and tall grass swept by gusts running left to right, continuous and without interruption | `play_zen.html`, `zen.css` |

## budgets

See the table in `CLAUDE.md`. Every mode has its own script and stylesheet cap, still vanilla JS, no libraries, no build step, no CDN, no web fonts.
