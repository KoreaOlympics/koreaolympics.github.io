# -*- coding: utf-8 -*-
"""한국 선수 문서 생성기 (골프형 포맷)
- 관심 개인종목 9개: 선수별 문서 + 기타 + 종목별 '한국 선수' 탭
- 세부종목별 7개: 세부종목·체급별 문서 + '한국 선수' 탭
- 해당 16개 종목 기존 문서: 상위 링크 index1 → index, 상단 선수 아이콘 링크, 하위 탭에 '한국 선수' 추가
- index.html: '한국 선수' 탭 + 관심 개인종목 표시
"""
import json, re, os, glob, html as H
from datetime import date
import weightrules as WR
WEIGHT = ("judo", "taekwondo", "weightlifting", "wrestling", "boxingw")

SITE = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))) + "/"
RS = __import__("os").path.dirname(__import__("os").path.abspath(__file__)) + "/research/"
TODAY = date(2026, 10, 5)
EDIT = "2026.10.05"
INDEX = "https://koreaolympics.github.io/index.html"
ICON = ('<svg class="ath-ic" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">'
        '<circle cx="8" cy="4.6" r="3" fill="currentColor"/><path d="M2 15.2c0-3.4 2.7-5.6 6-5.6s6 2.2 6 5.6z" fill="currentColor"/></svg>')


def e(s):
    return H.escape(str(s), quote=True) if s is not None else ""


def load(f):
    return json.load(open(RS + f, encoding="utf-8"))


D = {}
for f in ["climb_skate.json", "golf.json", "box_mp_sail_ten.json", "gymnastics.json", "swimming.json", "tkd_judo.json", "arch_bad.json", "shoot_fence.json", "weightlifting.json", "wrestling.json"]:
    D.update(load(f))

# ------------------------------------------------------------------ 종목 정의
BOX_MAP = {"신재용": "m55", "장동환": "m60", "김준수": "m70", "김민성": "m80", "김기채": "m90", "주태웅": "mo90",
           "박초롱": "w51", "임애지": "w54", "오연지": "w60"}


def _boxing_classes():
    ev = {}
    for p in D["boxing"]["persons"]:
        c = BOX_MAP.get(p["name"])
        if c:
            q = dict(p); q["link"] = f"olboxing-p-{p['slug']}.html"; q["note"] = p.get("status_note")
            ev.setdefault(c, {"athletes": [], "sources": []})["athletes"].append(q)
    for o in D["boxing"].get("others", []):
        c = BOX_MAP.get(o["name"])
        if c:
            ev.setdefault(c, {"athletes": [], "sources": []})["athletes"].append(
                {"name": o["name"], "sex": o.get("sex"), "note": o.get("note"), "results": [], "sources": [{"title": "출처", "url": o["source_url"]}] if o.get("source_url") else []})
    return {"events": ev}


D["boxingw"] = _boxing_classes()

INTEREST = [  # (key, prefix, 이름, 데이터키, 사용자 지정 순서)
    ("climbing", "olclimbing", "스포츠클라이밍", ["이도현", "서채현", "정지민"]),
    ("golf", "olgolf", "골프", ["김시우", "김주형", "유해란", "김세영"]),
    ("athletics", "olathletics", "육상", None),
    ("skateboard", "olskateboard", "스케이트보딩", ["강준이", "신지율"]),
    ("boxing", "olboxing", "복싱", ["임애지", "김민성", "장동환"]),
    ("modernpentathlon", "olmodernpentathlon", "근대5종", ["서창완", "전웅태", "성승민"]),
    ("sailing", "olsailing", "요트", ["하지민"]),
    ("tennis", "oltennis", "테니스", ["권순우"]),
    ("gymnastics", "olgymnastics", "체조", ["여서정", "황서현", "류성현"]),
]
ATHLETICS = [("woo-sanghyeok", "우상혁"), ("kim-jangwoo-yu-gyumin", "김장우·유규민"), ("cho-eljin-biwesa", "조엘진·비웨사"),
             ("lee-jaewoong", "이재웅"), ("park-sihun", "박시훈"), ("other-track", "기타 트랙"), ("other-field", "기타 필드")]

