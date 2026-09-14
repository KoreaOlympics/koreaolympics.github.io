"""Team-sport standings and knockout brackets -> data/brackets.json.

Standings and brackets come from the official groups/brackets feeds; the per-round match list is built
from the daily schedule files, which also covers sports whose bracket feed is empty (hockey, softball...).
To manage another event, add a line to EVENTS.
"""
import glob, json, pathlib, re
from translate import ko, NOC_KO

DATA = pathlib.Path(__file__).parent / "data"

# (discipline, event key, label)
EVENTS = [
    ("FBL", "M.TEAM11------------", "남자 축구"), ("FBL", "W.TEAM11------------", "여자 축구"),
    ("BBL", "M.TEAM9-------------", "야구"), ("SBL", "W.TEAM9-------------", "소프트볼"),
    ("BKB", "M.TEAM5-------------", "남자 농구"), ("BKB", "W.TEAM5-------------", "여자 농구"),
    ("BK3", "M.TEAM3-------------", "남자 3x3 농구"), ("BK3", "W.TEAM3-------------", "여자 3x3 농구"),
    ("VVO", "M.TEAM6-------------", "남자 배구"), ("VVO", "W.TEAM6-------------", "여자 배구"),
    ("HOC", "M.TEAM11------------", "남자 하키"), ("HOC", "W.TEAM11------------", "여자 하키"),
    ("HBL", "M.TEAM7-------------", "남자 핸드볼"), ("HBL", "W.TEAM7-------------", "여자 핸드볼"),
    ("WPO", "M.TEAM7-------------", "남자 수구"), ("WPO", "W.TEAM7-------------", "여자 수구"),
    ("RU7", "M.TEAM7-------------", "남자 7인제 럭비"), ("RU7", "W.TEAM7-------------", "여자 7인제 럭비"),
]

GENDER = re.compile(r"^(남자|여자|혼성)\s*")


def short(name, disc):
    """Drop the gender prefix and the redundant "예선 -": "Men Group Phase - Group A" -> "A조"."""
    s = GENDER.sub("", ko(name, disc))
    s = re.sub(r"^예선\s*-?\s*(?=\S+조$)", "", s).strip() or s
    return "풀리그" if s in ("라운드", "예선") else s


def team(org, name):
    return {"org": org, "name": NOC_KO.get(org, name) if org else ""}


def standings(disc, groups):
    out, names = [], {}
    for g in groups.get("Groups", []):
        comps = g.get("Competitors") or []
        names[g["Key"]] = short(g.get("DescA") or g.get("Desc", ""), disc)
        if g.get("Type") != "POOL" or not comps:
            continue
        rows = []
        for c in sorted(comps, key=lambda c: (c.get("RkPo") or 99, c.get("Pos") or "")):
            rows.append({
                **team(c.get("Org", ""), c.get("Name", "")),
                "rk": c.get("Rk", ""), "p": c.get("Played", ""), "w": c.get("Won", ""), "l": c.get("Lost", ""),
                "t": c.get("Tied", ""), "pts": c.get("Points", ""),
                "pf": c.get("PtsFor", c.get("For", "")), "pa": c.get("PtsAgainst", c.get("Against", "")),
                "diff": c.get("PtsDiff", c.get("Diff", "")), "q": c.get("Qualified", ""),
            })
        out.append({"key": g["Key"], "name": names[g["Key"]], "rows": rows})
    return out, names


def unit_no(key):
    m = re.search(r"\.(\d{6})--$", key or "")
    return int(m.group(1)) // 100 if m else 0


def origin(ext, phase_names):
    """Where a TBD bracket slot comes from: "A조 1위", "8강 2경기 승자"."""
    x = {e["Code"]: e.get("Value") for e in ext or []}
    rank, phase_key, unit_key = x.get("ComesFromRank"), x.get("ComesFromPhaseKey"), x.get("ComesFromUnitKey") or ""
    if not rank:
        return ""
    if unit_key and not unit_key.endswith(".--------"):
        ph = phase_names.get(unit_key.rsplit(".", 1)[0], "")
        return f"{ph} {unit_no(unit_key)}경기 {'승자' if rank == '1' else '패자'}".strip()
    if phase_key in phase_names:
        return f"{phase_names[phase_key]} {rank}위"
    return ""


