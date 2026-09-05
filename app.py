import csv, io, os, secrets
from datetime import date, datetime
from zoneinfo import ZoneInfo
from flask import Flask, Response, jsonify, redirect, render_template, request, url_for
import game, store

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
THEMES = ["classic", "loveydovey", "midnight", "forest", "ocean", "terminal", "newsprint", "candy", "sunset"]
ZURICH = ZoneInfo("Europe/Zurich")
YEAR = 365 * 24 * 3600
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
    elapsed = (gm["finished"] or gm["last"]) - gm["started"]
    return {**gm, "total": len(words), "max": top, "pct": gm["score"] / (top or 1), "rank": game.rank(gm["score"], gm["code"]),
            "elapsed": elapsed, "time": mmss(elapsed), "missed": [w for w in words if w not in gm["words"]],
            "local": datetime.fromtimestamp(gm["started"], ZURICH).strftime("%d.%m.%Y %H:%M")}

def with_cookie(resp: Response, name: str, value: str) -> Response:
    resp.set_cookie(name, value, max_age=YEAR, samesite="Lax")
    return resp

@app.after_request
def headers(resp: Response) -> Response:
    resp.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://tafo.ch https://www.tafo.ch"
    if getattr(request, "session", None) and request.session != cookie("session"):
        with_cookie(resp, "session", request.session)
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
    makers = {"daily": lambda: (game.daily_code(date.today()), ""), "manual": lambda: game.manual(f.get("letters", ""), f.get("centre", ""))}
    code, error = makers.get(action, lambda: (game.random_code(), ""))()
    if error:
        return render_template("index.html", open=[], error=error, form=f)
    return with_cookie(redirect(url_for("play", code=code)), "name", name)

@app.route("/play/<code>")
def play(code: str) -> str | tuple[str, int]:
    if game.canon(code, code[:1]) != code or not game.words_for(code):
        return "no such puzzle", 404
    gm = store.open_game(session(), code) or store.get(store.new_game(session(), cookie("name") or "anon", code, theme()))
    return render_template("play.html", gm=enrich(gm))

@app.post("/guess")
def guess() -> Response:
    d = request.get_json(silent=True) or {}
    gm = store.get(str(d.get("game", "")))
    if not gm or gm["finished"]:
        return jsonify(ok=False, msg="this game is over", points=0)
    word = str(d.get("word", "")).lower().strip()
    ok, msg, pts = game.check(word, gm["code"], gm["words"])
    if ok:
        store.add_word(gm["id"], word, pts)
        gm = store.get(gm["id"])
    done = len(gm["words"]) == len(game.words_for(gm["code"]))
    if done:
        store.finish(gm["id"])
    e = enrich(gm)
    return jsonify(ok=ok, msg=msg, points=pts, score=gm["score"], rank=e["rank"], found=gm["words"], elapsed=e["elapsed"], done=done)

@app.post("/finish")
def finish() -> Response | tuple[str, int]:
    id = request.form.get("game", "")
    if not store.get(id):
        return "no such game", 404
    store.finish(id)
    return redirect(url_for("done", id=id))

@app.route("/done/<id>")
def done(id: str) -> str | Response | tuple[str, int]:
    gm = store.get(id)
    if not gm:
        return "no such game", 404
    return render_template("done.html", gm=enrich(gm)) if gm["finished"] else redirect(url_for("play", code=gm["code"]))

@app.route("/theme/<name>")
def set_theme(name: str) -> Response | tuple[str, int]:
    if name not in THEMES:
        return "no such theme", 404
    nxt = request.args.get("next", "/")
    return with_cookie(redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else "/"), "theme", name)

def admin_block() -> Response | None:
    pw = os.environ.get("ADMIN_PASSWORD")
    if not pw:
        return Response("admin is disabled until ADMIN_PASSWORD is set.", 503, mimetype="text/plain")
    auth = request.authorization
    if not auth or auth.password != pw:
        return Response("password needed", 401, {"WWW-Authenticate": 'Basic realm="bee admin"'}, mimetype="text/plain")
    return None

def filtered() -> list[dict]:
    return [enrich(x) for x in store.games(request.args.get("name") or None, request.args.get("code") or None)]

@app.route("/admin")
def admin() -> str | Response:
    if block := admin_block():
        return block
    rows, players = filtered(), {}
    for r in rows:
        p = players.setdefault(r["name"], {"games": 0, "finished": 0, "words": 0, "pct": 0.0, "time": 0.0})
        p.update(games=p["games"] + 1, finished=p["finished"] + bool(r["finished"]), words=p["words"] + len(r["words"]),
                 pct=p["pct"] + r["pct"], time=p["time"] + r["elapsed"])
    return render_template("admin.html", rows=rows, players=players, mmss=mmss)

@app.route("/admin.csv")
def admin_csv() -> Response:
    if block := admin_block():
        return block
    out, head = io.StringIO(), ["name", "code", "started", "finished", "found", "total", "score", "max", "rank", "time"]
    rows = [[r["name"], r["code"], r["local"], "yes" if r["finished"] else "no", len(r["words"]), r["total"], r["score"], r["max"], r["rank"], r["time"]] for r in filtered()]
    csv.writer(out).writerows([head] + rows)
    return Response(out.getvalue(), mimetype="text/csv")
