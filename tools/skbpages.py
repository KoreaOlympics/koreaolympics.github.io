# -*- coding: utf-8 -*-
"""스케이트보딩: LA28 선발 구조 그림 + WSR 기반 선발 시뮬레이션 (멱등).
근거: World Skate LA28 Qualification System (2026.07.10판) D.1–D.3 · WSR(wyldata 공식 위젯) 2026.10.01판"""
import json, re, os, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from athletes import page, toc, infobox, tabs_html, footer_nav, ICON, e

SITE = "/root/site/"
HERE = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(HERE, "skb", "wsr.json"), encoding="utf-8"))
P = "olskateboard"
SIM = f"{P}-sim.html"
WSR_URL = "https://www.worldskate.org/skateboarding/ranking-wsr.html"
PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/SKB-LA28-Qualification-System.pdf"
EVENTS = [("M-street", "남자 스트리트", "street-men"), ("W-street", "여자 스트리트", "street-women"),
          ("M-park", "남자 파크", "park-men"), ("W-park", "여자 파크", "park-women")]
CONT = {"Africa": "RSA MAR SEN NIG".split(), "Oceania": "AUS NZL".split(), "Asia": "JPN KOR CHN TPE PHI THA INA".split(),
        "Americas": "USA BRA PUR ARG CHI PER COL MEX CAN".split()}
CK = {"Africa": "아프리카", "Americas": "아메리카", "Asia": "아시아", "Europe": "유럽", "Oceania": "오세아니아", "Neutral": "중립"}
NK = {"JPN": "일본", "KOR": "한국", "BRA": "브라질", "USA": "미국", "AUS": "호주", "ESP": "스페인", "CHN": "중국", "RSA": "남아공",
      "NIG": "니제르", "PER": "페루", "ARG": "아르헨티나", "FRA": "프랑스", "ITA": "이탈리아", "GBR": "영국", "SVK": "슬로바키아",
      "SWE": "스웨덴", "POR": "포르투갈", "DEN": "덴마크", "FIN": "핀란드", "THA": "태국", "TPE": "대만", "PHI": "필리핀", "COL": "콜롬비아",
      "CAN": "캐나다", "NZL": "뉴질랜드", "CZE": "체코", "GER": "독일", "ISR": "이스라엘", "PUR": "푸에르토리코"}
KOR_NAME = {"Juni Kang": "강준이", "Jiyul Shin": "신지율", "Jibeen Park": "박지빈"}
NAVY, BLUE, LBLUE, ORG, LORG, GREY, LGREY, INK, MUTE = "#233e50", "#2454a6", "#eaf0fa", "#b9734f", "#f6e9e1", "#a2a9b1", "#eef0f2", "#202122", "#54595d"
FONT = 'font-family="Arial, Malgun Gothic, sans-serif"'


def cont(n):
    for c, l in CONT.items():
        if n in l:
            return c
    return "Neutral" if n == "NIA" else "Europe"


def simulate(ev):
    rows = [(int(r[0]), r[2], r[3], int(r[1].replace(",", ""))) for r in W[ev]]
    a = W["africa"][ev]
    pool = rows + [(int(a[0]), a[2], a[3], int(a[1].replace(",", "")))]
    cnt, capped, status = {}, [], {}
    for rk, nm, n, pt in pool:
        if cnt.get(n, 0) >= 3:
            status[rk] = "cap"
            continue
        cnt[n] = cnt.get(n, 0) + 1
        capped.append((rk, nm, n, pt))
    k = 0
    while True:
        top = capped[:20 - k]
        miss = [c for c in ["Africa", "Americas", "Asia", "Europe", "Oceania"] if c not in {cont(x[2]) for x in top}]
        if len(miss) == k:
            break
        k = len(miss)
    conts = [next(x for x in capped[20 - k:] if cont(x[2]) == c) for c in miss]
    for x in top:
        status[x[0]] = "rank"
    for x in conts:
        status[x[0]] = "cont"
    nxt = next(x for x in capped[20 - k:] if x not in conts)  # 개최국 자리가 비면 받는 다음 선수
    host_in = any(x[2] == "USA" for x in top + conts)
    return {"top": top, "conts": conts, "miss": miss, "status": status, "rows": rows, "next": nxt, "host_in": host_in,
            "cut": [r for r in rows if status.get(r[0]) == "cap" and r[0] <= top[-1][0]]}


