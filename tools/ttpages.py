# -*- coding: utf-8 -*-
"""탁구 문서 생성기: 전체 안내 + 세부종목 6개 + 쿼터 트래킹.
실행: 사이트 루트에서  python3 tools/ttpages.py
쿼터 기록: tools/tt/live.json 편집 후 재실행."""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE) + "/"
DATA = json.load(open(os.path.join(HERE, "tt", "live.json"), encoding="utf-8"))
PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/TTE-LA28-Qualification-System.pdf"
WIKI24 = "https://en.wikipedia.org/wiki/Table_tennis_at_the_2024_Summer_Olympics_%E2%80%93_Qualification"
WC25 = "https://en.wikipedia.org/wiki/2025_ITTF_Mixed_Team_World_Cup"
WCALL = "https://en.wikipedia.org/wiki/ITTF_Mixed_Team_World_Cup"
AG26 = "https://www.olympics.com/ko/news/team-korea-all-results-table-tennis-asian-games-2026"
CHECK = "2026.10.05"
e = html.escape
FONT = "Arial, Malgun Gothic, sans-serif"

# 경로 색
C = {"cont": "#2a7f62", "world": "#2456c6", "wr": "#c77d12", "host": "#8a8f98", "add": "#b04a4a",
     "uni": "#5b5f66", "team": "#1f6f8b", "men": "#2456c6", "women": "#75548c", "mixed": "#c2571a"}

EVENTS = [  # key, file, 이름, 짧은 이름
    ("xt", "oltabletennis-team.html", "혼성 단체", "혼성 단체"),
    ("xd", "oltabletennis-xd.html", "혼합복식", "혼합복식"),
    ("md", "oltabletennis-md.html", "남자 복식", "남자 복식"),
    ("wd", "oltabletennis-wd.html", "여자 복식", "여자 복식"),
    ("ms", "oltabletennis-ms.html", "남자 단식", "남자 단식"),
    ("ws", "oltabletennis-ws.html", "여자 단식", "여자 단식"),
]
MAIN, LIVE = "oltabletennis.html", "oltabletennis-live.html"
FILE = {k: f for k, f, *_ in EVENTS}

CSS = ("<style>.tt-fig{margin:12px 0 18px;padding:12px 14px;background:#f8f9fa;border:1px solid #eaecf0}"
       ".tt-fig svg{display:block;width:100%;height:auto;max-width:900px}"
       ".tt-fig figcaption{font-size:13px;color:#54595d;margin-top:8px;line-height:1.6}"
       ".tt-key{border-left:4px solid #c2571a;background:#fdf3ec;padding:14px 18px;margin:16px 0}"
       ".tt-key strong.big{display:block;font-size:20px;color:#8f3d10;margin-bottom:4px}"
       ".tt-change{border:1px solid #c8ccd1;border-top:4px solid #1f6f8b;padding:14px 18px;margin:0 0 18px;background:#fff}"
       ".tt-change h2{margin-top:0;border:0}"
       ".tt-sc td,.tt-sc th{font-size:14px}.tt-sc .kor-row th,.tt-sc .kor-row td{background:#fff8d8}"
       ".chip{display:inline-block;font-size:11px;font-weight:700;padding:0 6px;border-radius:9px;color:#fff;margin-right:3px;vertical-align:1px}"
       ".st{display:inline-block;font-size:11px;font-weight:700;padding:0 6px;border-radius:9px;border:1px solid #a2a9b1;color:#54595d;margin-left:4px;vertical-align:1px}"
       ".st-확정{color:#202122;border-color:#202122}.st-잠정{color:#3366cc;border-color:#3366cc}.st-조건부{color:#54595d;border-style:dotted}"
       ".tbd{color:#72777d}.live-log td:first-child{white-space:nowrap}.qs td,.qs th{text-align:center}.qs th[scope=row]{text-align:left;min-width:110px}"
       ".qs tfoot td,.qs tfoot th{font-weight:700;background:#eaecf0}.fn{font-size:11px;vertical-align:super;margin-left:2px}"
       ".howto{font-size:14px}.howto code{background:#f8f9fa;border:1px solid #eaecf0;padding:0 4px}"
       ".tt-wrap{overflow-x:auto}.rule-no{color:#54595d;font-size:12px;font-weight:400}"
       "@media(max-width:600px){.tt-fig{overflow-x:auto}.tt-fig svg{min-width:620px}.qs{font-size:12px}.qs th,.qs td{padding:5px 3px}}</style>")


# ------------------------------------------------------------------ 공통 틀
def head(title, desc):
    return ('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="description" content="{e(desc)}"><title>{e(title)} | 탁구 · 올림픽예선</title>'
            f'<link rel="stylesheet" href="./css/olympic-wiki.css">{CSS}</head><body><a class="skip" href="#main">본문 바로가기</a>')


def topbar(is_main):
    up = ('<a href="./oltabletennis.html" aria-current="page">탁구</a>' if is_main
          else '<a href="./oltabletennis.html">↑ 탁구 전체 안내</a>')
    return ('<header class="topbar"><div class="topbar-inner"><a href="https://koreaolympics.github.io/index.html">← 올림픽예선 목차</a>'
            f'<nav class="sport-nav" aria-label="상위 문서">{up}</nav><span>LA28 · 종목별 예선</span></div></header>')


def a(href, label, cur):
    return f'<a href="./{href}"' + (' aria-current="page"' if href == cur else '') + f'>{label}</a>'


def navs(cur):
    row1 = ('<nav class="golf-nav" aria-label="탁구 문서">' + a(MAIN, "전체 안내", cur)
            + a(LIVE, "쿼터 트래킹", cur) + '</nav>')
    row2 = ('<nav class="golf-nav sub-nav" aria-label="탁구 세부 종목"><span class="sub-label">세부 종목</span>'
            + "".join(a(f, n, cur) for k, f, n, s in EVENTS) + '</nav>')
    return row1 + row2


def footer(cur, note):
    links = ('<a href="https://koreaolympics.github.io/index.html">← 올림픽예선 목차</a>' + a(MAIN, "전체 안내", cur)
             + "".join(a(f, n, cur) for k, f, n, s in EVENTS) + a(LIVE, "쿼터 트래킹", cur))
    return (f'<footer class="footer"><nav class="footer-nav" aria-label="하단 탁구 문서">{links}</nav>'
            f'<p>탁구 · 올림픽예선 | {note}</p><a href="#main">본문 위로 ↑</a></footer>')


def toc(items):
    return ('<nav class="toc" aria-label="이 문서의 목차"><strong>목차</strong><ol>'
            + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + '</ol></nav>')


def infobox(title, rows):
    return (f'<aside class="infobox" aria-label="{e(title)} 요약"><h2>{e(title)}</h2><dl>'
            + "".join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows)
            + f'</dl><p class="small"><a href="{PDF}">ITTF 공식 예선 규정 ↗</a></p></aside>')


def page(fname, title, h1, intro, desc, items, body, box_title, box_rows, note):
    t = (head(title, desc) + topbar(fname == MAIN) + f'<div class="shell"><h1 class="title">{h1}</h1><p class="intro">{intro}</p>'
         + navs(fname) + '<div class="columns"><main id="main">' + toc(items) + body + '</main>'
         + infobox(box_title, box_rows) + '</div>' + footer(fname, note) + '</div></body></html>\n')
    open(SITE + fname, "w", encoding="utf-8", newline="\r\n").write(t)
    return fname


def table(head_cells, rows, cls="data", caption=None, foot=None):
    t = f'<div class="tt-wrap"><table class="{cls}">' + (f'<caption>{caption}</caption>' if caption else '')
    t += '<thead><tr>' + "".join(f'<th scope="col">{h}</th>' for h in head_cells) + '</tr></thead><tbody>'
    for r in rows:
        tr_cls = ''
        if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], str) and r[1].startswith("class:"):
            r, tr_cls = r[0], f' class="{r[1][6:]}"'
        t += f'<tr{tr_cls}><th scope="row">{r[0]}</th>' + "".join(f'<td>{c}</td>' for c in r[1:]) + '</tr>'
    t += '</tbody>' + (f'<tfoot>{foot}</tfoot>' if foot else '') + '</table></div>'
    return t


def fig(svg, cap):
    return f'<figure class="tt-fig">{svg}<figcaption>{cap}</figcaption></figure>'


def chip(label, color):
    return f'<span class="chip" style="background:{color}">{label}</span>'


# ------------------------------------------------------------------ SVG
def T(x, y, s, size=13, w=400, fill="#202122", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{e(s)}</text>')


def R(x, y, w, h, fill, stroke=None, rx=4, dash=False, op=1):
    st = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ''
    if dash: st += ' stroke-dasharray="4 3"'
    o = f' fill-opacity="{op}"' if op != 1 else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{o}{st}/>'


def svg(w, h, label, inner):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}"><g font-family="{FONT}">{inner}</g></svg>')


