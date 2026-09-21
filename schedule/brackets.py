"""Standings and knockout brackets for every event the official feeds publish -> data/brackets/<DISC>.json.

Events are discovered from the feeds themselves (no hand-kept list): any (discipline, event) in the daily
schedule whose groups/brackets feed has data becomes a bracket page entry, so sports whose draw is published
later (judo, taekwondo, tennis...) show up on their own. Discovered events are remembered in
data/bracket_events.json; quick runs refresh only what is playing today, full runs refresh everything.
"""
import datetime, glob, json, pathlib, re
from translate import ko, DISC_KO, NOC_KO

DATA = pathlib.Path(__file__).parent / "data"
OUT = DATA / "brackets"
CACHE = DATA / "bracket_events.json"
JST = datetime.timezone(datetime.timedelta(hours=9))
GENDER = re.compile(r"^(남자|여자|혼성)\s*")
RESCAN_DAYS = 3  # 아직 대진이 없는 이벤트를 다시 확인하기까지의 간격


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


def schedule_rounds(units):
    """Every match of the event from the daily files, grouped by round in playing order."""
    rounds = {}
    for u in units:
        if "Ceremony" in u.get("unitEn", "") or "시상식" in u["phase"]:
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


def unit_index():
    """(discipline, event) -> its units, and the days it is played on."""
    idx, days = {}, {}
    for f in sorted(glob.glob(str(DATA / "2026-*.json"))):
        day = pathlib.Path(f).stem
        for u in json.loads(pathlib.Path(f).read_text(encoding="utf-8")):
            ev = u.get("ev")
            if not ev:
                continue
            idx.setdefault((u["disc"], ev), []).append(u)
            days.setdefault((u["disc"], ev), set()).add(day)
    return idx, days


def label_of(units):
    """"남자 단체", "여자 구미테 -61kg" — the event name the schedule already shows."""
    for u in units:
        if u.get("event"):
            return u["event"]
    return units[0]["unit"] if units else ""


def load_cache():
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {"events": {}, "empty": {}}


def has_data(get, disc, ev):
    """(pools, bracket matches) counts from the two feeds; either one makes the event worth keeping."""
    pools = matches = 0
    try:
        g = get(f"{disc}/groups/{ev}")
        pools = len([x for x in (g or {}).get("Groups", []) if x.get("Type") == "POOL" and x.get("Competitors")])
    except Exception as e:
        print("  groups fail", disc, ev, e)
    try:
        b = get(f"{disc}/brackets/{ev}")
        matches = sum(len(p.get("Matches", [])) for top in (b or []) for p in top.get("Phases", []))
    except Exception as e:
        print("  bracket fail", disc, ev, e)
    return pools, matches


def build_event(get, disc, ev, units, label):
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
    return {"disc": disc, "ev": ev, "label": label, "standings": table, "bracket": tree,
            "rounds": schedule_rounds(units)}


def build(get, window=None, discover_limit=400):
    """window=None (full run): re-check every event. window=N: only events played within N days of today."""
    OUT.mkdir(parents=True, exist_ok=True)
    idx, days = unit_index()
    cache = load_cache()
    today = datetime.datetime.now(JST).date()
    span = None if window is None else (str(today - datetime.timedelta(days=window)), str(today + datetime.timedelta(days=window)))

    def playing_now(key):
        return span is None or any(span[0] <= d <= span[1] for d in days.get(key, ()))

    # 1) 새 이벤트 찾기: 대진이 아직 없던 조합은 RESCAN_DAYS 간격으로만 다시 확인
    probes = 0
    for key in sorted(idx):
        disc, ev = key
        kid = f"{disc}/{ev}"
        if kid in cache["events"] or probes >= discover_limit:
            continue
        last = cache["empty"].get(kid)
        soon = any(str(today - datetime.timedelta(days=2)) <= d <= str(today + datetime.timedelta(days=5)) for d in days[key])
        if not (span is None or soon):
            continue
        if last and datetime.date.fromisoformat(last) > today - datetime.timedelta(days=RESCAN_DAYS):
            continue
        probes += 1
        pools, matches = has_data(get, disc, ev)
        if pools or matches:
            cache["events"][kid] = {"disc": disc, "ev": ev, "label": label_of(idx[key])}
            cache["empty"].pop(kid, None)
            print("  + bracket event", kid, cache["events"][kid]["label"])
        else:
            cache["empty"][kid] = str(today)

    # 2) 갱신: 전체 갱신이면 전부, 빠른 갱신이면 오늘 전후 경기가 있는 이벤트만
    by_disc = {}
    for kid, meta in cache["events"].items():
        by_disc.setdefault(meta["disc"], []).append(meta)
    written = refreshed = 0
    for disc, metas in sorted(by_disc.items()):
        path = OUT / f"{disc}.json"
        try:
            prev = {e["ev"]: e for e in json.loads(path.read_text(encoding="utf-8"))}
        except Exception:
            prev = {}
        events = []
        for meta in sorted(metas, key=lambda m: m["ev"]):
            key = (disc, meta["ev"])
            units = idx.get(key, [])
            meta["label"] = label_of(units) or meta["label"]
            if playing_now(key) or meta["ev"] not in prev:
                events.append(build_event(get, disc, meta["ev"], units, meta["label"]))
                refreshed += 1
            else:
                e = prev[meta["ev"]]
                e["rounds"] = schedule_rounds(units)  # 일정·점수는 매번 최신으로
                events.append(e)
        path.write_text(json.dumps(events, ensure_ascii=False), encoding="utf-8")
        written += 1

    # 3) 목록 파일: 페이지가 종목을 고를 때 쓰는 색인
    index = []
    for disc, metas in sorted(by_disc.items(), key=lambda kv: DISC_KO.get(kv[0], kv[0])):
        evs = []
        for meta in sorted(metas, key=lambda m: m["ev"]):
            key = (disc, meta["ev"])
            units = idx.get(key, [])
            kor = any("KOR" in (u.get("orgs") or []) or any(s and s.get("org") == "KOR" for s in (u.get("home"), u.get("away")))
                      for u in units)
            ds = sorted(days.get(key, ()))
            evs.append({"ev": meta["ev"], "label": meta["label"], "g": meta["ev"][0], "kor": kor,
                        "from": ds[0] if ds else "", "to": ds[-1] if ds else ""})
        index.append({"disc": disc, "name": DISC_KO.get(disc, disc), "events": evs})
    (DATA / "brackets_index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    print(f"brackets: {len(cache['events'])} events / {written} files (refreshed {refreshed}, probed {probes})")
    return index