def source_unit(ext):
    key = {e["Code"]: e.get("Value") for e in ext or []}.get("ComesFromUnitKey") or ""
    return "" if key.endswith(".--------") else key


def bracket(disc, data, phase_names):
    trees = []
    for top in data or []:
        phases = top.get("Phases", [])
        if not phases or sum(len(p.get("Matches", [])) for p in phases) > 16:
            continue  # round-robin "brackets" (e.g. a single 7-team league) are shown as standings instead
        for p in phases:
            phase_names[p["Code"]] = short(p.get("Desc", ""), disc)
        cols = []
        for p in phases:
            matches = []
            for m in p.get("Matches", []):
                info = m.get("Info", {})
                side = lambda s: {**team(s.get("Org", ""), s.get("Name", "")), "res": s.get("Res", ""), "win": s.get("Win", False),
                                  "from": origin(s.get("Extensions"), phase_names), "src": source_unit(s.get("Extensions"))}
                matches.append({"key": info.get("Key", ""), "dt": info.get("DateTimeRaw", ""), "loc": info.get("LocDesc", ""),
                                "status": info.get("Status", ""), "bye": info.get("IsBye", False),
                                "home": side(m.get("Home", {})), "away": side(m.get("Away", {}))})
            cols.append({"code": p["Code"], "name": phase_names[p["Code"]], "matches": matches})
        code = top.get("Code", "")
        title = "결선 토너먼트" if code == "FNL" else "동메달 결정전" if code == "BRN" else short(top.get("Desc", ""), disc)
        trees.append({"title": title, "cols": cols})
    return trees


def schedule_rounds(disc, ev):
    """Every match of the event from the daily files, grouped by round in playing order."""
    rounds = {}
    for f in sorted(glob.glob(str(DATA / "2026-*.json"))):
        for u in json.loads(pathlib.Path(f).read_text(encoding="utf-8")):
            if u["disc"] != disc or u.get("ev") != ev or "Ceremony" in u.get("unitEn", "") or "시상식" in u["phase"]:
                continue
            pkey = u["key"].rsplit(".", 1)[0]
            r = rounds.setdefault(pkey, {"key": pkey, "name": short(u["phase"], "") or u["phase"], "matches": []})
            side = lambda s: s and {"org": s["org"], "name": s.get("nameKo") or s["name"], "res": s.get("result", ""), "win": s.get("win", False)}
            r["matches"].append({"dt": u["dt"], "unit": GENDER.sub("", u["unit"]), "venue": u.get("venue", ""),
                                 "status": u.get("status", ""), "home": side(u.get("home")), "away": side(u.get("away"))})
    out = list(rounds.values())
    for r in out:
        r["matches"].sort(key=lambda m: m["dt"])
    out.sort(key=lambda r: (r["matches"][0]["dt"][:10] if r["matches"] else "", r["name"]))
    return out


def build(get):
    events = []
    for disc, ev, label in EVENTS:
        try:
            groups = get(f"{disc}/groups/{ev}")
        except Exception as e:
            print("  groups fail", disc, ev, e)
            groups = {}
        table, phase_names = standings(disc, groups)
        try:
            tree = bracket(disc, get(f"{disc}/brackets/{ev}"), phase_names)
        except Exception as e:
            print("  bracket fail", disc, ev, e)
            tree = []
        events.append({"disc": disc, "ev": ev, "label": label, "standings": table, "bracket": tree,
                       "rounds": schedule_rounds(disc, ev)})
    (DATA / "brackets.json").write_text(json.dumps(events, ensure_ascii=False), encoding="utf-8")
    return events