EV = {
    "swimming": ("olswimming", "수영", [
        ("자유형", [("free50", "자유형 50m"), ("free100", "자유형 100m"), ("free200", "자유형 200m"), ("free400", "자유형 400m"), ("free800", "자유형 800m"), ("free1500", "자유형 1500m")]),
        ("배영", [("back50", "배영 50m (신설)"), ("back100", "배영 100m"), ("back200", "배영 200m")]),
        ("평영", [("breast50", "평영 50m (신설)"), ("breast100", "평영 100m"), ("breast200", "평영 200m")]),
        ("접영", [("fly50", "접영 50m (신설)"), ("fly100", "접영 100m"), ("fly200", "접영 200m")]),
        ("개인혼영", [("im200", "개인혼영 200m"), ("im400", "개인혼영 400m")]),
        ("계영·혼계영", [("relay4x100free", "계영 400m (4×100m)"), ("relay4x200free", "계영 800m (4×200m)"), ("relay4x100medley", "혼계영 400m (4×100m)"), ("mixed4x100medley", "혼성 혼계영 400m")]),
    ]),
    "taekwondo": ("oltaekwondo", "태권도", [
        ("남자", [("m58", "남자 -58kg"), ("m68", "남자 -68kg"), ("m80", "남자 -80kg"), ("mo80", "남자 +80kg")]),
        ("여자", [("w49", "여자 -49kg"), ("w57", "여자 -57kg"), ("w67", "여자 -67kg"), ("wo67", "여자 +67kg")]),
    ]),
    "judo": ("oljudo", "유도", [
        ("남자", [("m60", "남자 -60kg"), ("m66", "남자 -66kg"), ("m73", "남자 -73kg"), ("m81", "남자 -81kg"), ("m90", "남자 -90kg"), ("m100", "남자 -100kg"), ("mo100", "남자 +100kg")]),
        ("여자", [("w48", "여자 -48kg"), ("w52", "여자 -52kg"), ("w57", "여자 -57kg"), ("w63", "여자 -63kg"), ("w70", "여자 -70kg"), ("w78", "여자 -78kg"), ("wo78", "여자 +78kg")]),
        ("혼성", [("xteam", "혼성 단체")]),
    ]),
    "archery": ("olarchery", "양궁", [
        ("리커브", [("rm", "리커브 남자 개인"), ("rw", "리커브 여자 개인"), ("rmt", "리커브 남자 단체"), ("rwt", "리커브 여자 단체"), ("rx", "리커브 혼성 단체")]),
        ("컴파운드", [("cx", "컴파운드 혼성 단체 (신설)")]),
    ]),
    "shooting": ("olshooting", "사격", [
        ("소총", [("arm", "10m 공기소총 남자"), ("arw", "10m 공기소총 여자"), ("r3m", "50m 소총3자세 남자"), ("r3w", "50m 소총3자세 여자"), ("arx", "10m 공기소총 혼성")]),
        ("권총", [("apm", "10m 공기권총 남자"), ("apw", "10m 공기권총 여자"), ("rfm", "25m 속사권총 남자"), ("p25w", "25m 권총 여자"), ("apx", "10m 공기권총 혼성")]),
        ("산탄총", [("trm", "트랩 남자"), ("trw", "트랩 여자"), ("skm", "스키트 남자"), ("skw", "스키트 여자"), ("trx", "트랩 혼성")]),
    ]),
    "fencing": ("olfencing", "펜싱", [
        ("남자 개인", [("fm", "남자 플뢰레 개인"), ("em", "남자 에페 개인"), ("sm", "남자 사브르 개인")]),
        ("여자 개인", [("fw", "여자 플뢰레 개인"), ("ew", "여자 에페 개인"), ("sw", "여자 사브르 개인")]),
        ("남자 단체", [("fmt", "남자 플뢰레 단체"), ("emt", "남자 에페 단체"), ("smt", "남자 사브르 단체")]),
        ("여자 단체", [("fwt", "여자 플뢰레 단체"), ("ewt", "여자 에페 단체"), ("swt", "여자 사브르 단체")]),
    ]),
    "badminton": ("olbadminton", "배드민턴", [
        ("단식", [("ms", "남자 단식"), ("ws", "여자 단식")]),
        ("복식", [("md", "남자 복식"), ("wd", "여자 복식"), ("xd", "혼합 복식")]),
    ]),
    "weightlifting": ("olweightlifting", "역도", [
        ("남자", [("m65", "남자 65kg"), ("m75", "남자 75kg"), ("m85", "남자 85kg"), ("m95", "남자 95kg"), ("m110", "남자 110kg"), ("mo110", "남자 +110kg")]),
        ("여자", [("w53", "여자 53kg"), ("w61", "여자 61kg"), ("w69", "여자 69kg"), ("w77", "여자 77kg"), ("w86", "여자 86kg"), ("wo86", "여자 +86kg")]),
    ]),
    "wrestling": ("olwrestling", "레슬링", [
        ("남자 자유형", [("fs57", "남자 자유형 57kg"), ("fs65", "남자 자유형 65kg"), ("fs74", "남자 자유형 74kg"), ("fs86", "남자 자유형 86kg"), ("fs97", "남자 자유형 97kg"), ("fs125", "남자 자유형 125kg")]),
        ("그레코로만형", [("gr60", "그레코로만형 60kg"), ("gr67", "그레코로만형 67kg"), ("gr77", "그레코로만형 77kg"), ("gr87", "그레코로만형 87kg"), ("gr97", "그레코로만형 97kg"), ("gr130", "그레코로만형 130kg")]),
        ("여자 자유형", [("ww50", "여자 자유형 50kg"), ("ww53", "여자 자유형 53kg"), ("ww57", "여자 자유형 57kg"), ("ww62", "여자 자유형 62kg"), ("ww68", "여자 자유형 68kg"), ("ww76", "여자 자유형 76kg")]),
    ]),
    "boxingw": ("olboxing", "복싱", [
        ("남자", [("m55", "남자 55kg"), ("m60", "남자 60kg"), ("m65", "남자 65kg"), ("m70", "남자 70kg"), ("m80", "남자 80kg"), ("m90", "남자 90kg"), ("mo90", "남자 +90kg")]),
        ("여자", [("w51", "여자 51kg"), ("w54", "여자 54kg"), ("w57", "여자 57kg"), ("w60", "여자 60kg"), ("w65", "여자 65kg"), ("w70", "여자 70kg"), ("w75", "여자 75kg")]),
    ]),
}


