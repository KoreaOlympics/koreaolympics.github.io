# -*- coding: utf-8 -*-
"""기계체조 세부 문서(15개) 생성 + 체조 문서 2행 탭 삽입 (멱등). athletes.py 실행 뒤에 실행한다.
근거: FIG LA28 Qualification System – Artistic Gymnastics (IOC 게시 PDF, 2026.06.03판)"""
import re, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weightrules as WR
from athletes import D, e, page, toc, infobox, tabs_html, footer_nav, ath_block, STUB, sources_list, ICON, EDIT

SITE = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))) + "/"
PREFIX, NAME = "olgymnastics", "체조"
PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/GAR-LA28-Qualification-System.pdf"
NAV_S, NAV_E = "<!-- agnav:start -->", "<!-- agnav:end -->"

EVENTS = [
    ("남자", [("m-team", "단체", "남자 단체"), ("m-aa", "개인종합", "남자 개인종합"), ("m-fx", "마루", "남자 마루"), ("m-ph", "안마", "남자 안마"),
              ("m-sr", "링", "남자 링"), ("m-vt", "도마", "남자 도마"), ("m-pb", "평행봉", "남자 평행봉"), ("m-hb", "철봉", "남자 철봉")]),
    ("여자", [("w-team", "단체", "여자 단체"), ("w-aa", "개인종합", "여자 개인종합"), ("w-vt", "도마", "여자 도마"), ("w-ub", "이단평행봉", "여자 이단평행봉"),
              ("w-bb", "평균대", "여자 평균대"), ("w-fx", "마루", "여자 마루")]),
    ("혼성", [("x-team", "혼성 단체", "혼성 단체")]),
]
KW = {"fx": ["마루"], "ph": ["안마"], "sr": ["링"], "vt": ["도마"], "pb": ["평행봉"], "hb": ["철봉"], "ub": ["이단평행봉"], "bb": ["평균대"], "aa": ["개인종합"]}


def fname(code):
    return f"{PREFIX}-ag-{code}.html"


def subnav(cur=None):
    out = '<nav class="golf-nav sub-nav" aria-label="기계체조 세부 문서">'
    for gl, items in EVENTS:
        out += f'<span class="sub-label">{gl}</span>' + "".join(
            f'<a href="./{fname(c)}"' + (' aria-current="page"' if c == cur else "") + f">{s}</a>" for c, s, _ in items)
    return NAV_S + out + "</nav>" + NAV_E


# ------------------------------------------------------------------ 규정
def seg_rows(code):
    g, ev = code.split("-")
    w = g == "w"
    if ev == "team":
        if g == "x":
            return None, [], "—"
        segs = [("2026 세계선수권 단체 결선 상위 3팀", 3, 0, "rank"), ("2027 세계선수권 단체 예선 상위 9팀", 9, 0, "cont")]
        rows = [("기준 1 · 2026 세계선수권 (2026.10.17–25)", "<b>3팀</b>", "단체 결선 상위 3개 NOC, 팀당 5명(예비 없음)", "D.1.1"),
                ("기준 2 · 2027 세계선수권 (2027.09.28–10.06)", "9팀", "단체 예선 성적으로 기준 1 미확보 상위 9개 NOC", "D.1.2")]
        return segs, rows, "12팀 · 60명"
    if ev == "aa":
        n4 = 14 if w else 8
        segs = [("세계선수권 단체 차순위 NOC", 3, 0, "gs"), ("2027 세계선수권 개인종합", n4, 0, "rank"), ("2028 대륙선수권 개인종합", 5, 0, "cont"),
                ("개최국", 1, 0, "host"), ("보편성", 1, 0, "univ")]
        rows = [("단체 출전 선수", "12팀 × 5명", "단체 출전 선수는 모두 개인종합 예선에 나갑니다", "D.1"),
                ("기준 3 · 2027 세계선수권", "3장 (NOC)", "단체 미확보 NOC 중 단체 예선 상위 3개국에 개인 1장씩", "D.1.3"),
                ("기준 4 · 2027 세계선수권 개인종합", f"<b>{n4}명</b>", f"단체 미확보 NOC 선수 중 개인종합 예선 상위 {n4}명(NOC당 1명)", "D.2.1"),
                ("기준 7 · 2028 대륙선수권 개인종합", "5명", "대륙별 최상위 1명(대륙 대표 보장)", "D.2.4"),
                ("개최국 · 보편성", "1명 · 1명", "개최국 미국 출전 보장 시 다음 순위 선수에게 · 보편성 신청 2028.01.15 마감", "D.3·D.4")]
        return segs, rows, f"개인 출전권 {3 + n4 + 5 + 2}명"
    segs = [("2027 세계선수권 종목 결선", 1, 0, "rank"), ("2028 종목별 월드컵 시리즈", 2, 0, "cont")]
    rows = [("기준 5 · 2027 세계선수권 종목별 결선", "<b>1명</b>", "단체·개인종합으로 미확보 선수 중 결선 1–3위의 최상위 1명", "D.2.2"),
            ("기준 6 · 2028 종목별 월드컵 시리즈 (2028.02.24–04.15)", "2명", "올림픽 예선 월드컵 랭킹(6개 대회 중 최고 4개) 상위 2명, NOC 종목당 1명", "D.2.3")]
    return segs, rows, "종목 전문 선수 3명"


