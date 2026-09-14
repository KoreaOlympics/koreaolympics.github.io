"""Korea-only view: Korean athlete names and data/kor.json."""
import glob, json, pathlib, re

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"


def name_key(s):
    return re.sub(r"[^A-Z]", "", s.upper())


def load_name_map():
    """Romanized -> Hangul names, harvested from the site's own pages ("안세영 (AN Seyoung)", "안세영 <em>AN Seyoung</em>")."""
    pats = [r"([가-힣]{2,5})\s*\(\s*([A-Z][A-Za-z'\- ]{2,40}?)\s*\)", r"([가-힣]{2,5})\s*<em>\s*([A-Z][A-Za-z'\- ]{2,40}?)\s*</em>"]
    names = {}
    for f in glob.glob(str(HERE.parent / "*.html")):
        text = pathlib.Path(f).read_text(encoding="utf-8", errors="ignore")
        for p in pats:
            for hangul, roman in re.findall(p, text):
                if " " in roman.strip() or "-" in roman:
                    names.setdefault(name_key(roman), hangul)
    return names


NAMES = load_name_map()


def athlete_ko(name):
    """"AN Seyoung" -> "안세영"; doubles "KIM A / LEE B" handled per part; unknown names stay romanized."""
    if name in ("Republic of Korea", "Korea"):
        return "대한민국"
    parts = re.split(r"\s*/\s*", name or "")
    return " / ".join(NAMES.get(name_key(p), p) for p in parts)


def involves_kor(u):
    return any(s and s.get("org") == "KOR" for s in (u.get("home"), u.get("away")))


def build():
    """Games where Korea appears in the official draw/start list. Everything else is added by hand in kor_manual.json."""
    items = []
    for f in sorted(glob.glob(str(DATA / "2026-*.json"))):
        date = pathlib.Path(f).stem
        for u in json.loads(pathlib.Path(f).read_text(encoding="utf-8")):
            if involves_kor(u) or "KOR" in (u.get("orgs") or []):
                items.append({**u, "id": f"{date}/{u['disc']}/{u['key']}", "date": date})
    items.sort(key=lambda x: (x["dt"], x["disc"]))
    return items