def kname(nm):
    return f"{KOR_NAME[nm]} ({nm})" if nm in KOR_NAME else nm


# ------------------------------------------------------------------ 그림 1: 22석 구조
def svg_structure():
    b = f'<text x="20" y="22" font-size="15" font-weight="700" fill="{INK}">세부종목마다 22석 (남녀 파크·스트리트 4개 × 22 = 88명)</text>'
    for i in range(22):
        x, y = 20 + i * 31, 44
        if i < 19:
            f, s, d = BLUE, BLUE, ""
        elif i == 19:
            f, s, d = ORG, ORG, ""
        else:
            f, s, d = "#fff", (GREY if i == 21 else NAVY), ' stroke-dasharray="4 3"'
        b += f'<rect x="{x}" y="{y}" width="26" height="34" rx="3" fill="{f}" stroke="{s}" stroke-width="1.6"{d}/>'
    b += f'<path d="M20 86h613" stroke="{BLUE}" stroke-width="2"/><path d="M20 82v8M633 82v8" stroke="{BLUE}" stroke-width="2"/>'
    b += f'<text x="326" y="104" font-size="13" text-anchor="middle" fill="{BLUE}" font-weight="700">WSR 20석 (2028.06.11 랭킹 · 국가당 최대 3명)</text>'
    b += f'<text x="602" y="124" font-size="12" text-anchor="middle" fill="{ORG}" font-weight="700">대륙 보장석은 20석 안</text>'
    b += f'<text x="653" y="40" font-size="11" text-anchor="middle" fill="{NAVY}">개최국</text><text x="684" y="96" font-size="11" text-anchor="middle" fill="{MUTE}">보편성</text>'
    # 흐름
    steps = [("① WSR 순위대로", "1위부터 내려가며"), ("② 국가 상한", "한 나라 4번째부터 건너뜀"), ("③ 대륙 보장", "20석에 없는 대륙 최상위"), ("④ 개최국·보편성", "미국 미선발 시 1 · 보편성 1")]
    for i, (a, c) in enumerate(steps):
        x = 20 + i * 172
        b += f'<rect x="{x}" y="146" width="158" height="54" rx="4" fill="{LBLUE if i < 2 else (LORG if i == 2 else LGREY)}" stroke="{BLUE if i < 2 else (ORG if i == 2 else GREY)}"/>'
        b += f'<text x="{x + 79}" y="168" font-size="13" font-weight="700" text-anchor="middle" fill="{INK}">{a}</text><text x="{x + 79}" y="188" font-size="12" text-anchor="middle" fill="{MUTE}">{c}</text>'
        if i < 3:
            b += f'<path d="M{x + 160} 173h10" stroke="{GREY}" stroke-width="2"/><path d="M{x + 166} 169l5 4-5 4" fill="none" stroke="{GREY}" stroke-width="2"/>'
    return (f'<figure class="skb-fig"><svg viewBox="0 0 720 214" role="img" aria-label="스케이트보딩 세부종목 22석 구조"><g {FONT}>{b}</g></svg>'
            '<figcaption>파란 칸 = 랭킹으로 뽑히는 자리, 주황 칸 = 대륙 보장석(20석 안에 포함), 점선 = 개최국·보편성(20석 밖). 대륙 보장석이 쓰이는 만큼 랭킹으로 뽑히는 인원이 줄어듭니다.</figcaption></figure>')