NOTES = {
    "team": ["단체로 출전권을 얻으면 그 NOC 선수는 개인 경로(기준 4–7)로 따로 출전권을 받을 수 없습니다.",
             "<b>첫 예선은 2026 세계선수권(2026.10.17–25)</b>입니다. 단체 결선 3위 안에 들면 바로 확정됩니다."],
    "aa": ["단체가 없는 NOC는 성별 최대 3명까지 개인으로 출전할 수 있습니다(B.2).",
           "기준 4–7과 개최국·보편성 자리는 선수 이름으로, 기준 1–3은 NOC로 배정됩니다(B.3)."],
    "app": ["종목별 출전권은 단체가 없는 NOC 선수에게만 해당합니다. 단체 출전 선수와 개인종합 선수도 이 종목 결선에 나갈 수 있습니다.",
            "이 경로로 뽑힌 선수도 LA28 예선에서는 모든 종목에 출전할 수 있습니다(D.2.2·D.2.3).",
            "한 선수가 여러 종목에서 자리를 얻거나 NOC 개인 3명 한도를 넘으면 FIG 동점 처리 규정으로 정리합니다."],
}


def rule_html(code, label):
    if code == "x-team":
        return ('<div class="notice">FIG 규정(2026.06.03판)은 혼성 단체를 LA28 신설 종목으로 적었지만, 별도 쿼터나 출전 방식은 적지 않았습니다. '
                '남녀 단체·개인 출전 선수로 구성될 것으로 보이며, FIG 발표가 나오면 추가합니다.</div>')
    segs, rows, tot = seg_rows(code)
    kind = code.split("-")[1]
    body = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows)
    nts = NOTES["team" if kind == "team" else "aa" if kind == "aa" else "app"]
    return (WR.seat_svg(f"{label} 출전권 구성", segs, tot)
            + f'<table class="data wrule"><caption>{label} · LA28 예선 경로 (FIG 2026.06.03판)</caption><thead><tr><th scope="col">경로</th><th scope="col">인원</th>'
              f'<th scope="col">선발 방식</th><th scope="col">규정</th></tr></thead><tbody>{body}</tbody></table>'
            + '<ul class="wnotes">' + "".join(f"<li>{n}</li>" for n in nts) + "</ul>")


# ------------------------------------------------------------------ 한국 선수
def korean(code):
    g, ev = code.split("-")
    sex = {"m": "남", "w": "여"}.get(g)
    gd = D["gymnastics"]
    out = []
    for p in gd["persons"]:
        if sex and p.get("sex") != sex and g != "x":
            continue
        disc = p.get("discipline", "")
        if ev == "team" or any(k in disc for k in KW.get(ev, [])):
            q = dict(p); q["link"] = f"{PREFIX}-p-{p['slug']}.html"; q["note"] = p.get("status_note")
            out.append(q)
    for o in gd.get("others", []):
        if sex and o.get("sex") != sex and g != "x":
            continue
        disc = o.get("discipline", "")
        if ev == "team" or any(k in disc for k in KW.get(ev, [])):
            out.append({"name": o["name"], "sex": o.get("sex"), "note": o.get("note"), "results": [],
                        "sources": [{"title": "출처", "url": o["source_url"]}] if o.get("source_url") else []})
    return out


