"""Walk api.isuresults.eu from a finished World Cup down to one result list."""
import json, pathlib, urllib.request
OUT = pathlib.Path("probe/out/walk"); OUT.mkdir(parents=True, exist_ok=True)
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        return json.loads(r.read())
log = {}
ev = get("https://api.isuresults.eu/events/?orderBy=-start&isPublished=1&season=2026&pageSize=50")
log["events"] = ev
wc = next(e for e in ev["results"] if "world-cup" in e.get("tags", []) and "senior" in e.get("tags", []))
log["schedule"] = get(wc["scheduleUrl"])
comps = get(wc["competitionsUrl"]); log["competitions"] = comps
c = comps[0] if isinstance(comps, list) else comps["results"][0]
log["competition"] = c
for k, v in c.items():
    if isinstance(v, str) and v.startswith("https://api.isuresults.eu"):
        try: log[k] = get(v)
        except Exception as e: log[k] = repr(e)
(OUT / "isuresults.json").write_text(json.dumps(log, ensure_ascii=False, indent=1)[:3_000_000])
