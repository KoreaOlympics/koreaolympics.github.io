"""Official results for Korea's recent units -> data/results/<row id>.json (one small file per unit)."""
import datetime, json, pathlib, re
from korea import athlete_ko
from translate import ko, NOC_KO

DATA = pathlib.Path(__file__).parent / "data"
OUT = DATA / "results"
JST = datetime.timezone(datetime.timedelta(hours=9))
HAS_RESULTS = re.compile(r"Official|Unofficial|Running|Live|Start List|Interrupted|Getting Ready")

# Result columns come back as extension codes; these are the ones worth a column header.
COLS = {
    "VICT": "승", "DEF": "패", "PEN": "반칙", "PENALTIES": "반칙", "TOUCHES_SCORED": "찌른 수", "TOUCHES_RECEIVED": "맞은 수",
    "POINTS": "점수", "TOTAL": "합계", "TIME": "기록", "REACTION_TIME": "반응", "DIFF": "차이", "LAPS": "랩",
    "SCORE": "점수", "TOTAL_POINTS": "총점", "SETS": "세트", "GOALS": "득점",
}


def path_for(row_id):
    return OUT / (row_id.replace("/", "_") + ".json")


def slim(data, disc):
    comps = []
    for c in data.get("Competitors") or []:
        ext = {}
        for e in c.get("Extensions") or []:
            if e.get("Type", "").startswith("ER_") and e.get("Code") in COLS and not e.get("Pos"):
                ext[e["Code"]] = e.get("Value", "")
        org = c.get("Org", "")
        name = c.get("Name", "")
        comps.append({
            "rk": c.get("Rk", ""), "org": org,
            # a competitor whose name is just the country is a team entry
            "name": (NOC_KO.get(org, name) if name == c.get("OrgDesc") else athlete_ko(name) if org == "KOR" else name),
            "orgName": NOC_KO.get(org, c.get("OrgDesc", "")),
            "res": c.get("Result", ""), "detail": c.get("ResDetail", ""), "irm": c.get("IRM", ""),
            "medal": c.get("Medal", ""), "qual": c.get("Qualified", ""), "cols": ext,
        })
    info = data.get("Info", {})
    res = data.get("Results", {}) or {}
    return {
        "title": ko(info.get("UnitDesc", ""), disc), "status": info.get("StatusDesc", ""), "dt": info.get("DateTimeRaw", ""),
        "venue": info.get("VenueDescS", ""), "result": res.get("Result", ""), "detail": res.get("ResDetail", ""),
        "periods": [{"name": p.get("Desc", ""), "home": p.get("HomeResult", ""), "away": p.get("AwayResult", "")}
                    for p in (res.get("Periods") or []) if p.get("HomeResult") not in (None, "")],
        "cols": [c for c in COLS if any(c in x["cols"] for x in comps)],
        # "Result" is meaningless for some units (all zeros): drop the column then
        "showRes": any(x["res"] not in ("", "0") for x in comps),
        "competitors": comps,
    }


def build(get, rows, days_back=3, limit=60):
    """Fetch results for recently played rows; older files stay as they are."""
    OUT.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now(JST).date()
    done, index = 0, {}
    for f in OUT.glob("*.json"):
        index[f.stem] = True
    for r in rows:
        if done >= limit:
            break
        day = datetime.date.fromisoformat(r["date"])
        if not (today - datetime.timedelta(days=days_back) <= day <= today) or not HAS_RESULTS.search(r.get("status", "")):
            continue
        keys = r.get("keys") or [r["key"]]
        try:
            data = get(f"{r['disc']}/results/{keys[0]}")
        except Exception as e:
            print("  results fail", r["id"], e)
            continue
        done += 1
        out = slim(data, r["disc"])
        if out["competitors"] or out["periods"] or out["result"]:
            path_for(r["id"]).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
            index[r["id"].replace("/", "_")] = True
    (DATA / "results_index.json").write_text(json.dumps(sorted(index), ensure_ascii=False), encoding="utf-8")
    print("results fetched", done)
