"""ISU figure skating: find GP de France in events/list and dump its schedule."""
import json, pathlib, urllib.request
OUT = pathlib.Path("probe/out/walk"); OUT.mkdir(parents=True, exist_ok=True)
def post(u, d):
    req = urllib.request.Request(u, data=json.dumps(d).encode(), headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r: return json.loads(r.read())
log = {}
for state in ["Live", "On", "Finished", ""]:
    for lvl in ["ISU", None]:
        body = {"discipline_id": 1, "page": 1, "pagesize": 60}
        if state: body["state"] = state
        if lvl: body["event_level"] = lvl
        try:
            r = post("https://front-api.isu.org/events/list", body)
            log[f"{state}|{lvl}"] = [(e["name"], e["from_date"][:10], e["state"], e["season"], e.get("event_sub_type_name"), e.get("slug"), e.get("event_level")) for e in r.get("data") or []]
        except Exception as ex:
            log[f"{state}|{lvl}"] = repr(ex)
for slug in ["isu-gp-grand-prix-de-france-2026"]:
    try: log["sched:" + slug] = get(f"https://front-api.isu.org/events/getschedule/{slug}")
    except Exception as ex: log["sched:" + slug] = repr(ex)
(OUT / "fs.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))
