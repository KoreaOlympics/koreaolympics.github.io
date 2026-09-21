"""Fetch AG2026 daily schedules (all units expanded) into data/*.json.

    python fetch.py            # every competition day
    python fetch.py --window 1 # yesterday..tomorrow (JST) only, for frequent refreshes
"""
import argparse, json, zlib, datetime, pathlib, urllib.request, time
from translate import ko, NOC_KO
import korea, brackets, results, ticker

BASE = "https://back.results.asiangames2026.org/s/AG2026/en/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://results.asiangames2026.org",
    "Referer": "https://results.asiangames2026.org/",
}
OUT = pathlib.Path(__file__).parent / "data"
FIRST, LAST = datetime.date(2026, 9, 10), datetime.date(2026, 10, 4)
JST = datetime.timezone(datetime.timedelta(hours=9))


def get(path, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, headers=HEADERS)
            raw = urllib.request.urlopen(req, timeout=30).read()
            # Body is zlib bytes serialized as latin-1 chars inside UTF-8.
            return json.loads(zlib.decompress(raw.decode("utf-8").encode("latin-1")))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2)


def slim(u):
    def side(s):
        if not s or not s.get("HasData"):
            return None
        org, name = s.get("Org", ""), s.get("Name", "")
        team = u.get("Type") == "T" or not org
        name_ko = NOC_KO.get(org, name) if team else korea.athlete_ko(name) if org == "KOR" else name
        return {"org": org, "name": name, "nameKo": name_ko, "team": team, "result": s.get("Result", ""), "win": s.get("Winner", False)}
    disc = u["Disc"]
    unit = u.get("UnitDesc") or u.get("UnitDescA", "")
    return {
        "key": u.get("Key", ""), "ev": u.get("Event", ""), "orgs": u.get("Orgs") or [],
        "disc": disc, "discDesc": u["DiscDesc"],
        "time": u["DateTimeRaw"][11:16], "dt": u["DateTimeRaw"],
        "hideTime": u.get("HideStartDate", False), "est": u.get("EstText", ""),
        "event": ko(u.get("EventDesc", ""), disc), "phase": ko(u.get("PhaseDesc", ""), disc),
        "unit": ko(unit, disc), "unitEn": unit,
        "medal": u.get("Medal", ""), "status": u.get("StatusDesc", ""),
        "venue": u.get("VenueDescS", ""), "loc": u.get("LocDescS", ""),
        "home": side(u.get("Home")), "away": side(u.get("Away")),
    }


def fetch_day(d):
    overview = get(f"ALL/schedule/day/{d}")
    units = []
    # The overview omits competitors; the per-discipline feed (what "Expand" loads) has them.
    for disc in dict.fromkeys(u["Disc"] for u in overview):
        try:
            detail = get(f"{disc}/schedule/daily/{d}")
        except Exception as e:
            print("  fallback", disc, e)
            detail = [u for u in overview if u["Disc"] == disc]
        units += [slim(u) for u in detail if not u.get("IsPhase")]
        time.sleep(0.2)
    units.sort(key=lambda u: (u["dt"], u["disc"]))
    return units


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, help="only refresh today±N days (JST)")
    args = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    start, end = FIRST, LAST
    if args.window is not None:
        today = datetime.datetime.now(JST).date()
        start = max(FIRST, today - datetime.timedelta(days=args.window))
        end = min(LAST, today + datetime.timedelta(days=args.window))

    index_path = OUT / "index.json"
    counts = {}
    if index_path.exists():
        counts = {x["date"]: x["count"] for x in json.loads(index_path.read_text(encoding="utf-8"))["days"]}

    d = start
    while d <= end:
        units = fetch_day(d)
        (OUT / f"{d}.json").write_text(json.dumps(units, ensure_ascii=False), encoding="utf-8")
        counts[str(d)] = len(units)
        print(d, len(units))
        d += datetime.timedelta(days=1)

    days, d = [], FIRST
    while d <= LAST:
        days.append({"date": str(d), "count": counts.get(str(d), 0)})
        d += datetime.timedelta(days=1)
    kor = korea.build(get, refresh_entries=args.window is None, start_days=None if args.window is None else max(args.window, 1))
    (OUT / "kor.json").write_text(json.dumps(kor, ensure_ascii=False), encoding="utf-8")
    print("kor items", len(kor))
    try:
        results.build(get, kor)
    except Exception as e:
        print("results failed", e)
    try:
        medals = sorted(get("ALL/medals/standings"), key=lambda r: r.get("RkPo") or 999)
        rows = [{"org": r["Org"], "name": NOC_KO.get(r["Org"], r.get("OrgDesc", "")), "rk": r.get("Rk", ""),
                 "g": r["Count"]["ME_GOLD"]["total"], "s": r["Count"]["ME_SILVER"]["total"], "b": r["Count"]["ME_BRONZE"]["total"],
                 "t": r["Count"]["total"]["total"]} for r in medals]
        (OUT / "medals.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print("medals failed", e)
        rows = []
    try:
        ticker.build(kor, rows)
    except Exception as e:
        print("ticker failed", e)
    try:
        brackets.build(get, window=args.window)
    except Exception as e:  # brackets are a bonus; never block the schedule refresh
        print("brackets failed", e)

    meta = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"), "days": days}
    index_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