def ev_rule_page(key, code):
    """세부종목 → 기존 예선 안내 하위 문서"""
    p = EV[key][0]
    if key == "swimming":
        if code in ("back50", "breast50", "fly50"): return f"{p}-new.html"
        if code.startswith(("relay", "mixed")): return f"{p}-relay.html"
        return f"{p}.html"
    if key == "taekwondo": return f"{p}-{'men' if code[0] == 'm' else 'women'}.html"
    if key == "judo": return f"{p}-{ {'m': 'men', 'w': 'women', 'x': 'mixed'}[code[0]] }.html"
    if key == "archery": return f"{p}-" + {"rm": "individual", "rw": "individual", "rmt": "team", "rwt": "team", "rx": "mixed", "cx": "compound"}[code] + ".html"
    if key == "shooting": return f"{p}-" + ("rifle" if code[0] in "ar" and code not in ("apm", "apw", "apx", "rfm") else "pistol" if code in ("apm", "apw", "apx", "rfm", "p25w") else "shotgun") + ".html"
    if key == "fencing": return f"{p}-{'team' if code.endswith('t') else 'individual'}.html"
    if key == "badminton": return f"{p}-{'singles' if code.endswith('s') else 'doubles'}.html"
    if key in ("weightlifting", "boxingw"): return f"{p}-{'men' if code[0] == 'm' else 'women'}.html"
    if key == "wrestling": return f"{p}-" + {"fs": "freestyle", "gr": "greco", "ww": "women"}[code[:2]] + ".html"


