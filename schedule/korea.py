"""Korea-only view: Korean athlete names and data/kor.json."""
import datetime, glob, json, pathlib, re

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
JST = datetime.timezone(datetime.timedelta(hours=9))


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


def kor_athletes(get, disc):
    """Event key -> Korean athlete names entered for that event."""
    try:
        data = get(f"{disc}/entries/org/KOR")
    except Exception as e:
        print("  entries fail", disc, e)
        return {}
    return {ev["EvKey"]: [athlete_ko(p.get("Name", "")) for p in ev.get("Partics", []) if not p.get("hasMembers")]
            for ev in data.get("Events", [])}


TEAM_DISCS = {"FBL", "BKB", "BK3", "VVO", "VBV", "HOC", "HBL", "WPO", "RU7", "BBL", "SBL", "KAB", "CKT", "SPK", "TEQ"}


def load_entries(get=None, refresh=False):
    """Korean entries per discipline, cached in data/kor_entries.json (refreshed on full runs)."""
    path = DATA / "kor_entries.json"
    if get and (refresh or not path.exists()):
        discs = [d if isinstance(d, str) else d.get("Key") for d in get("ALL/disc/list")]
        out = {}
        for d in discs:
            ev = kor_athletes(get, d)
            if ev:
                out[d] = ev
        path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def session_id(item):
    """Parts of one session (modern pentathlon semi-final A: fencing, obstacle, swim, laser run) share a start list."""
    parts = item["key"].split(".")
    return f"{item['date']}/{item['disc']}/{'.'.join(parts[:-1])}.{parts[-1][:4]}"


def apply_start_lists(get, items, days=1, limit=120):
    """Entries name every Korean in the event, but a later round only has those who advanced, split across heats or
    semi-finals. Each unit's official start list fixes that: athletes becomes the Koreans actually in it, and "lineup"
    says where the names came from ("start", "none" = no Korean in it, "entries" = start list not out yet).
    Cached in data/kor_startlists.json; finished units are not refetched. days=None looks at every day up to tomorrow."""
    path = DATA / "kor_startlists.json"
    try:
        cache = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
    today = datetime.datetime.now(JST).date()
    hi = str(today + datetime.timedelta(days=days or 1))
    lo = str(today - datetime.timedelta(days=days)) if days is not None else ""
    calls = 0
    for x in items:
        if x.get("home") or x.get("away"):
            continue
        sid = session_id(x)
        c = cache.get(sid)
        if get and lo <= x["date"] <= hi and calls < limit and not (c and c["final"]):
            calls += 1
            try:
                d = get(f"{x['disc']}/results/{(x.get('keys') or [x['key']])[0]}")
            except Exception as e:
                print("  start list fail", sid, e)
                d = None
            comps = (d or {}).get("Competitors") or []
            if comps:
                kor = [p for p in comps if p.get("Org") == "KOR"]
                # a team competitor is named after its country; its members aren't listed, so keep the entries then
                names = [athlete_ko(p.get("Name", "")) for p in kor if p.get("Name") != p.get("OrgDesc")]
                c = cache[sid] = {"athletes": names, "team": len(kor) > len(names),
                                  "final": "Official" in ((d.get("Info") or {}).get("StatusDesc") or "")}
        if not c:
            x["lineup"] = "entries"
        elif c["athletes"] or c["team"]:
            x["lineup"] = "start"
            x["athletes"] = c["athletes"] or x["athletes"]
        else:
            x["lineup"] = "none"
            x["athletes"] = []
    if get:
        path.write_text(json.dumps(cache, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        print("start lists fetched", calls)


def build(get=None, refresh_entries=False, start_days=1):
    """Korea's games: every unit where Korea appears in the official draw/start list, every medal-deciding unit of an
    event Korea is entered in, and anything named in kor_manual.json "include" (ID prefixes like "2026-09-16/MPN").
    Multi-part sessions (e.g. modern pentathlon semi-final A) collapse into one row."""
    try:
        manual = json.loads((HERE / "kor_manual.json").read_text(encoding="utf-8"))
    except Exception:
        manual = {}
    include = [p for p in manual.get("include", []) if p]
    entries = load_entries(get, refresh_entries)
    items, sessions = [], {}
    for f in sorted(glob.glob(str(DATA / "2026-*.json"))):
        date = pathlib.Path(f).stem
        for u in json.loads(pathlib.Path(f).read_text(encoding="utf-8")):
            uid = f"{date}/{u['disc']}/{u['key']}"
            if involves_kor(u) or "KOR" in (u.get("orgs") or []):
                items.append({**u, "id": uid, "date": date, "kind": "confirmed",
                              "athletes": [] if (u.get("home") or u.get("away")) else entries.get(u["disc"], {}).get(u["ev"], [])})
            elif "Ceremony" in u.get("unitEn", ""):
                continue
            elif (any(uid.startswith(p) for p in include)
                  or (u["medal"] in ("1", "2") and u["disc"] not in TEAM_DISCS and not (u.get("home") or u.get("away"))
                      # no start list yet: Korea is entered in the event, so the medal round is a candidate.
                      # Once the start list is out, the branch above keeps it only if Korea is actually in it.
                      and not u.get("orgs") and u["ev"] in entries.get(u["disc"], {}))):
                parts = u["key"].split(".")
                session = (date, u["disc"], ".".join(parts[:-1]), parts[-1][:4])
                g = sessions.get(session)
                if not g:
                    kind = "included" if any(uid.startswith(p) for p in include) else "medal"
                    g = sessions[session] = {**u, "id": uid, "date": date, "included": True, "kind": kind, "count": 0,
                                             "unit": u["unit"].rsplit(", ", 1)[0],
                                             "athletes": entries.get(u["disc"], {}).get(u["ev"], [])}
                g["count"] += 1
                g.setdefault("keys", []).append(u["key"])
                g["endTime"] = u["time"]
                if re.search(r"Running|Live", u.get("status", "")):
                    g["status"] = u["status"]
                elif g["count"] > 1 and not re.search(r"Running|Live", g["status"]):
                    g["status"] = u["status"]  # a session is as finished as its last part
    items += sessions.values()
    items.sort(key=lambda x: (x["dt"], x["disc"]))
    apply_start_lists(get, items, start_days)
    return items