# ------------------------------------------------------------------ 그림 2: 18~19명이 되는 원리
def svg_why():
    def row(y, k, title, note):
        out = f'<text x="20" y="{y - 8}" font-size="13" font-weight="700" fill="{INK}">{title}</text>'
        for i in range(20):
            c = BLUE if i < 20 - k else ORG
            out += f'<rect x="{20 + i * 25}" y="{y}" width="21" height="22" rx="3" fill="{c}"/>'
        out += f'<text x="530" y="{y + 16}" font-size="12" fill="{MUTE}">{note}</text>'
        return out
    b = (row(30, 0, "5개 대륙이 모두 랭킹 20위(상한 적용) 안에 있을 때", "랭킹 20 + 대륙 0")
         + row(84, 1, "한 대륙(보통 아프리카)이 없을 때 — 현재 4개 세부종목 모두", "랭킹 19 + 대륙 1")
         + row(138, 2, "두 대륙(아프리카·오세아니아)이 없을 때", "랭킹 18 + 대륙 2"))
    return (f'<figure class="skb-fig"><svg viewBox="0 0 720 176" role="img" aria-label="대륙 보장석 수에 따른 랭킹 선발 인원"><g {FONT}>{b}</g></svg>'
            '<figcaption>대륙 보장석은 20석 밖에 따로 붙는 자리가 아니라 20석 안에서 마지막 순번을 대신합니다. 그래서 국가 상한을 적용한 랭킹으로 실제 뽑히는 사람은 보통 18~19명입니다.</figcaption></figure>')