def build(code, short, label, gl):
    lst = korean(code)
    srcs = [{"title": "FIG · LA28 Qualification System – Artistic Gymnastics (IOC 게시 PDF, 2026.06.03판)", "url": PDF}]
    for a in lst:
        srcs += a.get("sources", [])
    body = "".join(ath_block(a) for a in lst) if lst else '<p class="stub">현재 정리된 한국 주요 선수 없음 · 추후 작성.</p>'
    main = (toc([("rules", f"{label} 예선 규정"), ("athletes", "한국 주요 선수"), ("overview", "개요"), ("sources", "출처")])
            + f'<section id="rules"><h2>{label} 예선 규정</h2>{rule_html(code, label)}</section>'
            + f'<section id="athletes"><h2>한국 주요 선수</h2>{body}</section>'
            + f'<section id="overview"><h2>개요</h2>{STUB}</section>'
            + f'<section id="sources"><h2>출처</h2>{sources_list(srcs)}<p class="small">기본 정보 기준일 {EDIT}.</p></section>')
    names = ", ".join(dict.fromkeys(a["name"] for a in lst)) or "—"
    box = infobox(f"기계체조 · {label}", [("종목", "체조 · 기계체조"), ("구분", gl), ("세부종목", label), ("한국 주요 선수", e(names)), ("기준일", EDIT)],
                  '<p class="small"><a href="./olgymnastics-artistic.html">기계체조 예선 규정 전체 →</a></p>')
    tabs, _ = tabs_html(PREFIX, NAME, cur="olgymnastics-artistic.html")
    nav = (f'<nav class="sport-nav" aria-label="상위 문서"><a href="./{PREFIX}.html">{NAME}</a><a href="./olgymnastics-artistic.html">↑ 기계체조</a></nav>'
           f'<a class="athlete-link" href="./{PREFIX}-athletes.html">{ICON}<span>한국 선수</span></a>')
    return page(f"기계체조 {label} | 체조 · 올림픽예선", f"LA28 기계체조 {label} 예선 경로와 한국 주요 선수", nav, f"기계체조 {label}",
                f"LA28 기계체조 <b>{label}</b>의 출전권 경로와 한국 주요 선수 기본 정보입니다.", tabs + subnav(code), main, box,
                footer_nav(PREFIX, NAME), f"체조 · 기계체조 {label} | 규정 2026.06.03판 · 기준 {EDIT}")


def insert_subnav():
    for f in glob.glob(SITE + PREFIX + "*.html"):
        if "_1" in f or "-ag-" in f:
            continue
        t = open(f, encoding="utf-8", newline="").read()
        o = t
        if NAV_S in t:
            t = t[:t.index(NAV_S)] + subnav() + t[t.index(NAV_E) + len(NAV_E):]
        else:
            m = re.search(r'<nav class="golf-nav"[^>]*>.*?</nav>', t, re.S)
            if not m:
                continue
            t = t[:m.end()] + subnav() + t[m.end():]
        if t != o:
            open(f, "w", encoding="utf-8", newline="").write(t)


def artistic_links():
    f = SITE + "olgymnastics-artistic.html"
    t = open(f, encoding="utf-8", newline="").read()
    S, E = "<!-- aglinks:start -->", "<!-- aglinks:end -->"
    rows = ""
    for gl, items in EVENTS:
        for c, s, l in items:
            segs, _, tot = seg_rows(c) if c != "x-team" else (None, None, "미기재")
            ns = ", ".join(dict.fromkeys(a["name"] for a in korean(c))) or "—"
            rows += f'<tr><th scope="row"><a href="./{fname(c)}">{l}</a></th><td>{tot}</td><td>{e(ns)}</td></tr>'
    block = (f'{S}<h3 id="ag-docs">세부종목별 문서</h3><table class="data"><caption>기계체조 세부종목 · 예선 경로와 한국 주요 선수</caption>'
             f'<thead><tr><th scope="col">세부종목</th><th scope="col">경로별 출전권</th><th scope="col">한국 주요 선수</th></tr></thead><tbody>{rows}</tbody></table>{E}')
    if S in t:
        t = t[:t.index(S)] + block + t[t.index(E) + len(E):]
    else:
        i = t.index('<section id="events">'); j = t.index("</section>", i)
        t = t[:j] + block + t[j:]
    open(f, "w", encoding="utf-8", newline="").write(t)


if __name__ == "__main__":
    n = 0
    for gl, items in EVENTS:
        for c, s, l in items:
            open(SITE + fname(c), "w", encoding="utf-8", newline="\r\n").write(build(c, s, l, gl)); n += 1
    artistic_links()
    insert_subnav()
    print("artistic pages", n)