EVC = {"단식": "#4f6b8a", "복식": "#75548c", "단체": "#1f6f8b", "혼합복식": "#c2571a", "혼성 단체": "#a33b1a"}


def svg_history():
    cols = [
        ("1988–2004", "서울 → 아테네 (6회)", [("남자 단식", "단식"), ("여자 단식", "단식"), ("남자 복식", "복식"), ("여자 복식", "복식")], "4종목"),
        ("2008–2016", "베이징 → 리우 (3회)", [("남자 단식", "단식"), ("여자 단식", "단식"), ("남자 단체", "단체"), ("여자 단체", "단체")], "4종목"),
        ("2020–2024", "도쿄 → 파리 (2회)", [("남자 단식", "단식"), ("여자 단식", "단식"), ("남자 단체", "단체"), ("여자 단체", "단체"), ("혼합복식", "혼합복식")], "5종목"),
        ("2028 LA", "이번 대회", [("혼성 단체", "혼성 단체"), ("혼합복식", "혼합복식"), ("남자 복식", "복식"), ("여자 복식", "복식"), ("남자 단식", "단식"), ("여자 단식", "단식")], "6종목"),
    ]
    o = T(14, 22, "올림픽 탁구 세부종목의 변천", 15, 700)
    cw, x0 = 222, 14
    for i, (yr, sub, evs, cnt) in enumerate(cols):
        x = x0 + i * (cw + 8)
        last = i == 3
        o += R(x, 36, cw, 296, "#fff" if not last else "#fff7f0", "#c2571a" if last else "#c8ccd1", 6)
        o += T(x + 12, 60, yr, 15, 700, "#a33b1a" if last else "#202122")
        o += T(x + cw - 12, 60, cnt, 13, 700, "#a33b1a" if last else "#54595d", "end")
        o += T(x + 12, 78, sub, 11.5, 400, "#54595d")
        for j, (n, typ) in enumerate(evs):
            y = 92 + j * 38
            o += R(x + 12, y, cw - 24, 28, EVC[typ], None, 5)
            o += T(x + 24, y + 19, n, 13, 700, "#fff")
            tag = ""
            if last and n == "혼성 단체": tag = "신설"
            if last and n in ("남자 복식", "여자 복식"): tag = "24년 만에 부활"
            if i == 2 and n in ("남자 단체", "여자 단체"): tag = "LA28 폐지"
            if tag:
                tw = 12 + len(tag) * 11.5
                o += R(x + cw - 18 - tw, y + 5, tw, 18, "#fff", None, 9)
                o += T(x + cw - 18 - tw / 2, y + 18, tag, 11, 700, EVC[typ], "middle")
        if i < 3:
            o += f'<path d="M{x + cw + 1} 184 l6 -6 v12 z" fill="#a2a9b1"/>'
    # legend
    lx = 14
    for n in ["단식", "복식", "단체", "혼합복식", "혼성 단체"]:
        o += R(lx, 344, 12, 12, EVC[n], None, 2) + T(lx + 17, 354, n, 12)
        lx += 30 + len(n) * 13
    o += T(934, 354, "인원은 계속 172명 (남 86 · 여 86)", 12, 700, "#54595d", "end")
    return svg(948, 366, "올림픽 탁구 세부종목 변천: 1988–2004 단식·복식 4종목, 2008–2016 단식·단체 4종목, 2020–2024 혼합복식 추가 5종목, 2028 혼성 단체·혼합복식·남녀 복식·남녀 단식 6종목", o)


def svg_six():
    players = [("남1", "men"), ("남2", "men"), ("남3", "men"), ("여1", "women"), ("여2", "women"), ("여3", "women")]
    rows = [  # 종목, 출전 선수 인덱스, 색, 메모
        ("혼성 단체", [0, 1, 2, 3, 4, 5], EVC["혼성 단체"], "6명 전원 (쿼터 1장 = 남녀 3명씩)"),
        ("남자 단식", [0, 1], EVC["단식"], "국가당 2명 · 단체 쿼터에 자동 포함"),
        ("여자 단식", [3, 4], EVC["단식"], "국가당 2명 · 단체 쿼터에 자동 포함"),
        ("남자 복식", [1, 2], EVC["복식"], "국가당 1조 · 별도 경로로 확보"),
        ("여자 복식", [4, 5], EVC["복식"], "국가당 1조 · 별도 경로로 확보"),
        ("혼합복식", [0, 3], EVC["혼합복식"], "국가당 1조 · 별도 경로로 확보"),
        ("혼합복식 2조", [2, 5], EVC["혼합복식"], "세계 8위 안에 2조일 때만 (예외)"),
    ]
    o = T(14, 22, "강국의 목표: 남녀 3명씩 6명으로 6종목 전부 출전", 15, 700)
    x0, cx = 150, 52
    for i, (p, g) in enumerate(players):
        x = x0 + i * cx + (14 if i >= 3 else 0)
        col = C[g]
        o += f'<circle cx="{x}" cy="54" r="16" fill="{col}"/>' + T(x, 59, p, 12, 700, "#fff", "middle")
    o += T(x0 + cx, 88, "남자 3명 (상한)", 11.5, 700, C["men"], "middle")
    o += T(x0 + 4 * cx + 14, 88, "여자 3명 (상한)", 11.5, 700, C["women"], "middle")
    for r, (n, idx, col, memo) in enumerate(rows):
        y = 104 + r * 34
        dash = n == "혼합복식 2조"
        o += R(14, y, 920, 28, "#fff" if r % 2 else "#f8f9fa", "#eaecf0", 3)
        o += T(24, y + 19, n, 13, 700, col)
        for i in range(6):
            x = x0 + i * cx + (14 if i >= 3 else 0)
            if i in idx:
                if dash:
                    o += f'<circle cx="{x}" cy="{y + 14}" r="8" fill="#fff" stroke="{col}" stroke-width="2" stroke-dasharray="3 2"/>'
                else:
                    o += f'<circle cx="{x}" cy="{y + 14}" r="8" fill="{col}"/>'
            else:
                o += f'<circle cx="{x}" cy="{y + 14}" r="3" fill="#c8ccd1"/>'
        o += T(x0 + 5 * cx + 46, y + 19, memo, 12.5, 400, "#54595d" if not dash else "#72777d")
    y = 104 + len(rows) * 34 + 22
    o += T(14, y, "→ 선수는 6명 그대로인데 엔트리는 단식 4 · 복식 3조 · 단체 1팀. 한 선수가 최대 4종목(단식·복식·혼합복식·단체)에 나선다.", 13, 700, "#a33b1a")
    return svg(948, y + 14, "6명 출전 구조: 혼성 단체 6명, 남녀 단식 2명씩, 남녀 복식 1조씩, 혼합복식 1조(조건부 2조)를 같은 6명이 나눠 맡는다", o)


def bar(o, x, y, w, segs, total, h=30):
    cx = x
    for n, col, lab in segs:
        sw = w * n / total
        o += R(cx, y, sw - 1, h, col, None, 2)
        if lab and sw > 40:
            o += T(cx + sw / 2, y + 20, lab, 12.5, 700, "#fff", "middle")
        cx += sw
    return o


def svg_split():
    o = T(14, 22, "172석은 어떻게 나뉘나 — 파리 2024 실제 vs LA28 구조", 15, 700)
    x, w = 150, 770
    o += T(14, 64, "파리 2024", 13, 700) + T(14, 80, "실제 배정", 11.5, 400, "#54595d")
    o = bar(o, x, 52, w, [(66, "#1f6f8b", "6명 꽉 채운 11개국 = 66명"), (106, "#a7b4c2", "나머지 49개국 = 106명")], 172)
    o += T(x, 100, "남녀 단체가 따로여서 한쪽 성별만 단체를 딴 나라(포르투갈 남자, 미국·홍콩 여자 등)도 많았다.", 12, 400, "#54595d")
    o += T(14, 146, "LA28", 13, 700) + T(14, 162, "규정상 구조", 11.5, 400, "#54595d")
    o = bar(o, x, 134, w, [(96, "#a33b1a", "혼성 단체 16개국 × 6명 = 96명"), (76, "#e3b9a3", "그 외 76명")], 172)
    o += T(x, 182, "혼성 단체는 남녀가 다 강해야 딸 수 있다 → 단체국 = 6명을 채우는 '탁구 강국 묶음'.", 12, 400, "#54595d")
    # 성별 분해
    y = 222
    o += T(14, y, "성별 86석 분해 (남녀 같음)", 13, 700)
    y += 12
    segs = [(48, "#a33b1a", "단체국 48 (16×3)"), (21, C["cont"], "대륙 단식 21"),
            (10, C["wr"], "랭킹 ≤10"), (1, C["uni"], ""), (6, "#c8ccd1", "")]
    o = bar(o, x, y, w, segs, 86)
    sx = x + w * 80 / 86
    o += T(sx - w / 86 / 2, y - 4, "보편성 1 ↓", 11.5, 700, C["uni"], "end")
    o += T(x + w - 2, y + 48, "복식 전용 ≈6", 11.5, 700, "#54595d", "end")
    o += T(x, y + 82, "비단체국 38명 = 단식 32명(대륙 21 + 랭킹 최대 10 + 보편성 1) + 복식에만 나오는 선수. 단식은 64명으로 고정되므로", 12, 400, "#54595d")
    o += T(x, y + 100, "비단체국 복식 전용 선수가 늘면 랭킹 단식 자리(최대 10)가 그만큼 줄어든다 (D.1.23 · Note 2).", 12, 400, "#54595d")
    return svg(948, y + 114, "172석 분해: 파리 2024는 6명 꽉 채운 11개국 66명과 49개국 106명, LA28은 혼성 단체 16개국 96명과 그 외 76명. 성별 86석은 단체국 48, 대륙 단식 21, 랭킹 최대 10, 보편성 1, 복식 전용 약 6", o)