# ------------------------------------------------------------------ 공통 조각
def age(b):
    if not b: return None
    m = re.match(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", b)
    y, mo, d = int(m.group(1)), m.group(2), m.group(3)
    if mo and d:
        a = TODAY.year - y - ((TODAY.month, TODAY.day) < (int(mo), int(d)))
        return f"{y}년 {int(mo)}월 {int(d)}일 (만 {a}세)"
    if mo:
        return f"{y}년 {int(mo)}월"
    return f"{y}년생"


def medal_cls(r):
    r = str(r)
    return "m-g" if r.startswith("금") else "m-s" if r.startswith("은") else "m-b" if r.startswith("동") else ""


def results_table(rs, cap="주요 성적"):
    if not rs:
        return '<p class="stub">확인된 주요 성적이 아직 정리되지 않았습니다.</p>'
    rows = "".join(f'<tr><td>{e(r.get("year"))}</td><td>{e(r.get("comp"))}</td><td>{e(r.get("event"))}</td><td class="{medal_cls(r.get("result"))}">{e(r.get("result"))}</td></tr>' for r in rs)
    return (f'<table class="data ath-res"><caption>{cap}</caption><thead><tr><th scope="col">연도</th><th scope="col">대회</th><th scope="col">세부종목</th>'
            f'<th scope="col">결과</th></tr></thead><tbody>{rows}</tbody></table>')


def sources_list(srcs):
    seen, out = set(), []
    for s in srcs:
        u = s.get("url") if isinstance(s, dict) else s
        if not u or u in seen: continue
        seen.add(u)
        t = s.get("title") if isinstance(s, dict) else u
        out.append(f'<li><a href="{e(u)}">{e(t or u)}</a></li>')
    return '<ol class="sources">' + "".join(out) + "</ol>" if out else '<p class="stub">출처 추가 예정.</p>'


STUB = '<p class="stub">본문은 추후 작성 예정입니다. 현재 문서는 기본 정보(인포박스)와 확인된 주요 성적만 담고 있습니다.</p>'


def page(title_tag, desc, top_nav, h1, intro, tabs, main, aside, foot_nav, foot_note):
    return ('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="description" content="{e(desc)}"><title>{e(title_tag)}</title><link rel="stylesheet" href="./css/olympic-wiki.css"></head>'
            f'<body><a class="skip" href="#main">본문 바로가기</a><header class="topbar"><div class="topbar-inner"><a href="{INDEX}">← 올림픽예선 목차</a>{top_nav}<span>LA28 · 종목별 예선</span></div></header>'
            f'<div class="shell"><h1 class="title">{h1}</h1><p class="intro">{intro}</p>{tabs}'
            f'<div class="columns"><main id="main">{main}</main>{aside}</div>'
            f'<footer class="footer"><nav class="footer-nav" aria-label="하단 문서">{foot_nav}</nav><p>{foot_note}</p><a href="#main">본문 위로 ↑</a></footer></div></body></html>\n')


def toc(items):
    return '<nav class="toc" aria-label="이 문서의 목차"><strong>목차</strong><ol>' + "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in items) + "</ol></nav>"


def infobox(h, rows, foot=""):
    dl = "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in rows if b)
    return f'<aside class="infobox ath-box" aria-label="{e(h)} 정보"><h2>{h}</h2><dl>{dl}</dl>{foot}</aside>'


# ---- 기존 종목 하위 탭 읽기
def sport_tabs(prefix):
    f = SITE + prefix + ".html"
    if not os.path.exists(f):
        return []
    t = open(f, encoding="utf-8").read()
    m = re.search(r'<nav class="golf-nav"[^>]*>(.*?)</nav>', t, re.S)
    if not m or "section-nav" in m.group(0):
        return [(f"{prefix}.html", "전체 안내")]
    return [(h.lstrip("./"), H.unescape(re.sub("<[^>]+>", "", x))) for h, x in re.findall(r'<a href="([^"#]+)"[^>]*>(.*?)</a>', m.group(1)) if "-athletes" not in h]


def tabs_html(prefix, name, cur_athletes=True, cur=None):
    tabs = sport_tabs(prefix) + [(f"{prefix}-athletes.html", "한국 선수")]
    def on(h):
        return (h == cur) if cur else (cur_athletes and h.endswith("-athletes.html"))
    a = "".join(f'<a href="./{h}"' + (' aria-current="page"' if on(h) else "") + f">{x}</a>" for h, x in tabs)
    return f'<nav class="golf-nav" aria-label="{name} 문서">{a}</nav>', a.replace(' aria-current="page"', ' aria-current="page"')


def top_nav(prefix, name, sub=False):
    parent = f'<a href="./{prefix}.html">{name}</a>' if os.path.exists(SITE + prefix + ".html") else f'<span class="nolink">{name}</span>'
    up = f'<a href="./{prefix}-athletes.html">↑ {name} 한국 선수</a>' if sub else ""
    return (f'<nav class="sport-nav" aria-label="상위 문서">{parent}{up}</nav>'
            f'<a class="athlete-link" href="./{prefix}-athletes.html"' + ("" if sub else ' aria-current="page"') + f'>{ICON}<span>한국 선수</span></a>')


def footer_nav(prefix, name):
    _, a = tabs_html(prefix, name, cur_athletes=False)
    return f'<a href="{INDEX}">← 올림픽예선 목차</a>' + a


# ------------------------------------------------------------------ 선수 문서 (관심 개인종목)
def person_page(prefix, name, p, blank=False):
    slug = p["slug"]
    if blank:
        box = infobox(e(p["name"]), [("종목", name), ("분류", "관심 개인종목"), ("상태", "문서 작성 예정")])
        main = toc([("overview", "개요"), ("results", "주요 성적"), ("sources", "출처")]) + \
            '<section id="overview"><h2>개요</h2>' + STUB + '</section><section id="results"><h2>주요 성적</h2><p class="stub">작성 예정.</p></section>' \
            '<section id="sources"><h2>출처</h2><p class="stub">출처 추가 예정.</p></section>'
        intro = f"{e(p['name'])} — {name} 한국 선수 문서입니다. 내용은 추후 작성합니다."
    else:
        sexw = {"남": "남자", "여": "여자"}.get(p.get("sex"), "")
        rows = [("영문 이름", e(p.get("name_en"))), ("성별", sexw), ("출생", e(age(p.get("birth"))) if p.get("birth") else ""),
                ("출생지", e(p.get("birthplace"))), ("소속", e(p.get("affiliation"))),
                ("신장", f'{p["height_cm"]} cm' if p.get("height_cm") else ""), ("종목", name), ("세부종목", e(p.get("discipline"))),
                ("랭킹", e(p.get("ranking"))), ("최근", e(p.get("status_note")))]
        box = infobox(e(p["name"]), rows, f'<p class="small"><a href="./{prefix}.html">{name} LA28 예선 안내 →</a></p>' if os.path.exists(SITE + prefix + ".html") else "")
        oly = p.get("olympics") or []
        olyh = ("<ul>" + "".join(f"<li>{e(x)}</li>" for x in oly) + "</ul>") if oly else '<p class="stub">올림픽 출전 기록 없음(또는 미확인).</p>'
        main = (toc([("overview", "개요"), ("results", "주요 성적"), ("olympics", "올림픽"), ("sources", "출처")])
                + f'<section id="overview"><h2>개요</h2>{STUB}</section>'
                + f'<section id="results"><h2>주요 성적</h2>{results_table(p.get("results"))}</section>'
                + f'<section id="olympics"><h2>올림픽</h2>{olyh}</section>'
                + f'<section id="sources"><h2>출처</h2>{sources_list(p.get("sources", []))}<p class="small">기본 정보 기준일 {EDIT}. 확인하지 못한 항목은 비워 두었습니다.</p></section>')
        en = f"({e(p['name_en'])})" if p.get("name_en") else ""
        intro = f"<b>{e(p['name'])}</b>{en}은 대한민국의 {name} 선수다." + (f" 주종목은 {e(p['discipline'])}." if p.get("discipline") else "")
    tabs, _ = tabs_html(prefix, name)
    return page(f"{p['name']} | {name} 한국 선수", f"{p['name']} — {name} 한국 선수 기본 정보", top_nav(prefix, name, True),
                e(p["name"]), intro, tabs, main, box, footer_nav(prefix, name), f"{name} · 한국 선수 | 기본 정보 기준 {EDIT}")


def others_page(prefix, name, others, slug="others", label="기타 선수", blank=False):
    if blank or not others:
        body = '<p class="stub">작성 예정.</p>'
    else:
        rows = "".join(f'<tr><th scope="row">{e(o["name"])}</th><td>{e({"남": "남", "여": "여"}.get(o.get("sex"), ""))}</td><td>{e(o.get("discipline"))}</td>'
                       f'<td>{e(o.get("note"))}</td><td>' + (f'<a href="{e(o["source_url"])}">출처</a>' if o.get("source_url") else "") + "</td></tr>" for o in others)
        body = ('<table class="data"><caption>기타 주요 선수 · 기본 정보</caption><thead><tr><th scope="col">선수</th><th scope="col">성별</th>'
                f'<th scope="col">세부종목</th><th scope="col">확인한 성적</th><th scope="col">근거</th></tr></thead><tbody>{rows}</tbody></table>')
    main = toc([("list", label), ("note", "비고")]) + f'<section id="list"><h2>{label}</h2>{body}</section><section id="note"><h2>비고</h2>{STUB}</section>'
    box = infobox(f"{name} · {label}", [("종목", name), ("분류", "관심 개인종목"), ("인원", f"{len(others)}명" if others and not blank else "작성 예정"), ("기준일", EDIT)])
    tabs, _ = tabs_html(prefix, name)
    return page(f"{label} | {name} 한국 선수", f"{name} {label}", top_nav(prefix, name, True), f"{name} {label}",
                f"개별 문서가 없는 {name} 한국 선수를 모은 문서입니다.", tabs, main, box, footer_nav(prefix, name), f"{name} · 한국 선수 | 기준 {EDIT}")


def interest_hub(key, prefix, name, persons, others, blank_list=None):
    if blank_list:
        rows = "".join(f'<tr><th scope="row"><a href="./{prefix}-p-{s}.html">{n}</a></th><td colspan="3" class="muted">문서 작성 예정</td></tr>' for s, n in blank_list)
    else:
        rows = ""
        for p in persons:
            rows += (f'<tr><th scope="row"><a href="./{prefix}-p-{p["slug"]}.html">{e(p["name"])}</a></th><td>{e(p.get("discipline"))}</td>'
                     f'<td>{e(age(p.get("birth")) or "—")}</td><td>{e(p.get("status_note") or "")}</td></tr>')
        rows += (f'<tr><th scope="row"><a href="./{prefix}-p-others.html">기타</a></th><td colspan="3">' +
                 (", ".join(e(o["name"]) for o in others) if others else "작성 예정") + "</td></tr>")
    table = ('<table class="data"><caption>선수 문서</caption><thead><tr><th scope="col">선수</th><th scope="col">세부종목</th>'
             f'<th scope="col">출생</th><th scope="col">최근 주요 성적</th></tr></thead><tbody>{rows}</tbody></table>')
    allsrc = [s for p in persons for s in p.get("sources", [])]
    if key == "boxing":
        crow = ""
        for gl, items in EV["boxingw"][2]:
            for c, l in items:
                ns = ", ".join(a["name"] for a in D["boxingw"]["events"].get(c, {}).get("athletes", []))
                crow += f'<tr><th scope="row"><a href="./olboxing-ev-{c}.html">{l}</a></th><td>{WR.total("boxingw", c)}</td><td>{e(ns) or "<span class=muted>—</span>"}</td></tr>'
        table += ('<h3 id="classes">체급별 문서</h3><table class="data"><caption>체급별 예선 규정·한국 선수</caption><thead><tr><th scope="col">체급</th>'
                  f'<th scope="col">정원</th><th scope="col">한국 주요 선수</th></tr></thead><tbody>{crow}</tbody></table>')
    main = (toc([("list", "선수 문서"), ("about", "문서 기준"), ("sources", "출처")])
            + f'<section id="list"><h2>선수 문서</h2>{table}</section>'
            + '<section id="about"><h2>문서 기준</h2><p>관심 개인종목으로 분류한 종목의 한국 주요 선수입니다. 각 문서는 위키 스타일의 기본 정보(출생·소속·주요 수상 성적)만 담고, 본문은 추후 작성합니다. '
              '확인하지 못한 항목은 비워 두었습니다.</p></section>'
            + f'<section id="sources"><h2>출처</h2>{sources_list(allsrc) if allsrc else "<p class=stub>출처 추가 예정.</p>"}</section>')
    n = len(blank_list) if blank_list else len(persons)
    box = infobox(f"{name} · 한국 선수", [("분류", "관심 개인종목"), ("선수 문서", f"{n}개" + ("" if blank_list else " + 기타")), ("기준일", EDIT)],
                  f'<p class="small"><a href="./{prefix}.html">{name} LA28 예선 안내 →</a></p>' if os.path.exists(SITE + prefix + ".html") else "")
    tabs, _ = tabs_html(prefix, name)
    return page(f"한국 선수 | {name} · 올림픽예선", f"LA28 {name} 한국 주요 선수 문서 목록", top_nav(prefix, name), f"{name} 한국 선수",
                f"LA28을 향한 한국 {name} 주요 선수 문서 목록입니다.", tabs, main, box, footer_nav(prefix, name), f"{name} · 한국 선수 | 기준 {EDIT}")


# ------------------------------------------------------------------ 세부종목·체급 문서
def ath_block(a):
    sexw = {"남": "남자", "여": "여자"}.get(a.get("sex"), "")
    meta = [("영문", a.get("name_en")), ("성별", sexw), ("출생", age(a.get("birth"))), ("소속", a.get("affiliation")),
            ("파트너", a.get("pair")), ("개인기록", a.get("pb")), ("랭킹", a.get("ranking"))]
    dl = "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in meta if v)
    link = f' <a class="small" href="./{a["link"]}">선수 문서 →</a>' if a.get("link") else ""
    note = f'<p class="small">{e(a["note"])}</p>' if a.get("note") else ""
    res = results_table(a.get("results"), e(a["name"]) + " 주요 성적") if (a.get("results") or not note) else ""
    return (f'<div class="ath-block"><h3>{e(a["name"])}{link}</h3><dl class="ath-meta">{dl}</dl>{note}{res}</div>')


def event_page(key, code, label, data, group_label):
    prefix, name, _ = EV[key]
    srcs = list(data.get("sources", []))
    if key == "swimming":
        secs = []
        for g, gl in (("men", "남자"), ("women", "여자")):
            lst = data.get(g, [])
            for a in lst: srcs += a.get("sources", [])
            body = "".join(ath_block(a) for a in lst) if lst else '<p class="stub">현재 정리된 한국 주요 선수 없음 · 추후 작성.</p>'
            secs.append((g, f"{gl} {label}", body))
        names = [a["name"] for g in ("men", "women") for a in data.get(g, [])]
    else:
        lst = data.get("athletes", [])
        for a in lst: srcs += a.get("sources", [])
        body = "".join(ath_block(a) for a in lst) if lst else '<p class="stub">현재 정리된 한국 주요 선수 없음 · 추후 작성.</p>'
        secs = [("athletes", "한국 주요 선수", body)]
        names = [a["name"] for a in lst]
        if key in WEIGHT:
            secs.insert(0, ("rules", f"{label} 예선 규정", WR.rule_html(key, code, label)))
            srcs.insert(0, {"title": WR.src_title(key), "url": WR.rule_pdf(key)})
    note = f'<div class="notice">{e(data["note"])}</div>' if data.get("note") else ""
    main = (toc([(a, b) for a, b, _ in secs] + [("overview", "개요"), ("sources", "출처")])
            + "".join(f'<section id="{a}"><h2>{b}</h2>{c}</section>' for a, b, c in secs)
            + f'<section id="overview"><h2>개요</h2>{note}{STUB}</section>'
            + f'<section id="sources"><h2>출처</h2>{sources_list(srcs)}<p class="small">기본 정보 기준일 {EDIT}. 확인하지 못한 항목은 비워 두었습니다.</p></section>')
    rule = ev_rule_page(key, code)
    box = infobox(f"{name} · {label}", [("종목", name), ("구분", group_label), ("세부종목", label), ("한국 주요 선수", ", ".join(names) or "—"), ("기준일", EDIT)],
                  f'<p class="small"><a href="./{rule}">{"성별 예선 규정 전체" if key in WEIGHT else "이 세부종목 LA28 예선 규정"} →</a></p>')
    if key in WEIGHT:
        tabs, _ = tabs_html(prefix, name, cur=rule)
        tl = dict(sport_tabs(prefix)).get(rule, "")
        nav = (f'<nav class="sport-nav" aria-label="상위 문서"><a href="./{prefix}.html">{name}</a><a href="./{rule}">↑ {name} {tl}</a></nav>'
               f'<a class="athlete-link" href="./{prefix}-athletes.html">{ICON}<span>한국 선수</span></a>')
        return page(f"{label} | {name} · 올림픽예선", f"LA28 {name} {label} 예선 규정과 한국 주요 선수", nav, f"{name} {label}",
                    f"LA28 {name} <b>{label}</b>의 체급별 예선 규정과 한국 주요 선수 기본 정보입니다.", tabs, main, box, footer_nav(prefix, name), f"{name} · {label} | 규정 {WR.PDF[key][2]}판 · 기준 {EDIT}")
    tabs, _ = tabs_html(prefix, name)
    return page(f"{label} | {name} 한국 선수", f"LA28 {name} {label} 한국 주요 선수", top_nav(prefix, name, True), f"{name} {label}",
                f"LA28 {name} <b>{label}</b> 세부종목의 한국 주요 선수 기본 정보입니다.", tabs, main, box, footer_nav(prefix, name), f"{name} · 한국 선수 | 기준 {EDIT}")


def event_hub(key):
    prefix, name, groups = EV[key]
    ev = D[key]["events"]
    secs, tocs = "", []
    for gi, (gl, items) in enumerate(groups):
        rows = ""
        for code, label in items:
            d = ev.get(code, {})
            if key == "swimming":
                ns = [a["name"] for a in d.get("men", [])] + [a["name"] for a in d.get("women", [])]
            else:
                ns = [a["name"] for a in d.get("athletes", [])]
            ns = list(dict.fromkeys(ns))
            rows += f'<tr><th scope="row"><a href="./{prefix}-ev-{code}.html">{label}</a></th><td>{e(", ".join(ns)) or "<span class=muted>추후 작성</span>"}</td></tr>'
        sid = f"g{gi + 1}"
        tocs.append((sid, gl))
        secs += (f'<section id="{sid}"><h2>{gl}</h2><table class="data"><caption>{gl} · 세부종목별 문서</caption><thead><tr><th scope="col">세부종목</th>'
                 f'<th scope="col">한국 주요 선수</th></tr></thead><tbody>{rows}</tbody></table></section>')
    n = sum(len(i) for _, i in groups)
    unit = "체급" if key in WEIGHT else "세부종목"
    main = toc(tocs + [("about", "문서 기준")]) + secs + \
        (f'<section id="about"><h2>문서 기준</h2><p>{name}은 {unit}별로 별도 문서를 둡니다. 각 문서는 한국 주요 선수의 기본 정보(출생·소속·주요 수상 성적)만 담고, 본문은 추후 작성합니다. '
         + ("경영은 남녀를 한 문서의 두 섹션으로 나눴습니다. " if key == "swimming" else "") + "확인하지 못한 항목은 비워 두었습니다.</p></section>")
    box = infobox(f"{name} · 한국 선수", [("분류", f"{unit}별 선수 문서"), ("문서 수", f"{n}개"), ("기준일", EDIT)],
                  f'<p class="small"><a href="./{prefix}.html">{name} LA28 예선 안내 →</a></p>')
    tabs, _ = tabs_html(prefix, name)
    return page(f"한국 선수 | {name} · 올림픽예선", f"LA28 {name} {unit}별 한국 주요 선수", top_nav(prefix, name), f"{name} 한국 선수",
                f"LA28 {name} {unit}별 한국 주요 선수 문서 목록입니다.", tabs, main, box, footer_nav(prefix, name), f"{name} · 한국 선수 | 기준 {EDIT}")


# ------------------------------------------------------------------ 기존 문서 수정
def patch_existing(prefix, name):
    files = [f for f in glob.glob(SITE + prefix + "*.html")
             if "_1" not in f and not re.search(r"-(athletes|p-[a-z-]+|ev-[a-z0-9]+)\.html$", f)
             and os.path.basename(f)[len(prefix)] in ".-"]
    for f in files:
        t = open(f, encoding="utf-8", newline="").read()
        o = t
        t = t.replace("koreaolympics.github.io/index1.html", "koreaolympics.github.io/index.html")
        link = f"./{prefix}-athletes.html"
        if 'class="athlete-link"' not in t:
            t = re.sub(r'(<header class="topbar"><div class="topbar-inner">.*?</nav>)', lambda m: m.group(1) + f'<a class="athlete-link" href="{link}">{ICON}<span>한국 선수</span></a>', t, count=1, flags=re.S)
        m = re.search(r'<nav class="golf-nav"[^>]*>.*?</nav>', t, re.S)
        if m and "section-nav" not in m.group(0) and link not in m.group(0):
            t = t[:m.end() - 6] + f'<a href="{link}">한국 선수</a>' + t[m.end() - 6:]
        m = re.search(r'<nav class="footer-nav"[^>]*>.*?</nav>', t, re.S)
        if m and link not in m.group(0):
            t = t[:m.end() - 6] + f'<a href="{link}">한국 선수</a>' + t[m.end() - 6:]
        if t != o:
            open(f, "w", encoding="utf-8", newline="").write(t)
    return len(files)


CSS_MARK = "/* == athletes (한국 선수 문서) == */"
CSS = (CSS_MARK + "\n.athlete-link{display:inline-flex;align-items:center;gap:5px;padding:2px 10px;border:1px solid var(--line);border-radius:999px;color:var(--link);font-size:13px;line-height:1.6;white-space:nowrap}"
       ".athlete-link:hover{background:var(--soft);text-decoration:none}.athlete-link[aria-current=page]{color:var(--ink);font-weight:700;border-color:var(--ink)}"
       ".athlete-link .ath-ic{flex:none}.nolink{color:var(--ink);font-weight:700}"
       ".stub{background:var(--soft);border:1px solid #eaecf0;border-left:3px solid #a2a9b1;padding:10px 14px;color:var(--muted);font-size:14px}"
       ".ath-block{border-top:1px solid #eaecf0;margin-top:18px;padding-top:4px}.ath-block h3{margin:10px 0 6px}"
       ".ath-meta{display:grid;grid-template-columns:90px minmax(0,1fr);gap:3px 12px;font-size:14px;margin:6px 0 10px}.ath-meta dt{color:var(--muted)}.ath-meta dd{margin:0}"
       + WR.CSS + ".ath-res td.m-g{font-weight:700}.ath-res td.m-s,.ath-res td.m-b{font-weight:600}.muted{color:var(--muted)}"
       "@media(max-width:900px){.infobox.ath-box{display:block;order:-1;margin:0 0 14px}}@media print{.infobox.ath-box{display:block}}@media(max-width:600px){.athlete-link span{display:none}.athlete-link{padding:3px 7px}.ath-meta{grid-template-columns:72px minmax(0,1fr)}}\n")


def patch_css():
    f = SITE + "css/olympic-wiki.css"
    t = open(f, encoding="utf-8", newline="").read()
    if CSS_MARK in t:
        t = t[:t.index(CSS_MARK)]
    nl = "\r\n" if "\r\n" in t else "\n"
    if not t.endswith(("\n", "\r\n")): t += nl
    open(f, "w", encoding="utf-8", newline="").write(t + CSS.replace("\n", nl))


# ------------------------------------------------------------------ index.html
IDX_MARK_S, IDX_MARK_E = "<!-- athletes-tab:start -->", "<!-- athletes-tab:end -->"


def patch_index():
    f = SITE + "index.html"
    t = open(f, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    # 탭 버튼
    if 'id="b-athletes"' not in t:
        t = t.replace('<button class="tab-btn" id="b-ranking"', '<button class="tab-btn" id="b-athletes" onclick="showTab(\'t-athletes\',this)">🏅 한국 선수</button>' + nl + '    <button class="tab-btn" id="b-ranking"', 1)
    # 패널
    cards = ""
    for key, prefix, name, order in INTEREST:
        if key == "athletics":
            ppl = [n for _, n in ATHLETICS]
            links = " · ".join(f'<a href="{prefix}-p-{s}.html">{n}</a>' for s, n in ATHLETICS)
        else:
            ps = D[key]["persons"]
            links = " · ".join(f'<a href="{prefix}-p-{p["slug"]}.html">{e(p["name"])}</a>' for p in ps) + f' · <a href="{prefix}-p-others.html">기타</a>'
        cards += f'<tr><th><a href="{prefix}-athletes.html">{name}</a></th><td>{links}</td></tr>'
    evrows = ""
    for key, (prefix, name, groups) in EV.items():
        if key == "boxingw":
            continue
        n = sum(len(i) for _, i in groups)
        unit = "체급" if key in WEIGHT else "세부종목"
        evrows += f'<tr><th><a href="{prefix}-athletes.html">{name}</a></th><td>{unit}별 문서 {n}개 · ' + " · ".join(f'<a href="{prefix}-athletes.html#g{i + 1}">{gl}</a>' for i, (gl, _) in enumerate(groups)) + "</td></tr>"
    panel = (f'{IDX_MARK_S}{nl}  <div class="tab-panel" id="t-athletes">{nl}'
             f'    <div class="cat">한국 선수 <span class="cnt">관심 개인종목 9 · 세부종목·체급별 9 · 기본 정보 기준 {EDIT}</span></div>{nl}'
             '    <p class="infoline">종목 문서 상단의 <b>👤 한국 선수</b> 아이콘에서도 열 수 있습니다. 각 선수 문서는 기본 정보(출생·소속·주요 수상 성적)만 담고, 본문은 추후 작성합니다.</p>' + nl +
             f'    <h2>관심 개인종목</h2>{nl}    <table class="wt"><tr><th>종목</th><th>선수 문서</th></tr>{cards}</table>{nl}'
             f'    <h2>세부종목·체급별 선수</h2>{nl}    <table class="wt"><tr><th>종목</th><th>세부 문서</th></tr>{evrows}</table>{nl}'
             f'  </div>{nl}{IDX_MARK_E}{nl}')
    if IDX_MARK_S in t:
        t = t[:t.index(IDX_MARK_S)] + panel + t[t.index(IDX_MARK_E) + len(IDX_MARK_E) + len(nl):]
    else:
        i = t.index('<div class="tab-panel" id="t-ranking">')
        i = t.rfind(nl, 0, i) + len(nl)
        t = t[:i] + panel + t[i:]
    # 전체 종목 카드에 '관심' 표시
    for key, prefix, name, _ in INTEREST:
        if key == "athletics": continue
        t = re.sub(rf'(<div class="nm"><a href="{prefix}\.html">{name}</a>)(?!<span class="tag interest">)', rf'\1<span class="tag interest">관심</span>', t, count=1)
    if ".tag.interest" not in t:
        t = t.replace(".tag.merge{", ".tag.interest{background:#eef0f2;color:#202122;border:1px solid #a2a9b1;}.tag.merge{", 1)
    open(f, "w", encoding="utf-8", newline="").write(t)


def write(name, t):
    open(SITE + name + ".html", "w", encoding="utf-8", newline="\r\n").write(t)


if __name__ == "__main__":
    from fencing_pages import preserve_hub, finish_generation
    fencing_hub = preserve_hub()
    n = 0
    for key, prefix, name, order in INTEREST:
        if key == "athletics":
            for s, nm in ATHLETICS:
                write(f"{prefix}-p-{s}", person_page(prefix, name, {"slug": s, "name": nm}, blank=True)); n += 1
            write(f"{prefix}-athletes", interest_hub(key, prefix, name, [], [], ATHLETICS)); n += 1
            continue
        ps = D[key]["persons"]
        ps.sort(key=lambda p: order.index(p["name"]) if p["name"] in order else 99)
        for p in ps:
            write(f"{prefix}-p-{p['slug']}", person_page(prefix, name, p)); n += 1
        write(f"{prefix}-p-others", others_page(prefix, name, D[key].get("others", []))); n += 1
        write(f"{prefix}-athletes", interest_hub(key, prefix, name, ps, D[key].get("others", []))); n += 1
        print(key, "persons", len(ps), "patched", patch_existing(prefix, name))
    for key, (prefix, name, groups) in EV.items():
        for gl, items in groups:
            for code, label in items:
                write(f"{prefix}-ev-{code}", event_page(key, code, label, D[key]["events"].get(code, {}), gl)); n += 1
        if key == "boxingw":
            continue
        write(f"{prefix}-athletes", event_hub(key)); n += 1
        print(key, "events", sum(len(i) for _, i in groups), "patched", patch_existing(prefix, name))
    patch_css()
    patch_index()
    finish_generation(fencing_hub)
    from taekwondo_pages import update_pages
    update_pages()
    print("pages written", n)
