import csv, io, os, secrets
from datetime import date, datetime, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo
from flask import Flask, Response, jsonify, redirect, render_template, request, url_for
import game, store

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
THEMES = ["classic", "world", "tome", "terminal", "loveydovey", "zen"]
ZURICH = ZoneInfo("Europe/Zurich")
YEAR = 365 * 24 * 3600
daily = lru_cache(game.daily_code)
store.init()

def cookie(name: str, default: str = "") -> str:
    return request.cookies.get(name, default)

def theme() -> str:
    return cookie("theme") if cookie("theme") in THEMES else "classic"

def session() -> str:
    request.session = getattr(request, "session", None) or cookie("session") or secrets.token_urlsafe(12)
    return request.session

def mmss(seconds: float) -> str:
    return f"{int(seconds) // 60:02d}:{int(seconds) % 60:02d}"

def enrich(gm: dict) -> dict:
    words, top = game.words_for(gm["code"]), game.max_score(gm["code"])
    elapsed, day = (gm["finished"] or gm["last"]) - gm["started"], datetime.fromtimestamp(gm["started"], ZURICH).date()
    return {**gm, "total": len(words), "max": top, "pct": gm["score"] / (top or 1), "rank": game.rank(gm["score"], gm["code"]),
            "elapsed": elapsed, "time": mmss(elapsed), "missed": [w for w in words if w not in gm["words"]], "day": day,
            "daily": gm["code"] == daily(day), "local": datetime.fromtimestamp(gm["started"], ZURICH).strftime("%d.%m.%Y %H:%M")}

def with_cookie(resp: Response, name: str, value: str) -> Response:
    resp.set_cookie(name, value, max_age=YEAR, samesite="Lax")
    return resp

@app.after_request
def headers(resp: Response) -> Response:
    resp.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://tafo.ch https://www.tafo.ch"
    if getattr(request, "session", None) and request.session != cookie("session"): with_cookie(resp, "session", request.session)
    return resp

@app.context_processor
def template_globals() -> dict:
    return {"theme": theme(), "themes": THEMES, "name": cookie("name"), "is_pangram": game.is_pangram}

@app.route("/")
def index() -> str:
    return render_template("index.html", open=[enrich(x) for x in store.by_session(cookie("session"))])

@app.post("/new")
def new() -> Response | str:
    f, action = request.form, request.form.get("action", "random")
    name = f.get("name", "").strip()[:24] or cookie("name") or "anon"
    makers = {"daily": lambda: (daily(datetime.now(ZURICH).date()), ""), "manual": lambda: game.manual(f.get("letters", ""), f.get("centre", ""))}
    code, error = makers.get(action, lambda: (game.random_code(), ""))()
    if error: return render_template("index.html", open=[], error=error, form=f)
    return with_cookie(redirect(url_for("play", code=code)), "name", name)

@app.route("/play/<code>")
def play(code: str) -> str | tuple[str, int]:
    if game.canon(code, code[:1]) != code or not game.words_for(code): return "no such puzzle", 404
    gm = store.open_game(session(), code) or store.get(store.new_game(session(), cookie("name") or "anon", code, theme()))
    return render_template([f"play_{theme()}.html", "play.html"], gm=enrich(gm))

@app.post("/guess")
def guess() -> Response:
    d = request.get_json(silent=True) or {}
    gm, word = store.get(str(d.get("game", ""))), str(d.get("word", "")).lower().strip()
    if not gm or gm["finished"]: return jsonify(ok=False, msg="this game is over", points=0)
    ok, msg, pts = game.check(word, gm["code"], gm["words"])
    if ok: store.add_word(gm["id"], word, pts)
    gm = store.get(gm["id"])
    done = len(gm["words"]) == len(game.words_for(gm["code"]))
    if done: store.finish(gm["id"])
    e = enrich(gm)
    return jsonify(ok=ok, msg=msg, points=pts, score=gm["score"], rank=e["rank"], found=gm["words"], elapsed=e["elapsed"], done=done)

@app.post("/finish")
def finish() -> Response | tuple[str, int]:
    id = request.form.get("game", "")
    store.finish(id)
    return redirect(url_for("done", id=id)) if store.get(id) else ("no such game", 404)

@app.route("/done/<id>")
def done(id: str) -> str | Response | tuple[str, int]:
    if not (gm := store.get(id)): return "no such game", 404
    return render_template("done.html", gm=enrich(gm)) if gm["finished"] else redirect(url_for("play", code=gm["code"]))

@app.route("/theme/<name>")
def set_theme(name: str) -> Response | tuple[str, int]:
    if name not in THEMES: return "no such theme", 404
    return with_cookie(redirect(n if (n := request.args.get("next", "/")).startswith("/") and not n.startswith("//") else "/"), "theme", name)

def streak(mine: list[dict]) -> int:
    # consecutive days with a daily game, ending today or yesterday
    days, day, n = {r["day"] for r in mine if r["daily"]}, datetime.now(ZURICH).date(), 0
    if day not in days: day -= timedelta(days=1)
    while day in days: n, day = n + 1, day - timedelta(days=1)
    return n

@app.route("/stats")
def stats() -> str:
    rows, by_code = [enrich(x) for x in store.games()], {}
    for r in rows: by_code.setdefault(r["code"], []).append(r)
    order = lambda r: (-len(r["words"]), r["elapsed"])
    tops = [{"code": c, "runs": sorted(rs, key=order), "best": min(rs, key=order)} for c, rs in by_code.items()]
    by_time = request.args.get("sort") == "time"
    key = (lambda t: (not t["best"]["words"], t["best"]["elapsed"])) if by_time else (lambda t: order(t["best"]))
    mine = [r for r in rows if r["session"] == cookie("session")]
    return render_template("stats.html", tops=sorted(tops, key=key), mine=mine, streak=streak(mine), by_time=by_time)

def admin_block() -> Response | None:
    pw, auth = os.environ.get("ADMIN_PASSWORD"), request.authorization
    if not pw: return Response("admin is disabled until ADMIN_PASSWORD is set.", 503, mimetype="text/plain")
    if not auth or auth.password != pw: return Response("password needed", 401, {"WWW-Authenticate": 'Basic realm="bee admin"'}, mimetype="text/plain")

def filtered() -> list[dict]:
    return [enrich(x) for x in store.games(request.args.get("name") or None, request.args.get("code") or None)]

@app.route("/admin")
def admin() -> str | Response:
    if block := admin_block(): return block
    rows, players = filtered(), {}
    for r in rows:
        p = players.setdefault(r["name"], {"games": 0, "finished": 0, "words": 0, "pct": 0.0, "time": 0.0})
        p.update(games=p["games"] + 1, finished=p["finished"] + bool(r["finished"]), words=p["words"] + len(r["words"]),
                 pct=p["pct"] + r["pct"], time=p["time"] + r["elapsed"])
    return render_template("admin.html", rows=rows, players=players, mmss=mmss)

@app.route("/admin.csv")
def admin_csv() -> Response:
    if block := admin_block(): return block
    out, head = io.StringIO(), ["name", "code", "started", "finished", "found", "total", "score", "max", "rank", "time"]
    rows = [[r["name"], r["code"], r["local"], "yes" if r["finished"] else "no", len(r["words"]), r["total"], r["score"], r["max"], r["rank"], r["time"]] for r in filtered()]
    csv.writer(out).writerows([head] + rows)
    return Response(out.getvalue(), mimetype="text/csv")
