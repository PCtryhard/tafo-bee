import os, random
from datetime import date
from functools import lru_cache
from itertools import combinations, count
from pathlib import Path

RANKS = ["start", "warming up", "rolling", "sharp", "strong", "brilliant", "expert", "master", "genius", "perfect"]
THRESHOLDS = [0, 2, 5, 8, 15, 25, 40, 50, 70, 100]
PRAISE = [(8, "great"), (5, "nice"), (0, "good")]
DATA = Path(__file__).parent / "data"
MIN_WORDS = int(os.environ.get("MIN_WORDS", 20))
MAX_WORDS = int(os.environ.get("MAX_WORDS", 80))
ALLOW_S = os.environ.get("ALLOW_S", "0") == "1"

@lru_cache
def load_words() -> frozenset[str]:
    read = lambda name: set((DATA / name).read_text().split()) if (DATA / name).exists() else set()
    return frozenset(w for w in read("words.txt") - read("exclude.txt") if len(w) >= 4 and w.isascii() and w.isalpha())

def mask(word: str) -> int:
    return sum(1 << ord(c) - 97 for c in set(word))

@lru_cache
def by_mask() -> dict[int, list[str]]:
    groups: dict[int, list[str]] = {}
    for w in load_words(): groups.setdefault(mask(w), []).append(w)
    return groups

@lru_cache
def candidates() -> list[str]:
    return sorted(w for w in load_words() if len(set(w)) == 7 and (ALLOW_S or "s" not in w))

def clean(letters: str, centre: str) -> tuple[str, str]:
    return "".join(letters.lower().split()), centre.lower().strip()

def canon(letters: str, centre: str) -> str | None:
    letters, centre = clean(letters, centre)
    ok = len(letters) == 7 == len(set(letters)) and letters.isascii() and letters.isalpha() and len(centre) == 1 and centre in letters
    return centre + "".join(sorted(set(letters) - {centre})) if ok else None

def manual(letters: str, centre: str) -> tuple[str | None, str]:
    letters, centre = clean(letters, centre)
    checks = [(len(letters) != 7, "need exactly 7 letters"), (len(set(letters)) != 7, "duplicate letters"),
              (not (letters.isascii() and letters.isalpha()), "letters a to z only"),
              (len(centre) != 1 or centre not in letters, "the centre must be one of the seven letters")]
    if bad := [m for failed, m in checks if failed]:
        return None, bad[0]
    code = canon(letters, centre)
    return (code, "") if len(words_for(code)) >= 5 else (None, "fewer than 5 valid words")

@lru_cache
def words_for(code: str) -> list[str]:
    # every valid word's letter set is one of the 64 subsets of the outer letters plus the centre
    subsets = (code[0] + "".join(c) for r in range(7) for c in combinations(code[1:], r))
    return sorted(w for s in subsets for w in by_mask().get(mask(s), []))

def is_pangram(word: str, code: str) -> bool:
    return set(word) == set(code)

def points(word: str, code: str) -> int:
    return (1 if len(word) == 4 else len(word)) + (7 if is_pangram(word, code) else 0)

@lru_cache
def max_score(code: str) -> int:
    return sum(points(w, code) for w in words_for(code))

def check(word: str, code: str, found: list[str]) -> tuple[bool, str, int]:
    word = word.lower().strip()
    fails = [(len(word) < 4, "too short"), (code[0] not in word, "missing centre letter"), (not set(word) <= set(code), "bad letters"),
             (word in found, "already found"), (word not in words_for(code), "not in word list")]
    if bad := [m for failed, m in fails if failed]:
        return False, bad[0], 0
    p = points(word, code)
    return True, "pangram!" if is_pangram(word, code) else next(m for t, m in PRAISE if p >= t), p

def rank(score: int, code: str) -> str:
    pct = 100 * score / (max_score(code) or 1)
    return [name for t, name in zip(THRESHOLDS, RANKS) if pct >= t][-1]

def random_code(rng: random.Random | None = None) -> str:
    rng, words = rng or random.Random(), candidates()
    for i in count():
        letters = "".join(set(rng.choice(words)))
        code = canon(letters, rng.choice(letters))
        n = len(words_for(code))
        if n >= 10 and (i >= 200 or MIN_WORDS <= n <= MAX_WORDS):
            return code

def daily_code(day: date) -> str:
    return random_code(random.Random(day.isoformat()))