# ------------------------------------------------------------------ 그림 3: 랭킹 사다리
def svg_ladder(ev, label):
    S = simulate(ev)
    last = S["top"][-1][0]
    n = max(30, last + 2)
    n = min(n, len(S["rows"]))
    per, cw, ch = 10, 64, 40
    rows_ = (n + per - 1) // per
    b = f'<text x="14" y="22" font-size="14" font-weight="700" fill="{INK}">{label} · WSR {W["date"]} 기준 1–{n}위</text>'
    byrank = {r[0]: r for r in S["rows"]}
    for i in range(n):
        rk = i + 1
        r = byrank[rk]
        st = S["status"].get(rk)
        x, y = 14 + (i % per) * (cw + 4), 34 + (i // per) * (ch + 6)
        kor = r[2] == "KOR"
        if st == "rank":
            fill, tc, stroke = BLUE, "#fff", BLUE
        elif st == "cap":
            fill, tc, stroke = LGREY, MUTE, GREY
        else:
            fill, tc, stroke = "#fff", MUTE, GREY
        b += f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="4" fill="{fill}" stroke="{ORG if kor else stroke}" stroke-width="{3 if kor else 1}"/>'
        b += f'<text x="{x + cw / 2}" y="{y + 16}" font-size="12" font-weight="700" text-anchor="middle" fill="{tc}">{rk}위</text>'
        b += f'<text x="{x + cw / 2}" y="{y + 32}" font-size="11" text-anchor="middle" fill="{tc}">{r[2]}</text>'
        if st == "cap":
            b += f'<path d="M{x + 6} {y + 6}L{x + cw - 6} {y + ch - 6}" stroke="{GREY}" stroke-width="1.4"/>'
    yb = 34 + rows_ * (ch + 6) + 6
    cx = 14
    for c in S["conts"]:
        b += (f'<rect x="{cx}" y="{yb}" width="150" height="40" rx="4" fill="{ORG}"/>'
              f'<text x="{cx + 75}" y="{yb + 17}" font-size="12" font-weight="700" text-anchor="middle" fill="#fff">대륙 보장 · {CK[cont(c[2])]}</text>'
              f'<text x="{cx + 75}" y="{yb + 33}" font-size="11" text-anchor="middle" fill="#fff">{c[0]}위 {c[2]}</text>')
        cx += 160
    nr = len(S["top"])
    b += f'<text x="{cx + 6}" y="{yb + 25}" font-size="13" fill="{INK}"><tspan font-weight="700" fill="{BLUE}">랭킹 {nr}명</tspan> + <tspan font-weight="700" fill="{ORG}">대륙 {len(S["conts"])}명</tspan> = 20석</text>'
    ly = yb + 62
    leg = [(BLUE, BLUE, "랭킹 선발"), (LGREY, GREY, "국가 상한(3명)으로 제외"), ("#fff", GREY, "20석 밖"), ("#fff", ORG, "한국 선수")]
    lx = 14
    for f, s, t in leg:
        b += f'<rect x="{lx}" y="{ly - 11}" width="14" height="14" rx="2" fill="{f}" stroke="{s}" stroke-width="{3 if t == "한국 선수" else 1}"/><text x="{lx + 20}" y="{ly}" font-size="12" fill="{INK}">{t}</text>'
        lx += 160
    H = ly + 14
    Wd = 14 + per * (cw + 4) + 10
    return (f'<figure class="skb-fig"><svg viewBox="0 0 {Wd} {H}" role="img" aria-label="{label} 선발 예시 랭킹 사다리"><g {FONT}>{b}</g></svg>'
            f'<figcaption>{label}: 국가 상한으로 {len(S["cut"])}명이 건너뛰어지고, 랭킹 {S["top"][-1][0]}위({e(S["top"][-1][1])})까지 {nr}명이 들어갑니다. '
            f'20석 안에 없는 {", ".join(CK[m] for m in S["miss"]) or "대륙"}은 대륙 보장석으로 채웁니다.</figcaption></figure>')


def sel_table(ev, label):
    S = simulate(ev)
    body = ""
    for i, x in enumerate(S["top"] + S["conts"]):
        route = "대륙 보장" if x in S["conts"] else "WSR 랭킹"
        kor = ' class="kor-row"' if x[2] == "KOR" else ""
        body += (f'<tr{kor}><td>{i + 1}</td><td>{x[0]}위</td><td>{e(kname(x[1]))}</td><td>{NK.get(x[2], x[2])} <span class="muted">({x[2]})</span></td>'
                 f'<td>{CK[cont(x[2])]}</td><td>{route}</td></tr>')
    cut = ", ".join(f"{r[0]}위 {e(r[1])}({r[2]})" for r in S["cut"])
    host = ("미국 선수가 이미 랭킹으로 들어 있어 개최국 자리는 쓰이지 않고, 상한을 지킨 다음 순위 "
            f"<b>{S['next'][0]}위 {e(S['next'][1])}({S['next'][2]})</b>에게 넘어갑니다(F.2)." if S["host_in"] else "미국 최상위 선수가 개최국 자리를 받습니다(D.2).")
    return (f'<table class="data skb-sel"><caption>{label} · 선발 예시 20명 (WSR {W["date"]} · 단순 적용)</caption><thead><tr><th scope="col">순번</th><th scope="col">WSR</th>'
            f'<th scope="col">선수</th><th scope="col">국가</th><th scope="col">대륙</th><th scope="col">경로</th></tr></thead><tbody>{body}</tbody></table>'
            f'<ul class="wnotes"><li>국가 상한으로 건너뛴 선수: {cut or "없음"}.</li><li>개최국: {host}</li><li>보편성 1자리는 삼자위원회가 정하며(대상: WSR 상위 50% 또는 50위 이내), 이 예시에는 넣지 않았습니다.</li></ul>')


def summary_table():
    body = ""
    for ev, label, slug in EVENTS:
        S = simulate(ev)
        kor = ", ".join(f"{KOR_NAME.get(x[1], x[1])}({x[0]}위)" for x in S["top"] + S["conts"] if x[2] == "KOR") or "—"
        c = ", ".join(f"{e(x[1])}({x[2]}, {x[0]}위)" for x in S["conts"])
        body += (f'<tr><th scope="row"><a href="./{P}-{slug}.html">{label}</a></th><td>{len(S["top"])}명 (~{S["top"][-1][0]}위)</td><td>{len(S["cut"])}명</td>'
                 f'<td>{c}</td><td>{kor}</td></tr>')
    return (f'<table class="data"><caption>4개 세부종목 선발 예시 요약 · WSR {W["date"]}</caption><thead><tr><th scope="col">세부종목</th><th scope="col">랭킹 선발</th>'
            f'<th scope="col">상한 제외</th><th scope="col">대륙 보장석</th><th scope="col">한국</th></tr></thead><tbody>{body}</tbody></table>')


CAVEAT = ('<div class="notice"><b>예시일 뿐입니다.</b> 현재 WSR(지난 18개월 성적)에는 LA28 포인트 인정 기간(2026.06.11~) 이전 성적이 섞여 있고, '
          '실제 선발은 2028.06.11 최종 WSR로 합니다. 규정 문장을 현재 순위에 그대로 적용한 단순 계산입니다.</div>')

FIG_CSS = ('<style>.skb-fig{margin:12px 0 18px;padding:12px 14px;background:#f8f9fa;border:1px solid #eaecf0}.skb-fig svg{display:block;width:100%;height:auto;max-width:720px}'
           '.skb-fig figcaption{font-size:13px;color:#54595d;margin-top:8px;line-height:1.6}.skb-sel{font-size:14px}.skb-sel tr.kor-row td{background:#f6e9e1;font-weight:700}'
           '@media(max-width:600px){.skb-fig{overflow-x:auto}.skb-fig svg{min-width:560px}}</style>')


def build_sim():
    secs = ""
    for ev, label, slug in EVENTS:
        secs += f'<section id="{slug}"><h2>{label}</h2>{svg_ladder(ev, label)}{sel_table(ev, label)}</section>'
    main = (toc([("rule", "선발 규칙"), ("summary", "요약")] + [(s, l) for _, l, s in EVENTS] + [("sources", "출처")])
            + f'<section id="rule"><h2>선발 규칙</h2>{CAVEAT}{svg_structure()}{svg_why()}'
              '<p>규정 D.1은 WSR(2028.06.11) 순위로 <b>국가당 세부종목 최대 3명</b>을 지키며 <b>대륙 보장석을 포함해</b> 20명을 채운다고 정합니다. '
              '5개 대륙(아프리카·아메리카·아시아·유럽·오세아니아) 중 20명 안에 없는 대륙은 그 대륙 최상위 선수가 들어가고, 그만큼 랭킹 선발 인원이 줄어듭니다.</p></section>'
            + f'<section id="summary"><h2>요약</h2>{summary_table()}<p>현재 4개 세부종목 모두 아프리카 선수가 랭킹 20명 안에 없어 <b>랭킹 19명 + 아프리카 1명</b>입니다. '
              '오세아니아는 호주 선수가 상위권에 있어 보장석이 필요 없습니다. 호주가 빠지는 종목이 생기면 18명이 됩니다.</p></section>'
            + secs
            + f'<section id="sources"><h2>출처</h2><ol class="sources"><li><a href="{PDF}">World Skate · LA28 Qualification System (IOC 게시 PDF, 2026.07.10판)</a></li>'
              f'<li><a href="{WSR_URL}">World Skate · World Skateboarding Ranking (WSR) — {W["date"]}판, 2026.10.06 조회</a></li></ol>'
              '<p class="small">대륙 구분은 올림픽 5개 대륙(남북 아메리카 통합) 기준이며 이스라엘은 유럽으로 계산했습니다. 아프리카 최상위는 WSR 대륙 필터로 확인했습니다.</p></section>')
    box = infobox("스케이트보딩 · 선발 예시", [("기준 랭킹", f"WSR {W['date']}"), ("세부종목 정원", "22명 (WSR 20 + 개최국 1 + 보편성 1)"),
                                           ("국가 상한", "세부종목 3명 · 성별 6명"), ("현재 결과", "4개 종목 모두 랭킹 19 + 대륙 1"),
                                           ("한국", "남 스트리트 강준이 · 여 스트리트 신지율·박지빈")],
                  f'<p class="small"><a href="./{P}-wsr.html">WSR 규정 안내 →</a></p>')
    tabs, _ = tabs_html(P, "스케이트보딩", cur=SIM)
    nav = (f'<nav class="sport-nav" aria-label="상위 문서"><a href="./{P}.html">↑ 스케이트보딩 전체 안내</a></nav>'
           f'<a class="athlete-link" href="./{P}-athletes.html">{ICON}<span>한국 선수</span></a>')
    t = page("선발 예시 | 스케이트보딩 · 올림픽예선", "LA28 스케이트보딩 WSR 선발 규칙 그림과 현재 랭킹 기준 선발 예시", nav, "스케이트보딩 선발 예시",
             "현재 WSR 순위에 LA28 규정(국가당 3명 · 대륙 보장 포함 20명)을 그대로 적용하면 누가 뽑히는지 보여 주는 예시 문서입니다.",
             tabs, main, box, footer_nav(P, "스케이트보딩"), f"스케이트보딩 · 선발 예시 | WSR {W['date']}")
    t = t.replace("</head>", FIG_CSS + "</head>", 1)
    open(SITE + SIM, "w", encoding="utf-8", newline="\r\n").write(t)


# ------------------------------------------------------------------ 기존 문서 패치
MS, ME = "<!-- skbfig:start -->", "<!-- skbfig:end -->"


def put(t, block, anchor_sec):
    blk = MS + block + ME
    if MS in t:
        return t[:t.index(MS)] + blk + t[t.index(ME) + len(ME):]
    i = t.index(f'<section id="{anchor_sec}">')
    j = t.index("</section>", i)
    return t[:j] + blk + t[j:]


def add_css(t):
    return t if ".skb-fig{" in t else t.replace("</head>", FIG_CSS + "</head>", 1)


def add_tab(t):
    for nav in ("golf-nav", "footer-nav"):
        m = re.search(rf'<nav class="{nav}"[^>]*>.*?</nav>', t, re.S)
        if m and SIM not in m.group(0):
            seg = m.group(0).replace(f'<a href="./{P}-athletes.html">', f'<a href="./{SIM}">선발 예시</a><a href="./{P}-athletes.html">', 1)
            t = t[:m.start()] + seg + t[m.end():]
    return t


def patch():
    for f in glob.glob(SITE + P + "*.html"):
        b = os.path.basename(f)
        if b == SIM:
            continue
        t = open(f, encoding="utf-8", newline="").read(); o = t
        t = add_tab(t)
        t = t.replace("박지빈은 WSR 24위지만 일본 선수 7명이 상한(3명)에 걸려 빠지면 19번째가 된다.",
                      "박지빈은 WSR 24위지만 그 앞의 일본 선수 5명(6·7·13·14·16위)이 상한(3명)에 걸려 빠지면 19번째가 된다.")
        if b == f"{P}.html":
            t = add_css(t)
            t = put(t, '<h3 id="skb-structure">그림으로 보는 선발 구조</h3>' + svg_structure() + svg_why()
                    + summary_table() + f'<p class="small">현재 WSR({W["date"]})을 규정에 단순 적용한 예시입니다. 세부종목별 명단은 <a href="./{SIM}">선발 예시</a> 문서에 있습니다.</p>', "pathway")
        elif b == f"{P}-wsr.html":
            t = add_css(t)
            t = put(t, svg_why() + f'<p class="small">4개 세부종목의 실제 적용 예시는 <a href="./{SIM}">선발 예시</a>를 보세요.</p>', "cap")
        else:
            for ev, label, slug in EVENTS:
                if b == f"{P}-{slug}.html":
                    t = add_css(t)
                    t = put(t, f'<h3 id="skb-example">선발 예시 (WSR {W["date"]})</h3>' + svg_ladder(ev, label)
                            + f'<p class="small">20명 명단과 상한 제외 선수는 <a href="./{SIM}#{slug}">선발 예시 · {label}</a>에 있습니다.</p>', "pathway")
        if t != o:
            open(f, "w", encoding="utf-8", newline="").write(t)
            print("patched", b)


if __name__ == "__main__":
    patch()
    build_sim()
    print("sim built")
