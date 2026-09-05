import json, os, secrets, sqlite3, time
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", str(Path(__file__).parent / "data" / "bee.db"))
SCHEMA = """CREATE TABLE IF NOT EXISTS games (
    id text PRIMARY KEY, session text, name text, code text, theme text,
    started real, last real, finished real, words text, score integer)"""


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = lambda cur, row: {d[0]: v for d, v in zip(cur.description, row)}
    con.execute("PRAGMA journal_mode=WAL")
    return con


def init() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.execute(SCHEMA)


def run(sql: str, *args: object) -> list[dict]:
    with connect() as con:
        return con.execute(sql, args).fetchall()


def row(r: dict | None) -> dict | None:
    return {**r, "words": json.loads(r["words"])} if r else None


def new_game(session: str, name: str, code: str, theme: str) -> str:
    id, now = secrets.token_urlsafe(9), time.time()
    run("INSERT INTO games VALUES (?,?,?,?,?,?,?,NULL,'[]',0)", id, session, name, code, theme, now, now)
    return id


def get(id: str) -> dict | None:
    return row(next(iter(run("SELECT * FROM games WHERE id=?", id)), None))


def open_game(session: str, code: str) -> dict | None:
    return row(next(iter(run("SELECT * FROM games WHERE session=? AND code=? AND finished IS NULL ORDER BY started DESC", session, code)), None))


def add_word(id: str, word: str, points: int) -> None:
    g = get(id)
    words = json.dumps(sorted(g["words"] + [word]))
    run("UPDATE games SET words=?, score=score+?, last=? WHERE id=?", words, points, time.time(), id)


def finish(id: str) -> None:
    run("UPDATE games SET finished=? WHERE id=? AND finished IS NULL", time.time(), id)


def games(name: str | None = None, code: str | None = None) -> list[dict]:
    where = " AND ".join(f"{k}=?" for k, v in (("name", name), ("code", code)) if v) or "1"
    return [row(r) for r in run(f"SELECT * FROM games WHERE {where} ORDER BY started DESC", *[v for v in (name, code) if v])]


def by_session(session: str) -> list[dict]:
    return [row(r) for r in run("SELECT * FROM games WHERE session=? AND finished IS NULL ORDER BY started DESC", session)]