def svg_flow():
    steps = [("① 혼성 단체", "16팀", "D.1.1–5", EVC["혼성 단체"]), ("② 혼합복식", "16조", "D.1.6–10", EVC["혼합복식"]),
             ("③ 남자 복식", "16조", "D.1.11–15", EVC["복식"]), ("④ 여자 복식", "16조", "D.1.16–20", EVC["복식"]),
             ("⑤ 남녀 단식", "64명씩", "D.1.21–24", EVC["단식"])]
    o = T(14, 22, "배정 순서 (규정의 위계) — 앞 단계 결과가 뒤 단계 자격을 정한다", 15, 700)
    bw, gap = 170, 17
    for i, (n, q, d, col) in enumerate(steps):
        x = 14 + i * (bw + gap)
        o += R(x, 38, bw, 70, col, None, 6)
        o += T(x + bw / 2, 64, n, 14, 700, "#fff", "middle") + T(x + bw / 2, 84, q, 13, 700, "#fff", "middle")
        o += T(x + bw / 2, 100, d, 11, 400, "#fff", "middle")
        if i < 4:
            o += f'<path d="M{x + bw + 3} 73 h{gap - 8} m-6 -5 l6 5 l-6 5" stroke="#72777d" stroke-width="2" fill="none"/>'
    notes = [(0, "쿼터 1장 = 남녀 3명씩", "+ 남녀 단식 2명씩 자동"),
             (1, "추가 4조: 남녀 단식 선수가", "다 있는 NOC 우선"),
             (2, "추가 4조: 남자 단식", "2명 확보 NOC 우선"),
             (3, "추가 4조: 여자 단식", "2명 확보 NOC 우선"),
             (4, "단체국 32 + 대륙 21", "+ 랭킹 ≤10 + 보편성 1")]
    for i, l1, l2 in notes:
        x = 14 + i * (bw + gap)
        o += T(x + 4, 130, l1, 12, 400, "#202122") + T(x + 4, 147, l2, 12, 400, "#202122")
    o += f'<path d="M100 166 v14 h740 v-14" stroke="#b04a4a" stroke-width="1.6" fill="none" stroke-dasharray="5 3"/>'
    o += T(470, 198, "단, 혼성 단체 마지막 2장(D.1.5)은 복식·단식 결과를 다 본 뒤 2028.05.15에 '남녀 3명씩 이미 모은 나라'에게 준다", 12.5, 700, "#b04a4a", "middle")
    return svg(948, 212, "배정 순서: 혼성 단체, 혼합복식, 남자 복식, 여자 복식, 남녀 단식 순. 혼성 단체 추가 2장은 개인·복식 결과를 본 뒤 배정", o)


ROUTE_COLOR = [("대륙", C["cont"]), ("월드컵", C["world"]), ("세계 예선", C["world"]), ("세계랭킹", C["wr"]),
               ("랭킹", C["wr"]), ("개최국", C["host"]), ("추가", C["add"]), ("보편성", C["uni"]), ("확보국", C["team"])]


def rcolor(route):
    for k, c in ROUTE_COLOR:
        if k in route: return c
    return "#72777d"


