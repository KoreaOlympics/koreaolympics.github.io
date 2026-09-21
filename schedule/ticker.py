"""A few lines of "what just happened" for the pages' ticker -> data/ticker.json.

Built from the Korea rows that korea.build() already produced, so it costs no extra API calls.
"""
import datetime, json, pathlib, re
from translate import DISC_KO

DATA = pathlib.Path(__file__).parent / "data"
JST = datetime.timezone(datetime.timedelta(hours=9))
LIVE = re.compile(r"Running|Live|Interrupted")
DONE = re.compile(r"Official|Unofficial|Finished")
MEDAL_KO = {"ME_GOLD": "금", "ME_SILVER": "은", "ME_BRONZE": "동"}
RECENT_H, SOON_H = 3, 3
BALL = {"FBL", "BBL", "BKB", "BK3", "VVO", "VBV"}  # 축구·야구·농구·배구를 먼저 보여준다
KIND_ORDER = {"live": 0, "medal": 1, "result": 2, "next": 3}
KEEP = 2  # 전광판에 올릴 최대 줄 수


def score(x):
    """"대한민국 3 : 0 카타르" for matches, "" for everything else."""
    h, a = x.get("home"), x.get("away")
    if not (h or a):
        return ""
    k, o = (h, a) if (h and h["org"] == "KOR") else (a, h)
    me, you = (k or {}).get("nameKo") or "대한민국", (o or {}).get("nameKo") or (o or {}).get("name") or "미정"
    if (k or {}).get("result") or (o or {}).get("result"):
        return f'{me} {k.get("result", "")} : {o.get("result", "") if o else ""} {you}'
    return f"{me} vs {you}"


def result_medals(row_id):
    """Korean medals recorded in the unit's result file, if it has one."""
    try:
        r = json.loads((DATA / "results" / (row_id.replace("/", "_") + ".json")).read_text(encoding="utf-8"))
    except Exception:
        return []
    return [(c.get("name", ""), MEDAL_KO[c["medal"]]) for c in r.get("competitors", [])
            if c.get("org") == "KOR" and c.get("medal") in MEDAL_KO]


def build(kor, medals):
    now = datetime.datetime.now(JST)
    today = str(now.date())
    items, seen = [], set()

    def add(kind, text, when="", disc="", rid="", mins=0):
        if text and text not in seen:
            seen.add(text)
            items.append({"kind": kind, "text": text, "when": when, "disc": disc, "id": rid, "_m": abs(mins)})

    # 오늘 딴 메달
    for x in kor:
        if x["date"] != today or not DONE.search(x.get("status", "")):
            continue
        for name, m in result_medals(x["id"]):
            add("medal", f'{m}메달 · {x["unit"]} {name}', x["time"], x["disc"], x["id"])
        h, a = x.get("home"), x.get("away")
        if x.get("medal") == "1" and (h or a):
            k = h if (h and h["org"] == "KOR") else a
            if k and k.get("win"):
                add("medal", f'금메달 · {x["unit"]} {score(x)}', x["time"], x["disc"], x["id"])

    for x in kor:
        if x["date"] != today:
            continue
        dt = x.get("dt", "")
        try:
            start = datetime.datetime.fromisoformat(dt)
        except ValueError:
            continue
        mins = (start - now).total_seconds() / 60
        unit = f'{x.get("sportName") or DISC_KO.get(x["disc"], x.get("discDesc", ""))} {x["unit"]}'.strip()
        if LIVE.search(x.get("status", "")):
            add("live", f"{unit} {score(x)}".strip(), x["time"], x["disc"], x["id"], mins)
        elif DONE.search(x.get("status", "")) and -RECENT_H * 60 <= mins <= 0:
            add("result", f"{unit} {score(x)}".strip(), x["time"], x["disc"], x["id"], mins)
        elif 0 < mins <= SOON_H * 60:
            add("next", f"{unit} {score(x)}".strip(), x["time"], x["disc"], x["id"], mins)

    # 구기 먼저, 그 다음 진행 중 > 메달 > 결과 > 예정, 같은 조건이면 지금에 가까운 것
    items.sort(key=lambda i: (i["disc"] not in BALL, KIND_ORDER.get(i["kind"], 9), i["_m"]))
    items = [{k: v for k, v in i.items() if k != "_m"} for i in items[:KEEP]]

    kr = next((m for m in medals if m.get("org") == "KOR"), None)
    out = {"updated": now.isoformat(timespec="minutes"), "date": today,
           "medals": {"rk": kr.get("rk", ""), "g": kr["g"], "s": kr["s"], "b": kr["b"], "t": kr["t"]} if kr else None,
           "items": items}
    (DATA / "ticker.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print("ticker items", len(out["items"]))
    return out
