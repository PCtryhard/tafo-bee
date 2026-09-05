# bee

A spelling bee word game for tafo.ch. Seven letters in a honeycomb, the centre one is mandatory, words are four letters or longer, as many puzzles as you like.

<!-- agent: replace this file's TODO blocks as you go. keep it short. -->

## play

TODO: one paragraph on rules, scoring, ranks, themes.

## run locally

```
pip install -r requirements.txt
ADMIN_PASSWORD=x SECRET_KEY=dev flask --app app run --debug
```

## deploy

See `docs/DEPLOY.md`. Short version: `docker compose up -d` on a VPS with `bee.tafo.ch` pointed at it.

## admin

`/admin` (basic auth, password from `ADMIN_PASSWORD`) lists every game with player name, puzzle, words found, score, rank and time spent. `/admin.csv` exports the same.

## dictionary

SCOWL British English, see `data/README.md`. Replace `data/words.txt` to change it.

## decisions

<!-- agent: log every non stylistic choice you made that the spec left open, one line each -->

- TODO

## licence

MIT for the code (see `LICENSE`). Word list under the SCOWL licence, see `data/README.md`.
