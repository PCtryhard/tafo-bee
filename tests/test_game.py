import random
from datetime import date

import game

CODE = "bdeikln"


def test_canon():
    assert game.canon("blinked", "b") == CODE
    assert game.canon("KLINDEB", "B") == CODE
    assert game.canon("blinked", "x") is None
    assert game.canon("blinkedd", "b") is None
    assert game.canon("blinke", "b") is None
    assert game.canon("blink3d", "b") is None
    assert game.canon("blinked", "") is None


def test_manual_messages():
    assert game.manual("blinked", "b") == (CODE, "")
    assert game.manual("blinke", "b")[1] == "need exactly 7 letters"
    assert game.manual("bliinkd", "b")[1] == "duplicate letters"
    assert game.manual("blink3d", "b")[1] == "letters a to z only"
    assert game.manual("blinked", "z")[1] == "the centre must be one of the seven letters"
    assert game.manual("qxzjvwk", "q")[1] == "fewer than 5 valid words"


def test_words_for():
    words = game.words_for(CODE)
    assert words == sorted(words) and len(words) == 43
    assert "blinked" in words and all(len(w) >= 4 and "b" in w and set(w) <= set(CODE) for w in words)


def test_check_priority():
    assert game.check("bin", CODE, []) == (False, "too short", 0)
    assert game.check("linked", CODE, []) == (False, "missing centre letter", 0)
    assert game.check("blinks", CODE, []) == (False, "bad letters", 0)
    assert game.check("bike", CODE, ["bike"]) == (False, "already found", 0)
    assert game.check("bnik", CODE, []) == (False, "not in word list", 0)
    assert game.check("bnk", CODE, ["bnk"]) == (False, "too short", 0)
    assert game.check(" Bike ", CODE, []) == (True, "good", 1)
    assert game.check("blinked", CODE, []) == (True, "pangram!", 14)


def test_points():
    assert game.points("bike", CODE) == 1
    assert game.points("biked", CODE) == 5
    assert game.points("blinked", CODE) == 14
    assert game.is_pangram("blinked", CODE) and not game.is_pangram("biked", CODE)
    assert game.max_score(CODE) == sum(game.points(w, CODE) for w in game.words_for(CODE))


def test_rank_thresholds():
    top = game.max_score(CODE)
    assert game.rank(0, CODE) == "start"
    assert game.rank(top, CODE) == "perfect"
    assert game.rank(top - 1, CODE) == "genius"
    for pct, name in zip(game.THRESHOLDS, game.RANKS):
        assert game.rank(-(-pct * top // 100), CODE) == name


def acceptable(code: str) -> bool:
    n = len(game.words_for(code))
    return game.MIN_WORDS <= n <= game.MAX_WORDS and any(game.is_pangram(w, code) for w in game.words_for(code))


def test_random_codes():
    rng = random.Random(42)
    for _ in range(100):
        code = game.random_code(rng)
        assert game.canon(code, code[0]) == code and acceptable(code)
        assert game.ALLOW_S or "s" not in code


def test_daily_stable():
    day = date(2026, 9, 5)
    assert game.daily_code(day) == game.daily_code(day) and acceptable(game.daily_code(day))
    assert game.daily_code(day) != game.daily_code(date(2026, 9, 6))