def svg_slots(ev, title):
    rows = ev["rows"]
    total = ev["total"]
    per_row = 16
    size, gap = 48 if total <= 16 else 47, 8 if total <= 16 else 9
    if total > 16: size, gap = 47, 9
    o = T(14, 22, title, 15, 700)
    order = sorted(rows, key=lambda r: (0 if "확보국" in r["route"] else 1 if "대륙" in r["route"] or "(대륙" in r["route"] else
                                        2 if "월드컵" in r["route"] or "세계 예선" in r["route"] else 3 if "랭킹" in r["route"] else
                                        4 if "개최국" in r["route"] else 5 if "추가" in r["route"] else 6))
    i = 0
    cells = []
    for r in order:
        for k in range(r["n"]):
            cells.append((r, k))
    for idx, (r, k) in enumerate(cells):
        cx = 14 + (idx % per_row) * (size + gap / 2 + 4)
        cy = 38 + (idx // per_row) * (size * (0.62 if total > 16 else 1) + 10)
        hh = size * (0.62 if total > 16 else 1)
        col = rcolor(r["route"])
        dash = "최대" in r.get("nlabel", "")
        ql = [q["noc"] for q in r["q"] for _ in range(2 if "확보국" in r["route"] else 1)]
        q = ql[k] if k < len(ql) else ""
        o += R(cx, cy, size, hh, col if not dash else "#fff", col if dash else None, 4, dash)
        if q:
            o += T(cx + size / 2, cy + hh / 2 + 5, q, 12, 700, "#fff" if not dash else col, "middle")
    nrows = (len(cells) + per_row - 1) // per_row
    hh = size * (0.62 if total > 16 else 1)
    y = 38 + nrows * (hh + 10) + 14
    # legend
    seen = []
    for r in order:
        lab = r["route"]
        key = ("대륙 예선" if "대륙" in lab else lab.split(" (")[0])
        if key in [s[0] for s in seen]:
            for s in seen:
                if s[0] == key: s[1] += r["n"]
            continue
        seen.append([key, r["n"], rcolor(lab), "최대" in r.get("nlabel", "")])
    lx, ly = 14, y
    for key, n, col, dash in seen:
        lab = f"{key} {'≤' if dash else ''}{n}"
        wlab = 26 + len(lab) * 12.2
        if lx + wlab > 934: lx, ly = 14, ly + 22
        o += R(lx, ly - 11, 13, 13, col if not dash else "#fff", col if dash else None, 2, dash) + T(lx + 18, ly, lab, 12.5)
        lx += wlab + 10
    return svg(948, ly + 14, title, o)


def svg_scenario():
    tiles = [("대륙 예선 5", C["cont"], ["CHN", "GER", "BRA", "EGY", "AUS"]),
             ("개최국 1", C["host"], ["USA"]),
             ("2027 월드컵 6", C["world"], ["JPN", "KOR", "FRA", "CRO", "HKG", "SWE"]),
             ("세계랭킹 2", C["wr"], ["TPE", "ROU"]),
             ("추가 2", C["add"], ["PRK?", "?"])]
    o = T(14, 22, "가상 예시: 2025 혼성 단체 월드컵 성적을 LA28 규정에 대입하면", 15, 700)
    x = 14
    for lab, col, nocs in tiles:
        w = len(nocs) * 54 - 4
        o += T(x, 50, lab, 12.5, 700, col)
        for j, n in enumerate(nocs):
            tx = x + j * 54
            hl = n == "KOR"
            o += R(tx, 58, 50, 40, col, "#202122" if hl else None, 5)
            o += T(tx + 25, 83, n, 13, 700, "#fff", "middle")
        x += w + 16
    o += T(14, 124, "대륙 예선 승자는 '그 대륙 최강국'(아시아=중국, 유럽=독일 등)으로, 세계랭킹 2장은 월드컵 9–12위권으로 가정. 추가 2장은 개인 경로로", 12, 400, "#54595d")
    o += T(14, 142, "남녀 3명씩(또는 3+2, 2+2)을 채운 나라 몫이라 지금은 비워 둠 — 북한처럼 혼성 단체 대회엔 안 나와도 개인 쿼터를 많이 모으는 나라가 후보.", 12, 400, "#54595d")
    return svg(948, 156, "가상 예시 16팀: 대륙 CHN GER BRA EGY AUS, 개최국 USA, 월드컵 JPN KOR FRA CRO HKG SWE, 세계랭킹 TPE ROU, 추가 2", o)


# ------------------------------------------------------------------ 내용 조각
def src_list(extra=()):
    items = [(PDF, "ITTF · LA28 Qualification System (IOC 게시 PDF, Version as of 14 August 2026, 13쪽)")] + list(extra)
    return '<ol class="sources">' + "".join(f'<li><a href="{u}">{e(t)}</a></li>' for u, t in items) + '</ol>'


def live_link(key, name):
    return f'<p class="small"><a href="./{LIVE}#ev-{key}">{name} 쿼터 확보 현황 → 쿼터 트래킹</a></p>'


def ev(key):
    return next(x for x in DATA["events"] if x["key"] == key)


TIMELINE = [
    ("2027.06.01–10.31", "각 대륙 혼성 단체 대륙 예선"), ("2027.06.20–22", "유럽 혼성 단체 대륙 예선 · 이스탄불 (TUR)"),
    ("2027.06.01–2028.02.28", "각 대륙 혼합복식 · 남녀 복식 대륙 예선"), ("2027.10.01", "IOC, 보편성 쿼터 신청 안내"),
    ("2027.11.15–12.20 중", "2027 혼성 단체 월드컵 · 6팀"), ("2028.01", "혼성 단체 세계랭킹 · 2팀"),
    ("2028.01.04–02.28", "각 대륙 단식 대륙 예선"), ("2028.01.15", "보편성 쿼터 신청 마감"),
    ("2028.03.13", "남녀 복식 · 혼합복식 세계랭킹 배정 · 각 2조"), ("2028.03.15–05.07", "혼합복식 · 남녀 복식 세계 예선 대회 · 각 4조"),
    ("2028.05.15", "혼성 단체 15·16번째 추가 배정 + 그 2팀의 단식 자리 재정리"), ("2028.05.22", "남녀 복식 · 혼합복식 추가 4조 배정"),
    ("2028.06.05", "단식 세계랭킹 배정 (잔여 단식)"), ("2028.06.15", "ITTF 미사용 쿼터 최종 재배정"),
    ("2028.06.26", "LA28 스포츠 엔트리 마감"), ("2028.07.14–30", "LA28 올림픽"),
]


def timeline_table(filter_words=None):
    rows = [(d, t) for d, t in TIMELINE if not filter_words or any(w in t for w in filter_words)]
    return table(["날짜", "일정"], rows, caption="ITTF 규정 H (Qualification timeline) 기준")


# ------------------------------------------------------------------ 전체 안내
def build_main():
    body = ""
    body += ('<section id="change" class="tt-change"><h2>LA28에서 달라진 점: 5종목 → 6종목</h2>'
             '<p>파리 2024까지는 <strong>남자 단식 · 여자 단식 · 남자 단체 · 여자 단체 · 혼합복식</strong> 5종목이었다. '
             'LA28은 남녀 단체를 없애고 <strong>혼성 단체</strong>를 새로 만들었으며, 아테네 2004 이후 사라졌던 <strong>남자 복식 · 여자 복식</strong>이 돌아왔다. '
             '그래서 <strong>혼성 단체 · 혼합복식 · 남자 복식 · 여자 복식 · 남자 단식 · 여자 단식</strong> 6종목이 된다. 전체 인원은 그대로 172명(남녀 86명씩)이다.</p>'
             + fig(svg_history(), "종목 수는 늘었지만 선수 수는 그대로다. 같은 인원이 더 많은 종목을 겸해야 하므로 '한 나라가 몇 명을 확보하느냐'가 더 중요해졌다.")
             + '</section>')
    body += ('<section id="focus"><h2>핵심: 남녀 3명씩, 최대 6명</h2>'
             '<div class="tt-key"><strong class="big">국가당 상한 = 남자 3명 + 여자 3명 = 6명</strong>'
             '종목이 6개여도 한 나라가 보낼 수 있는 선수는 성별 3명뿐이다(B.2). 그래서 탁구 예선은 결국 '
             '<strong>“어떤 조합으로든 남녀 3명씩을 채우느냐”</strong>의 싸움이다. 가장 빠른 길은 <a href="./oltabletennis-team.html">혼성 단체</a> 쿼터 1장으로, '
             '이것 하나로 남녀 3명씩 6명이 확정되고 남녀 단식 2자리씩이 따라온다(B.4, D.1.21).</div>'
             + fig(svg_six(), "예시 라인업. 단식·복식·혼합복식 쿼터를 따로 따더라도 출전 선수는 이 6명 안에서 겹쳐 쓰므로 인원은 늘지 않는다. 복식 3종(남복·여복·혼복)은 단체 쿼터에 포함되지 않아 별도 경로로 확보해야 한다.")
             + '<p>혼성 단체를 놓친 나라도 길은 있다. 단식·복식·혼합복식을 개별로 모아 <strong>남녀 3명씩(또는 3+2, 2+2)</strong>을 채우면 '
               '마지막 혼성 단체 2장(D.1.5)의 후보가 된다. 이때도 목표는 같다 — 6명.</p></section>')
    body += ('<section id="math"><h2>172석의 구조</h2>'
             + fig(svg_split(), f'파리 2024 배정은 <a href="{WIKI24}">Wikipedia 2024 탁구 예선 문서</a>의 국가별 표 기준(60개 NOC). LA28은 규정상 산술이다.')
             + '<p>LA28에서 혼성 단체 16개국이 가져가는 인원만 <strong>96명(56%)</strong>이다. 남은 <strong>76명</strong>을 나머지 나라들이 대륙 단식(성별 21명), '
               '랭킹 단식(최대 10명), 보편성(1명), 비단체국 복식으로 나눠 갖는다. 파리에서 6명을 다 채운 나라가 11개국이었으니, '
               'LA28은 “6명 보유국”이 오히려 늘고 그 외 나라들은 1–2명씩 흩어지는 구조가 될 가능성이 높다.</p></section>')
    body += ('<section id="powers"><h2>예시: 탁구 강국은 이렇게 채운다</h2>'
             '<p>중국 · 일본 · 한국 · 독일 · 스웨덴 · 북한 · 대만 · 브라질 같은 강국은 대부분 혼성 단체 쿼터로 6명을 먼저 확보하고, '
             '그다음 복식 3종 쿼터를 쌓아 6종목 엔트리를 채우는 방식이 될 것이다. 나머지 소소한 단식·복식 쿼터는 그 밖의 나라들에 나뉜다.</p>'
             + table(["국가", "혼성 단체 월드컵", "파리 2024 인원", "LA28 예상 경로 (참고)"], [
                 ("중국 CHN", "2023·2024·2025 우승", "6", "아시아 대륙 예선 1장 유력 → 6명"),
                 ("일본 JPN", "2023 동 · 2025 은", "6", "2027 월드컵 상위 6 (대륙 1장은 중국과 경쟁)"),
                 (("대한민국 KOR", "2023 은 · 2024 은 · 2025 4위", "6", "2027 월드컵 상위 6이 현실적 경로"), "class:kor-row"),
                 ("독일 GER", "2025 동", "6", "유럽 대륙 예선(2027.06 이스탄불) 또는 월드컵"),
                 ("스웨덴 SWE", "2025 8위", "6", "유럽 대륙 예선 · 월드컵 · 세계랭킹"),
                 ("대만 TPE", "2025 조별 3위", "6", "월드컵 · 세계랭킹 2장"),
                 ("브라질 BRA", "2025 조별 4위", "6", "아메리카 대륙 예선 (미국은 개최국 쿼터 보유)"),
                 ("북한 PRK", "출전 기록 없음", "3", "개인 경로(대륙 단식·복식)로 3+3 또는 3+2를 모으면 추가 2장(D.1.5) 후보"),
                 ("프랑스 FRA", "2025 5위", "6 (개최국)", "월드컵 · 유럽 대륙 예선"),
                 ("홍콩 HKG", "2024 동 · 2025 7위", "4", "월드컵 · 세계랭킹 경계선"),
             ], cls="data tt-sc", caption="강국별 참고 — 월드컵 성적은 Wikipedia, 파리 인원은 2024 예선 문서 기준")
             + fig(svg_scenario(), f'2025 혼성 단체 월드컵(청두) 최종 순위: 중국 1 · 일본 2 · 독일 3 · 한국 4 · 프랑스 5 · 크로아티아 6 · 홍콩 7 · 스웨덴 8 (<a href="{WC25}">Wikipedia</a>). '
                   '실제 LA28 배정은 2027 대륙 예선과 2027 월드컵 결과로 정해지며, 이 그림은 규정 구조를 보여 주기 위한 가상 예시다.')
             + '<p class="note">북한은 파리 2024에서 혼합복식 은메달(리정식·김금용)을 땄지만 국제 대회 출전이 적어 랭킹 경로가 불리하다. '
               '혼성 단체 대회 출전 없이 개인 쿼터로 6명을 채울 수 있는지가 관전 포인트다.</p></section>')
    # pathway summary
    rows = [
        (f'<a href="./oltabletennis-team.html">혼성 단체</a>', "16팀", "대륙 5 · 월드컵 6 · 세계랭킹 2 · 개최국 1 · 추가 2", "1팀 (남녀 3명씩)"),
        (f'<a href="./oltabletennis-xd.html">혼합복식</a>', "16조", "대륙 5 · 세계 예선 4 · 세계랭킹 2 · 개최국 1 · 추가 4", "1조 (세계 8위 안 2조면 2조)"),
        (f'<a href="./oltabletennis-md.html">남자 복식</a>', "16조", "대륙 5 · 세계 예선 4 · 세계랭킹 2 · 개최국 1 · 추가 4", "1조"),
        (f'<a href="./oltabletennis-wd.html">여자 복식</a>', "16조", "대륙 5 · 세계 예선 4 · 세계랭킹 2 · 개최국 1 · 추가 4", "1조"),
        (f'<a href="./oltabletennis-ms.html">남자 단식</a>', "64명", "단체국 32 · 대륙 21 · 랭킹 최대 10 · 보편성 1", "2명"),
        (f'<a href="./oltabletennis-ws.html">여자 단식</a>', "64명", "단체국 32 · 대륙 21 · 랭킹 최대 10 · 보편성 1", "2명"),
    ]
    body += ('<section id="pathway"><h2>예선 경로 한눈에</h2>'
             + fig(svg_flow(), "규정 D절은 종목을 위계 순서로 나열한다. 혼성 단체가 가장 먼저이고 단식이 마지막이다.")
             + table(["세부종목", "쿼터", "경로", "국가 상한"], rows, caption="세부종목별 경로 요약 · 자세한 내용은 각 세부 탭")
             + '<h3 id="continental">대륙별 쿼터 (D.1.25)</h3>'
             + table(["대륙", "혼성 단체", "남자 복식", "여자 복식", "혼합복식", "단식 (성별)"], [
                 ("아프리카", "1", "1", "1", "1", "4"), ("아메리카", "1", "1", "1", "1", "4"), ("아시아", "1", "1", "1", "1", "6"),
                 ("유럽", "1", "1", "1", "1", "6"), ("오세아니아", "1", "1", "1", "1", "1")], caption="대륙 예선 배정 수 · 각 대륙연맹이 기존 대회 중 예선 대회를 지정")
             + '<p class="note">아시아는 혼성 단체·복식 대륙 쿼터가 1장씩뿐이라 중국·일본·한국·대만·북한·홍콩이 한 자리를 다툰다. 아시아 강국 대부분은 월드컵·세계 예선·세계랭킹·추가 배정 같은 세계 경로로 들어간다.</p></section>')
    body += ('<section id="quota"><h2>쿼터 표</h2>'
             + table(["성별", "일반쿼터", "개최국쿼터", "보편성쿼터", "합계"], [("남자", "82", "3", "1", "86"), ("여자", "82", "3", "1", "86"), ("합계", "164", "6", "2", "172")], cls="data quota", caption="선수 쿼터 · 단위: 명 (B.1)")
             + '<p>단식 쿼터는 <strong>선수 이름</strong>으로, 복식·혼합복식·혼성 단체 쿼터는 <strong>NOC</strong>에 배정된다(B.4).</p></section>')
    body += ('<section id="other"><h2>개최국·보편성 쿼터</h2>'
             '<p>개최국 미국은 다른 경로로 확보하지 못한 경우 혼성 단체 1팀, 남녀 단식 2명씩, 남녀 복식·혼합복식 1조씩을 보장받는다(D.2). 쓰지 않은 개최국 쿼터는 세계랭킹 차순위에게 재배정된다(F.2).</p>'
             '<p><strong>보편성 쿼터는 남녀 단식 1명씩</strong>이다. IOC가 2027.10.01 신청을 안내하고 2028.01.15에 마감하며, 2027.05.31–2028.06.01 사이 ITTF 랭킹에 오른 적이 있어야 한다(C, D.3). 쓰지 않은 보편성 쿼터는 2028.06.05 세계랭킹 차순위에게 간다(F.3).</p></section>')
    body += ('<section id="eligibility"><h2>참가 자격</h2><p>올림픽 헌장(제41조 국적, 제43조 세계반도핑규약 및 경기 조작 방지 규정), 여성 카테고리 보호에 관한 IOC 정책, IOC 참가 조건, ITTF 규정과 ITTF 올림픽 출전 자격을 충족해야 한다. '
             '혼성 단체 출전국은 성별 1명씩 비출전 대체선수(Ap)를 둘 수 있다(G).</p></section>')
    body += '<section id="timeline"><h2>예선 및 대회 일정</h2><p>2026년에는 탁구 예선 대회가 없다. 첫 예선은 2027년 6월 대륙별 혼성 단체 예선이다.</p>' + timeline_table() + '</section>'
    body += ('<section id="sources"><h2>공식 근거</h2>' + src_list([(WIKI24, "Wikipedia · Table tennis at the 2024 Summer Olympics – Qualification (파리 배정 비교)"),
                                                                 (WC25, "Wikipedia · 2025 ITTF Mixed Team World Cup"), (WCALL, "Wikipedia · ITTF Mixed Team World Cup"),
                                                                 (AG26, "Olympics.com · 아시안게임 탁구 한국 대표팀 결과")])
             + f'<p class="note">규정 확인일: {CHECK}. IOC가 게시한 ITTF 원문 PDF(Version as of 14 August 2026)를 직접 읽고 정리했다. 본 문서는 비공식 한국어 요약이며 최종 적용은 ITTF 공지를 따른다.</p></section>')
    body += ('<section id="korea"><h2>한국 출전 전망</h2><div class="notice"><strong>2026-10-05 기준 참고</strong><br>현재 성적을 LA28 규정에 단순 적용한 참고치이며 2028 확정 전망이 아님.</div>'
             '<div class="korea"><h3>목표는 6명 · 길은 2027 혼성 단체 월드컵</h3>'
             '<p>한국은 파리 2024에서 남녀 3명씩 6명을 모두 채웠고 혼합복식(임종훈·신유빈)과 여자 단체에서 동메달을 땄다. 혼성 단체 월드컵에서는 2023·2024 준우승, 2025 4위로 꾸준히 상위권이다. '
             '아시아 대륙 혼성 단체 쿼터는 1장뿐이라 중국과 겹치므로, <strong>2027 혼성 단체 월드컵 상위 6(미확보국 기준)</strong>이 6명 확보의 현실적 경로다.</p>'
             + table(["선수·팀", "공개 성적", "근거"], [
                 ("임종훈·신유빈", "아시안게임 2026 혼합복식 동", f'<a href="{AG26}">Olympics.com</a>'),
                 ("남녀 단체", "아시안게임 2026 동 2개 (준결승 일본에 각 0–3)", f'<a href="{AG26}">Olympics.com</a>'),
                 ("신유빈 · 장우진", "아시안게임 2026 여자 단식 8강 · 남자 단식 16강", f'<a href="{AG26}">Olympics.com</a>'),
                 ("혼성 단체", "월드컵 2023 은 · 2024 은 · 2025 4위", f'<a href="{WCALL}">Wikipedia</a>'),
             ], cls="data ranking", caption="근거로 확인한 성적 · 확정 대표 명단이 아님")
             + '<p><strong>단체 확보 후:</strong> 남녀 단식 2명씩이 자동으로 정해지고, 복식 3종은 따로 따야 한다. 아시아 대륙 1장은 중국·일본과 경쟁이므로 세계랭킹(2028.03.13, 2조) · 세계 예선(4조) · 추가 배정(4조, 단식 2명 보유국 우선)이 주 경로다. 혼합복식은 세계 8위 안에 한국 조가 2개면 두 번째 조도 받을 수 있다.</p>'
             '<p class="small">아시안게임은 탁구 예선 경로가 아니다.</p></div></section>')
    items = [("change", "달라진 점: 5종목 → 6종목"), ("focus", "핵심: 남녀 3명씩, 최대 6명"), ("math", "172석의 구조"), ("powers", "예시: 탁구 강국"),
             ("pathway", "예선 경로 한눈에"), ("quota", "쿼터 표"), ("other", "개최국·보편성 쿼터"), ("eligibility", "참가 자격"),
             ("timeline", "예선 및 대회 일정"), ("sources", "공식 근거"), ("korea", "한국 출전 전망")]
    box = [("주관", "국제탁구연맹 (ITTF)"), ("세부종목", "6 (혼성 단체 · 혼합복식 · 남녀 복식 · 남녀 단식)"), ("파리 2024 대비", "남녀 단체 → 혼성 단체, 남녀 복식 부활"),
           ("선수 쿼터", "172명 (남 86 · 여 86)"), ("NOC 상한", "성별 3명 (최대 6명)"), ("종목별 상한", "단식 2명 · 복식 1조 · 단체 1팀"),
           ("배정 방식", "단식 선수 이름 · 나머지 NOC"), ("규정 버전", "2026.08.14")]
    return page(MAIN, "탁구 (Table Tennis)", "탁구 (Table Tennis)",
                "탁구는 네트를 사이에 둔 탁자 위에서 라켓으로 공을 주고받는 종목이다. LA28에서는 남녀 단체가 혼성 단체로 바뀌고 남녀 복식이 돌아와 6개 세부종목에 메달이 걸린다. 그래도 국가당 선수는 남녀 3명씩, 최대 6명이다.",
                "LA28 탁구 예선: 5종목에서 6종목으로 바뀐 체계, 국가당 남녀 3명씩 최대 6명 확보 구조, 세부종목별 경로와 쿼터 트래킹",
                items, body, "탁구 · LA28 예선", box, f"규정 확인 {CHECK} · 한국 전망 기준 {CHECK}")


# ------------------------------------------------------------------ 세부종목
def path_table(rows, caption):
    return table(["경로 (규정)", "쿼터", "선발 방식"], rows, caption=caption)


def build_event(key):
    _, fname, name, _ = next(x for x in EVENTS if x[0] == key)
    E = ev(key)
    body = ""
    items = [("overview", "개요"), ("slots", "자리 그림"), ("pathway", "선발 경로"), ("realloc", "재배정"), ("timeline", "일정"), ("korea", "한국 관점"), ("sources", "공식 근거")]
    if key == "xt":
        intro = "혼성 단체는 LA28 신설 종목이다. 16팀이 남녀 3명씩 출전하며, 이 쿼터 1장이 곧 '6명 확보'다."
        ov = ('<p><strong>16팀 · 96명.</strong> 국가당 1팀(남녀 3명씩)이고 쿼터는 NOC에 배정된다. 혼성 단체 쿼터를 얻으면 <strong>남녀 단식 2자리씩이 자동</strong>으로 따라온다(B.4, D.1.21). '
              '파리 2024의 남녀 단체(각 16팀)가 하나로 합쳐진 셈이라, 남녀 중 한쪽만 강한 나라는 단체 쿼터를 따기 어려워졌다.</p>'
              '<div class="tt-key"><strong class="big">혼성 단체 1장 = 남 3 + 여 3 = 국가 상한 전부</strong>탁구 강국에게 이 쿼터는 사실상 “올림픽 6명 패키지”다. 나머지 종목 쿼터는 이 6명이 누구와 어떤 조로 나설지를 정할 뿐 인원을 늘리지 않는다.</div>')
        rows = [("대륙 예선 <span class='rule-no'>D.1.1</span>", "5팀", "대륙마다 지정 대회 최상위 1개국. 대회는 각 대륙연맹이 기존 대회 중 지정(2027.06.01–10.31). 유럽은 2027.06.20–22 이스탄불."),
                ("2027 혼성 단체 월드컵 <span class='rule-no'>D.1.2</span>", "6팀", "미확보 팀 중 최상위 6팀 (2027.11.15–12.20 중)."),
                ("혼성 단체 세계랭킹 <span class='rule-no'>D.1.3</span>", "2팀", "2028년 1월 혼성 단체 세계랭킹 미확보 상위 2팀."),
                ("개최국 <span class='rule-no'>D.1.4</span>", "1팀", "미국 (다른 경로로 확보하지 못한 경우)."),
                ("추가 배정 <span class='rule-no'>D.1.5 · D.4</span>", "2팀", "단식·복식·혼합복식으로 선수를 가장 많이 모은 NOC. 우선순위 ① 남녀 3명씩 이상 ② 3+2 또는 2+3 ③ 2+2. 동률이면 단식 선수 수 → 2028.05.15 주 세계랭킹 최고 단식 선수 순.")]
        extra = ('<h3 id="format">참고: 혼성 단체 월드컵 경기 방식</h3><p>ITTF 혼성 단체 월드컵(2023년 신설, 2027년까지 청두 개최)은 혼합복식 → 여자 단식 → 남자 단식 → 여자/남자 복식 순으로 진행하며, 3게임제 경기를 이어 8게임을 먼저 따는 팀이 이긴다(최대 15게임). '
                 f'혼합복식에 나선 선수는 이어지는 단식에 나설 수 없다(<a href="{WCALL}">Wikipedia</a>). LA28 올림픽 혼성 단체 경기 방식은 예선 규정 문서에 없다.</p>'
                 + fig(svg_scenario(), "2025 월드컵 순위를 대입한 가상 예시. 실제 배정은 2027 대륙 예선·월드컵·2028.01 랭킹으로 정해진다."))
        realloc = "대륙 쿼터를 확정하지 않거나 반납하면 같은 대륙 예선의 차순위 팀, 월드컵 쿼터는 월드컵 차순위 팀, 추가 2장은 D.4 순위의 다음 팀에게 간다. 개최국 미사용분은 2028년 5월 세계 단체 랭킹 차순위에게 간다(F.1, F.2)."
        korea = ('<p>한국은 월드컵 2023·2024 준우승, 2025 4위. 아시아 대륙 1장은 중국과 겹치므로 <strong>2027 월드컵 미확보국 상위 6</strong>이 주 경로이고, 놓치면 2028.01 세계랭킹 2장이 다음 기회다. '
                 '그것도 놓치면 개인 경로로 3+3을 채워 추가 2장(D.1.5)을 노려야 한다.</p>')
        tl = ["혼성 단체", "단체 세계랭킹", "추가 배정", "엔트리", "올림픽"]
    elif key == "xd":
        intro = "혼합복식은 도쿄 2020에서 처음 열렸고 LA28에도 유지된다. 16조가 출전한다."
        ov = ('<p><strong>16조 · 32명.</strong> 원칙은 국가당 1조이지만, 배정 시점에 <strong>세계 8위 안에 2조</strong>가 있는 NOC는 두 번째 조를 받을 수 있다. '
              '단, 그 4명(2조)이 모두 그 나라의 6명(성별 3명) 안에 있어야 한다(B.3, D.1.10). 쿼터는 NOC에 배정된다.</p>')
        rows = [("대륙 예선 <span class='rule-no'>D.1.6</span>", "5조", "대륙마다 지정 대회 최상위 1조 (NOC당 1조). 기간 2027.06.01–2028.02.28."),
                ("세계랭킹 <span class='rule-no'>D.1.8</span>", "2조", "2028.03.13 혼합복식 세계랭킹에서 미확보·이미 확보한 NOC와 다른 나라의 상위 2조."),
                ("세계 예선 대회 <span class='rule-no'>D.1.7</span>", "4조", "2028.03.15–05.07 사이 지정 대회 상위 4조. 미확보 NOC만 같은 나라 선수 조합으로 NOC당 1조 출전."),
                ("개최국 <span class='rule-no'>D.1.9</span>", "1조", "미국 (다른 경로로 확보하지 못한 경우)."),
                ("추가 배정 <span class='rule-no'>D.1.10 · D.4</span>", "4조", "먼저 세계 8위 안 2조 보유국의 두 번째 조(조건 충족 시). 이어서 남녀 단식 선수가 1명 이상씩 있는 NOC의 조. 부족하면 혼합복식 미확보 팀 중에서. 동률은 혼합복식 세계랭킹.")]
        extra = ""
        realloc = "대륙 쿼터 미사용분은 같은 대륙 예선에서 아직 출전권이 없는 차순위 조에게, 세계랭킹 쿼터 미사용분은 2028.03.13 랭킹 차순위 조에게 간다. 개최국 미사용분은 2028.05.22 복식 랭킹 차순위에게 간다(F.1, F.2)."
        korea = ('<p>임종훈·신유빈은 파리 2024 동메달, 2026 아시안게임 동메달. 아시아 대륙 1장은 중국·일본과 경쟁이다. 한국이 혼성 단체를 따면 남녀 단식 선수가 생기므로 추가 4조(D.1.10)의 우선 대상이 되고, '
                 '세계랭킹 8위 안에 한국 조가 둘이면 두 번째 조도 노릴 수 있다.</p>')
        tl = ["혼합복식", "복식", "엔트리", "올림픽"]
    elif key in ("md", "wd"):
        g = "남자" if key == "md" else "여자"
        intro = f"{g} 복식은 아테네 2004 이후 24년 만에 올림픽에 돌아온다. 16조가 출전한다."
        ov = (f'<p><strong>16조 · 32명.</strong> 국가당 1조(같은 나라 선수 2명)이고 쿼터는 NOC에 배정된다. 베이징 2008부터 {g} 복식은 {g} 단체에 흡수됐다가 LA28에서 단체가 혼성으로 바뀌며 독립 종목으로 부활했다.</p>'
              f'<p>추가 4조는 <strong>{g} 단식 2명을 확보한 NOC</strong>가 우선이라, 혼성 단체국(단식 2명 자동)에 유리한 구조다.</p>')
        n1, n2, n3, n4, n5 = ("D.1.11", "D.1.13", "D.1.12", "D.1.14", "D.1.15") if key == "md" else ("D.1.16", "D.1.18", "D.1.17", "D.1.19", "D.1.20")
        rows = [(f"대륙 예선 <span class='rule-no'>{n1}</span>", "5조", "대륙마다 지정 대회 최상위 1조. 기간 2027.06.01–2028.02.28."),
                (f"세계랭킹 <span class='rule-no'>{n2}</span>", "2조", f"2028.03.13 {g} 복식 세계랭킹에서 미확보·다른 NOC의 상위 2조."),
                (f"세계 예선 대회 <span class='rule-no'>{n3}</span>", "4조", "2028.03.15–05.07 사이 지정 대회 상위 4조. 미확보 NOC만 같은 나라 선수 조합으로 NOC당 1조 출전."),
                (f"개최국 <span class='rule-no'>{n4}</span>", "1조", "미국 (다른 경로로 확보하지 못한 경우)."),
                (f"추가 배정 <span class='rule-no'>{n5} · D.4</span>", "4조", f"{g} 단식 2명이 확보된 NOC의 조. 부족하면 {g} 복식 미확보 팀 중에서. 동률은 {g} 복식 세계랭킹.")]
        extra = ""
        realloc = "대륙 쿼터 미사용분은 같은 대륙 예선에서 아직 출전권이 없는 차순위 조에게, 세계랭킹 쿼터 미사용분은 2028.03.13 랭킹 차순위 조에게 간다. 개최국 미사용분은 2028.05.22 복식 랭킹 차순위에게 간다(F.1, F.2)."
        korea = (f'<p>아시아 대륙 1장은 중국·일본과 경쟁이다. 한국은 혼성 단체를 확보하면 {g} 단식 2명이 생겨 추가 4조의 우선 대상이 된다. 따라서 '
                 f'<strong>단체 확보 → 세계랭킹(2028.03.13) 또는 추가 배정</strong>이 가장 안정적인 순서다. 복식 선수는 단체 3명 안에서 나와야 한다.</p>')
        tl = ["복식", "엔트리", "올림픽"]
    else:
        g = "남자" if key == "ms" else "여자"
        intro = f"{g} 단식은 64명이 출전한다. 절반(32명)은 혼성 단체 출전국 몫이고, 나머지 32명이 대륙 예선·랭킹·보편성으로 정해진다."
        ov = (f'<p><strong>64명.</strong> 국가당 최대 2명이고 쿼터는 <strong>선수 이름</strong>으로 배정된다(B.3, B.4). 혼성 단체 16개국은 {g} 단식 2명씩, 32자리를 자동으로 받는다.</p>'
              '<p>단식은 항상 64명으로 맞춘다. 비단체국 복식에만 나온 선수가 있으면 그 선수가 랭킹 단식 자리(최대 10)를 먼저 채울 수 있고(D.1.23), 그만큼 순수 랭킹 자리가 줄어든다(Note 2).</p>')
        rows = [("혼성 단체 확보국 <span class='rule-no'>D.1.21</span>", "32명", "혼성 단체 16개국 × 2명."),
                ("대륙 예선·대륙 랭킹 <span class='rule-no'>D.1.22</span>", "21명", "아프리카 4 · 아메리카 4 · 아시아 6 · 유럽 6 · 오세아니아 1. 대륙별 예선 대회(2028.01.04–02.28) 또는 단식 세계랭킹."),
                ("세계랭킹·복식 전용 선수 <span class='rule-no'>D.1.23</span>", "최대 10명", "2028.06.05 단식 세계랭킹, 또는 복식만 확보한 선수. 국가 상한 적용."),
                ("보편성 <span class='rule-no'>D.1.24</span>", "1명", "IOC 초청 2027.10.01, 신청 마감 2028.01.15. 2027.05.31–2028.06.01 ITTF 랭킹 등재 필요.")]
        extra = ('<h3 id="cont-singles">대륙별 단식 자리</h3>' + table(["대륙", "자리"], [("아프리카", "4"), ("아메리카", "4"), ("아시아", "6"), ("유럽", "6"), ("오세아니아", "1"), ("합계", "21")], caption="D.1.25 · 성별"))
        realloc = "단체 미확보 NOC 선수의 대륙 쿼터를 쓰지 않으면 같은 대륙 단식 예선의 차순위 선수에게, 그 밖의 쿼터는 2028.06.05 세계 단식 랭킹 차순위 선수(NOC 무관)에게 간다. 보편성 미사용분도 2028.06.05 랭킹 차순위에게 간다(F.1, F.3)."
        korea = (f'<p>한국 {g} 단식 2명은 혼성 단체 쿼터로 들어오는 것이 기본 경로다. 단체를 놓치면 아시아 6자리를 놓고 대륙 예선을 치르거나 2028.06.05 세계랭킹에 기대야 한다. '
                 '아시아 6자리에는 중국·일본 등 단체국이 아닌 나라 선수들만 경쟁하므로, 단체국이 된 나라는 이 경쟁에 끼지 않는다.</p>')
        tl = ["단식", "보편성", "단체", "엔트리", "올림픽"]
    body += f'<section id="overview"><h2>개요</h2>{ov}</section>'
    body += ('<section id="slots"><h2>자리 그림</h2>' + fig(svg_slots(E, f"{name} {E['total']}{E['unit']} · 경로별 자리"),
             "칸 하나가 " + ("1팀" if key == "xt" else "1조" if E["unit"] == "조" else "1명") + ". 국가 코드가 적힌 칸은 쿼터 트래킹에 기록된 자리(조건부 포함). 점선 칸은 '최대' 자리.") + '</section>')
    body += ('<section id="pathway"><h2>선발 경로</h2>' + path_table(rows, f"{name} · ITTF 규정 D절") + extra + live_link(key, name) + '</section>')
    body += f'<section id="realloc"><h2>재배정</h2><p>{realloc}</p></section>'
    body += '<section id="timeline"><h2>일정</h2>' + timeline_table(tl) + '</section>'
    body += ('<section id="korea"><h2>한국 관점</h2><div class="korea"><h3>6명 안에서 생각하기</h3>' + korea
             + '<p class="small">국가당 상한은 성별 3명이다. 어떤 경로로 쿼터를 따든 출전 선수는 이 한도 안에서 겹쳐 쓴다.</p></div></section>')
    body += '<section id="sources"><h2>공식 근거</h2>' + src_list([(WCALL, "Wikipedia · ITTF Mixed Team World Cup")] if key == "xt" else []) + '</section>'
    if key != "xt":
        items = [x for x in items]
    box = [("세부종목", name), ("쿼터", f"{E['total']}{E['unit']}" + (f" ({E['per']})" if E['per'] else "")),
           ("국가 상한", {"xt": "1팀", "xd": "1조 (조건부 2조)", "md": "1조", "wd": "1조", "ms": "2명", "ws": "2명"}[key]),
           ("배정 대상", "선수 이름" if key in ("ms", "ws") else "NOC"),
           ("파리 2024", {"xt": "없음 (남녀 단체 따로)", "xd": "16조", "md": "없음 (2004 이후 폐지)", "wd": "없음 (2004 이후 폐지)", "ms": "단식 (단체와 별도)", "ws": "단식 (단체와 별도)"}[key]),
           ("규정", "ITTF 2026.08.14판")]
    return page(fname, f"탁구 {name}", f"탁구 {name}", intro, f"LA28 탁구 {name} 예선 경로, 쿼터 {E['total']}{E['unit']}, 재배정과 일정",
                items, body, f"탁구 {name}", box, f"규정 확인 {CHECK}")


# ------------------------------------------------------------------ 쿼터 트래킹
KO_EV = {"xt": "혼성 단체", "xd": "혼합복식", "md": "남자 복식", "wd": "여자 복식", "ms": "남자 단식", "ws": "여자 단식"}


def st(s):
    return f'<span class="st st-{e(s)}">{e(s)}</span>' if s else ''


def summary():
    nocs = {}
    for E in DATA["events"]:
        for r in E["rows"]:
            for q in r["q"]:
                d = nocs.setdefault(q["noc"], {"ko": q.get("ko", q["noc"]), "ev": {}, "cond": False})
                cnt = 2 if E["key"] in ("ms", "ws") and "확보국" in r["route"] else 1
                d["ev"][E["key"]] = d["ev"].get(E["key"], 0) + cnt
                if q.get("st") == "조건부": d["cond"] = True
    rows, tot = [], {k: 0 for k in KO_EV}
    tm = tw = 0
    for noc in sorted(nocs, key=lambda n: (nocs[n]["cond"], -sum(nocs[n]["ev"].values()), n)):
        d = nocs[noc]
        v = d["ev"]
        if noc in DATA.get("athletes", {}):
            m, w = DATA["athletes"][noc]
            est = ""
        elif v.get("xt"):
            m = w = 3
            est = ""
        else:
            m = min(3, v.get("ms", 0) + 2 * v.get("md", 0) + v.get("xd", 0))
            w = min(3, v.get("ws", 0) + 2 * v.get("wd", 0) + v.get("xd", 0))
            est = "*"
        name = f'{e(d["ko"])} <span class="tbd">({noc})</span>' + (st("조건부") + '<a class="fn" href="#note-c">[c]</a>' if d["cond"] else "")
        rows.append([name] + [str(v.get(k, "")) for k in KO_EV] + [f"{m}{est}", f"{w}{est}", f"{m + w}{est}"])
        if not d["cond"]:
            for k in KO_EV: tot[k] += v.get(k, 0)
            tm += m; tw += w
    n_real = sum(1 for n in nocs if not nocs[n]["cond"])
    foot = (f'<tr><th scope="row">합계 {n_real}개국<br><span class="small">조건부 제외</span></th>' + "".join(f'<td>{tot[k]}</td>' for k in KO_EV)
            + f'<td>{tm}</td><td>{tw}</td><td>{tm + tw}</td></tr>'
            + '<tr><th scope="row">배정 총량</th><td>16</td><td>16</td><td>16</td><td>16</td><td>64</td><td>64</td><td>86</td><td>86</td><td>172</td></tr>')
    t = ('<div class="tt-wrap"><table class="data qs"><caption>국가별 쿼터 요약 · ' + DATA["asof"] + ' 기준 · 단위: 단체=팀, 복식=조, 단식=명</caption>'
         '<thead><tr><th scope="col">국가</th>' + "".join(f'<th scope="col">{v}</th>' for v in ["혼성<br>단체", "혼합<br>복식", "남자<br>복식", "여자<br>복식", "남자<br>단식", "여자<br>단식", "남", "여", "선수"])
         + '</tr></thead><tbody>')
    for r in rows:
        t += f'<tr><th scope="row">{r[0]}</th>' + "".join(f'<td>{c}</td>' for c in r[1:]) + '</tr>'
    t += f'</tbody><tfoot>{foot}</tfoot></table></div>'
    return t


def event_table(E):
    unit = E["unit"]
    t = (f'<h3 id="ev-{E["key"]}">{KO_EV[E["key"]]} · {E["total"]}{unit}</h3><p class="small"><a href="./{FILE[E["key"]]}">규정 설명 → {KO_EV[E["key"]]} 탭</a></p>'
         f'<div class="tt-wrap"><table class="data"><thead><tr><th scope="col">예선 대회·경로</th><th scope="col">날짜</th><th scope="col">장소</th><th scope="col">쿼터</th><th scope="col">확보</th></tr></thead><tbody>')
    filled = 0
    for r in E["rows"]:
        qs = r["q"]
        if qs:
            cell = "<br>".join(f'{e(q.get("ko", q["noc"]))} <span class="tbd">({q["noc"]})</span>'
                               + (f' — {e(q["players"])}' if q.get("players") else "") + st(q.get("st", ""))
                               + ('<a class="fn" href="#note-c">[c]</a>' if q.get("st") == "조건부" else "") for q in qs)
        else:
            cell = '<span class="tbd">—</span>'
        filled += sum(1 for q in qs if q.get("st") != "조건부")
        t += (f'<tr><th scope="row">{e(r["route"])}</th><td>{e(r["date"])}</td><td>{e(r["venue"])}</td><td>{e(r.get("nlabel", str(r["n"])))}</td><td>{cell}</td></tr>')
    t += f'</tbody><tfoot><tr><th scope="row">합계</th><td></td><td></td><td>{E["total"]}</td><td>{filled} 확보 · {E["total"] - filled if E["key"] in ("xt","xd","md","wd") else "—"} 남음</td></tr></tfoot></table></div>'
    return t


def build_live():
    log = "".join(f'<tr><td>{e(x["d"])}</td><td>{e(x["ev"])}</td><td>{e(x["txt"])}</td><td>'
                  + " · ".join(f'<a href="{u}">{e(n)}</a>' for n, u in x.get("src", [])) + '</td></tr>' for x in DATA["log"])
    body = ('<section id="log"><h2>업데이트 로그</h2><p>쿼터가 움직일 때마다 최신 순으로 기록한다. <span class="st st-잠정">잠정</span>은 ITTF 공식 통보 전, '
            '<span class="st st-확정">확정</span>은 ITTF가 NOC에 서면 통보(대회 후 2일 이내)하고 NOC가 사용을 확인(1주 이내)한 자리다.</p>'
            '<div class="tt-wrap"><table class="data live-log"><caption>쿼터 변동 기록</caption><thead><tr><th scope="col">날짜</th><th scope="col">대회</th><th scope="col">내용</th><th scope="col">출처</th></tr></thead><tbody>'
            + log + '</tbody></table></div></section>')
    body += ('<section id="summary"><h2>국가별 쿼터 요약</h2>' + summary()
             + '<p class="small">선수 수: 혼성 단체국은 남녀 3명씩. 그 밖의 나라는 단식 + 복식 2 + 혼합복식 1로 계산해 성별 3명에서 자르며(*표시 = 추정, 복식 선수가 단식과 겹칠 수 있음), 확정 명단이 나오면 live.json의 athletes로 덮어쓴다.</p></section>')
    body += '<section id="events"><h2>세부종목별 확보 현황</h2>' + "".join(event_table(E) for E in DATA["events"]) + '</section>'
    body += '<section id="timeline"><h2>예선 일정</h2>' + timeline_table() + '</section>'
    body += ('<section id="notes"><h2>주석</h2><ol class="footnotes"><li id="note-c"><span class="n">[c]</span>개최국 미국은 다른 경로로 확보하지 못한 경우에만 개최국 쿼터를 쓴다. 쓰지 않으면 세계랭킹 차순위에게 재배정되므로 합계에서 뺐다.</li>'
             '<li><span class="n">[d]</span>혼성 단체 15·16번째(추가 2장)는 2028.05.15, 복식 추가 4조는 2028.05.22, 잔여 단식은 2028.06.05에 정해진다.</li></ol></section>')
    body += ('<section id="howto"><h2>기록 방법</h2><div class="howto"><ol>'
             '<li><code>tools/tt/live.json</code>의 <code>events</code>에서 해당 경로 <code>rows[].q</code>에 <code>{"noc":"KOR","ko":"대한민국","players":"선수명","st":"잠정"}</code>을 추가한다.</li>'
             '<li><code>log</code> 맨 앞에 <code>{"d":"2027.11.30","ev":"대회명","txt":"내용","src":[["출처명","URL"]]}</code>을 추가하고 <code>asof</code> 날짜를 바꾼다.</li>'
             '<li>사이트 루트에서 <code>python3 tools/ttpages.py</code>를 실행하면 이 문서와 세부종목 자리 그림이 함께 갱신된다.</li>'
             '<li>확정 명단이 나오면 <code>athletes</code>에 <code>"KOR":[3,3]</code>처럼 남녀 인원을 적어 추정치를 덮어쓴다.</li></ol></div></section>')
    body += ('<section id="sources"><h2>출처</h2>' + src_list([(WIKI24, "Wikipedia · 2024 탁구 예선 (트래킹 형식 참고)")])
             + '<p class="note">ITTF는 각 예선 결과를 대회 후 2일 이내 ITTF.com에 게시한다(E.1).</p></section>')
    items = [("log", "업데이트 로그"), ("summary", "국가별 쿼터 요약"), ("events", "세부종목별 확보 현황"), ("timeline", "예선 일정"), ("notes", "주석"), ("howto", "기록 방법"), ("sources", "출처")]
    nreal = len({q["noc"] for E in DATA["events"] for r in E["rows"] for q in r["q"] if q.get("st") != "조건부"})
    box = [("기준일", DATA["asof"]), ("확보 NOC", f"{nreal} (조건부 미국 제외)"), ("다음 예선", "2027.06.20–22 유럽 혼성 단체 (이스탄불)"),
           ("총 쿼터", "172명 · 혼성 단체 16 · 복식 16조×3 · 단식 64×2")]
    return page(LIVE, "탁구 쿼터 트래킹", "탁구 쿼터 트래킹 (라이브 현황)",
                "LA28 탁구 출전 쿼터가 어느 나라에 배정됐는지 기록하는 문서다. Wikipedia 예선 문서처럼 국가별 요약과 세부종목별 표를 함께 둔다.",
                "LA28 탁구 쿼터 확보 현황: 국가별 요약, 세부종목별 확보 표, 업데이트 로그", items, body, "쿼터 트래킹", box, f"기준 {DATA['asof']}")


def build_moved(fname, title, links):
    body = ('<section id="moved"><h2>문서가 나뉘었습니다</h2><p>LA28 탁구 문서는 세부종목별 탭으로 정리했습니다. 아래 문서로 이동하세요.</p><ul>'
            + "".join(f'<li><a href="./{f}">{n}</a></li>' for f, n in links) + '</ul></section>')
    return page(fname, title, title, "이 문서는 세부종목 문서로 나뉘었습니다.", f"{title}: 세부종목 문서 안내", [("moved", "문서 이동")], body,
                title, [("이동", " · ".join(n for f, n in links))], f"규정 확인 {CHECK}")


if __name__ == "__main__":
    out = [build_main()] + [build_event(k) for k, *_ in EVENTS] + [build_live()]
    out.append(build_moved("oltabletennis-doubles.html", "탁구 복식", [("oltabletennis-xd.html", "혼합복식"), ("oltabletennis-md.html", "남자 복식"), ("oltabletennis-wd.html", "여자 복식")]))
    out.append(build_moved("oltabletennis-singles.html", "탁구 단식", [("oltabletennis-ms.html", "남자 단식"), ("oltabletennis-ws.html", "여자 단식")]))
    print("\n".join(out))
