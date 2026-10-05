# -*- coding: utf-8 -*-
"""카누 스프린트: 보트 지도·배정 순서·아시아 K2 2척·한국 경로 그림 + ICF OQR 기반 카약 선발 예시 (멱등).
근거: ICF LA28 Qualification System – Canoe Sprint (IOC 게시 PDF, 2026.05.12판) · ICF OQR Live (rankings.canoeicf.com, 2026.09.25)"""
import json, os, re, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from athletes import page, toc, infobox, tabs_html, footer_nav, ICON, e

SITE = "/root/site/"
HERE = os.path.dirname(os.path.abspath(__file__))
O = json.load(open(os.path.join(HERE, "csp", "oqr.json"), encoding="utf-8"))
P = "olcanoe"
SIM = f"{P}-kayak.html"
PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/CSP-LA28-Qualification-System.pdf"
NAVY, BLUE, LBLUE, ORG, LORG, GREY, LGREY, INK, MUTE, TEAL = "#233e50", "#2454a6", "#eaf0fa", "#b9734f", "#f6e9e1", "#a2a9b1", "#eef0f2", "#202122", "#54595d", "#267b76"
FONT = 'font-family="Arial, Malgun Gothic, sans-serif"'
NK = {"KOR": "한국", "CHN": "중국", "JPN": "일본", "UZB": "우즈베키스탄", "KAZ": "카자흐스탄", "KGZ": "키르기스스탄", "IND": "인도", "SGP": "싱가포르",
      "HKG": "홍콩", "TPE": "대만", "THA": "태국", "VIE": "베트남", "HUN": "헝가리", "GER": "독일", "POR": "포르투갈", "LTU": "리투아니아", "ESP": "스페인",
      "SRB": "세르비아", "DEN": "덴마크", "CZE": "체코", "POL": "폴란드", "AUS": "호주", "USA": "미국", "ITA": "이탈리아", "SVK": "슬로바키아",
      "BEL": "벨기에", "SWE": "스웨덴", "GBR": "영국", "MEX": "멕시코", "NOR": "노르웨이", "NED": "네덜란드", "ARG": "아르헨티나"}
CK = {"EUR": "유럽", "ASI": "아시아", "PAN": "팬암", "OCE": "오세아니아", "AFR": "아프리카"}
STYLE = ('<style>.csp-fig{margin:12px 0 18px;padding:12px 14px;background:#f8f9fa;border:1px solid #eaecf0}.csp-fig svg{display:block;width:100%;height:auto;max-width:860px}'
         '.csp-fig figcaption{font-size:13px;color:#54595d;margin-top:8px;line-height:1.6}.csp-sel{font-size:14px}.csp-sel tr.kor-row td{background:#f6e9e1;font-weight:700}'
         '@media(max-width:600px){.csp-fig{overflow-x:auto}.csp-fig svg{min-width:600px}}</style>')


def fig(svg, cap, label):
    return f'<figure class="csp-fig"><svg viewBox="{svg[0]}" role="img" aria-label="{e(label)}"><g {FONT}>{svg[1]}</g></svg><figcaption>{cap}</figcaption></figure>'


def boat(x, y, crew, color, dashed=False, mark=False):
    w = crew * 13 + 18
    d = ' stroke-dasharray="4 3"' if dashed else ""
    out = (f'<path d="M{x} {y + 9}Q{x + 6} {y} {x + 16} {y}H{x + w - 16}Q{x + w - 6} {y} {x + w} {y + 9}Q{x + w - 6} {y + 18} {x + w - 16} {y + 18}H{x + 16}Q{x + 6} {y + 18} {x} {y + 9}Z" '
           f'fill="{"#fff" if dashed else color}" stroke="{"#5c2e14" if mark else color}" stroke-width="{2.6 if mark else 1.4}"{d}/>')
    for k in range(crew):
        out += f'<circle cx="{x + 15 + k * 13}" cy="{y + 9}" r="3.6" fill="{color if dashed else "#fff"}"/>'
    return out, w


# ------------------------------------------------------------------ 그림 1: 성별 117석 보트 지도
def svg_boats():
    rows = [("K4 500m", 4, [("OQR", 11, BLUE, False, 0)], "44명 = OQR 11척"),
            ("K2 500m", 2, [("OQR", 4, BLUE, False, 0), ("대륙", 5, ORG, False, 2)], "18명 = OQR 4척 + 대륙 5척(아시아 2척)"),
            ("K1", 1, [("OQR", 6, BLUE, False, 0), ("개최국", 1, GREY, True, 0), ("대륙", 8, ORG, False, 2)], "15명 = OQR 6 + 개최국 1 + 대륙 8(아시아 2)"),
            ("C2 500m", 2, [("OQR", 8, TEAL, False, 0), ("대륙", 5, ORG, False, 2)], "26명 = OQR 8척 + 대륙 5척(아시아 2척)"),
            ("C1", 1, [("OQR", 5, TEAL, False, 0), ("개최국", 1, GREY, True, 0), ("대륙", 8, ORG, False, 2)], "14명 = OQR 5 + 개최국 1 + 대륙 8(아시아 2)")]
    b = f'<text x="14" y="22" font-size="15" font-weight="700" fill="{INK}">카누 스프린트 · 성별 117석을 보트로 보면 (남녀 동일 구조)</text>'
    y = 44
    maxx = 0
    for name, crew, groups, note in rows:
        b += f'<text x="14" y="{y + 14}" font-size="13" font-weight="700" fill="{INK}">{name}</text>'
        x = 92
        for lab, n, col, dashed, asia in groups:
            for i in range(n):
                s, w = boat(x, y, crew, col, dashed, mark=(lab == "대륙" and i < asia))
                b += s
                x += w + (6 if crew > 1 else 4)
            x += 10
        b += f'<text x="92" y="{y + 34}" font-size="12" fill="{MUTE}">{note}</text>'
        maxx = max(maxx, x)
        y += 50
    leg = [(BLUE, "카약 OQR(국가 랭킹)"), (TEAL, "카누 OQR"), (ORG, "2028 대륙 예선"), (GREY, "개최국(미국)")]
    lx = 14
    for c, t in leg:
        b += f'<rect x="{lx}" y="{y + 4}" width="14" height="10" rx="5" fill="{c}"/><text x="{lx + 20}" y="{y + 13}" font-size="12" fill="{INK}">{t}</text>'
        lx += 170
    b += f'<rect x="{lx}" y="{y + 3}" width="14" height="12" rx="5" fill="{ORG}" stroke="#5c2e14" stroke-width="2.6"/><text x="{lx + 20}" y="{y + 13}" font-size="12" fill="#5c2e14" font-weight="700">진한 테두리 = 아시아 몫</text>'
    return fig((f"0 0 {max(maxx, 860) + 10} " + str(y + 28), b), "보트 한 척 = 한 나라. 점 하나가 선수 1명(쿼터 1장)입니다. K4는 대륙 예선이 없고 OQR 11척뿐이며, 아시아가 대륙 예선으로 가져갈 수 있는 것은 성별·범주마다 K2(C2) 2척과 K1(C1) 2명입니다.", "카누 스프린트 보트 지도")


# ------------------------------------------------------------------ 그림 2: 배정 순서
def svg_flow():
    steps = [("① K4", "OQR 상위 11개국 × 4명", "최소 4개 대륙", LBLUE, BLUE),
             ("② K2", "상위 4개국 × 2명", "K4 받은 나라는 제외", LBLUE, BLUE),
             ("③ K1", "상위 6개국 × 1명", "K4 나라는 최대 5개국", LBLUE, BLUE),
             ("④ 대륙 예선 (2028)", "아시아: K2 2척 · K1 2명", "OQR 카약 0장 나라만", LORG, ORG)]
    b = f'<text x="14" y="22" font-size="15" font-weight="700" fill="{INK}">카약 배정 순서 — OQR 잠금 2027.12.31, 큰 배부터</text>'
    for i, (a, c, d, f, s) in enumerate(steps):
        x = 14 + i * 214
        b += (f'<rect x="{x}" y="38" width="198" height="84" rx="6" fill="{f}" stroke="{s}" stroke-width="1.5"/>'
              f'<text x="{x + 99}" y="62" font-size="15" font-weight="700" text-anchor="middle" fill="{INK}">{a}</text>'
              f'<text x="{x + 99}" y="86" font-size="13" text-anchor="middle" fill="{INK}">{c}</text>'
              f'<text x="{x + 99}" y="108" font-size="12" text-anchor="middle" fill="{MUTE}">{d}</text>')
        if i < 3:
            b += f'<path d="M{x + 200} 80h12" stroke="{GREY}" stroke-width="2"/><path d="M{x + 207} 75l6 5-6 5" fill="none" stroke="{GREY}" stroke-width="2"/>'
    b += (f'<text x="14" y="146" font-size="12" fill="{MUTE}">카누(C) 범주도 같은 방식: C2 상위 8개국 × 2명 → C1 상위 5개국 × 1명 → 대륙 예선(아시아 C2 2척·C1 2명). '
          '쿼터는 나라에 주어지며, 딴 선수와 실제 출전 선수는 달라도 됩니다.</text>')
    return fig(("0 0 870 160", b), "앞 단계에서 자리를 얻은 나라는 다음 단계 대상에서 빠지거나 제한을 받습니다. 그래서 K2 랭킹이 높아도 K4를 이미 딴 나라는 K2 자리를 받지 않습니다.", "카약 배정 순서")


# ------------------------------------------------------------------ 시뮬레이션
def sim(g):
    k4, k2, k1 = O[g + "k4"], O[g + "k2"], O[g + "k1"]
    cont = {r["noc"]: r["cont"] for r in k4 + k2 + k1}
    top = [r["noc"] for r in k4[:11]]
    swapped_out, swapped_in = [], []
    conts = {cont[n] for n in top}
    for r in k4[11:]:
        if len(conts) >= 4:
            break
        if r["cont"] not in conts:
            for n in reversed(top):
                if sum(1 for m in top if cont[m] == cont[n]) > 1:
                    top.remove(n); swapped_out.append(n); break
            top.append(r["noc"]); swapped_in.append(r["noc"]); conts.add(r["cont"])
    K2 = [r["noc"] for r in k2 if r["noc"] not in top][:4]
    K1, k4n, k1skip = [], 0, []
    for r in k1:
        if len(K1) == 6:
            break
        if r["noc"] in top:
            if k4n >= 5:
                k1skip.append(r["noc"]); continue
            k4n += 1
        K1.append(r["noc"])
    q = set(top) | set(K2) | set(K1)
    asia = [r for r in k2 if r["cont"] == "ASI" and r["noc"] not in q]
    asia_out = [r["noc"] for r in k2 if r["cont"] == "ASI" and r["noc"] in q]
    return dict(K4=top, K2=K2, K1=K1, swapped_out=swapped_out, swapped_in=swapped_in, k1skip=k1skip, asia=asia, asia_out=asia_out)


def ladder(g, ev, n, title):
    S = sim(g)
    rows = O[g + ev][:n]
    per, cw, ch = 10, 74, 42
    b = f'<text x="14" y="22" font-size="14" font-weight="700" fill="{INK}">{title}</text>'
    for i, r in enumerate(rows):
        noc = r["noc"]
        x, y = 14 + (i % per) * (cw + 5), 34 + (i // per) * (ch + 6)
        sel = noc in S[ev.upper()]
        if ev == "k4":
            st = "swap" if noc in S["swapped_in"] else ("sel" if sel else ("out" if noc in S["swapped_out"] else ""))
        elif ev == "k2":
            st = "sel" if sel else ("excl" if noc in S["K4"] else "")
        else:
            st = "sel" if sel else ("excl" if noc in S["k1skip"] else "")
        fill, tc, stroke = {"sel": (BLUE, "#fff", BLUE), "swap": (ORG, "#fff", ORG), "excl": (LGREY, MUTE, GREY), "out": (LGREY, MUTE, GREY)}.get(st, ("#fff", MUTE, GREY))
        kor = noc == "KOR"
        b += f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="4" fill="{fill}" stroke="{ORG if kor else stroke}" stroke-width="{3 if kor else 1}"/>'
        b += f'<text x="{x + cw / 2}" y="{y + 17}" font-size="12" font-weight="700" text-anchor="middle" fill="{tc}">{r["rank"]}위 {noc}</text>'
        b += f'<text x="{x + cw / 2}" y="{y + 33}" font-size="11" text-anchor="middle" fill="{tc}">{r["pts"]:,}점</text>'
        if st in ("excl", "out"):
            b += f'<path d="M{x + 6} {y + 6}L{x + cw - 6} {y + ch - 6}" stroke="{GREY}" stroke-width="1.3"/>'
    rws = (n + per - 1) // per
    ly = 34 + rws * (ch + 6) + 14
    leg = {"k4": [(BLUE, "K4 출전권"), (ORG, "4개 대륙 조건으로 들어감"), (LGREY, "대륙 조건 때문에 밀려남")],
           "k2": [(BLUE, "K2 출전권"), (LGREY, "이미 K4 보유 → 제외")],
           "k1": [(BLUE, "K1 출전권"), (LGREY, "K4 나라 5개국 한도 초과")]}[ev]
    lx = 14
    for c, t in leg:
        b += f'<rect x="{lx}" y="{ly - 11}" width="14" height="14" rx="2" fill="{c}" stroke="{GREY if c == LGREY else c}"/><text x="{lx + 20}" y="{ly}" font-size="12" fill="{INK}">{t}</text>'
        lx += 210
    b += f'<rect x="{lx}" y="{ly - 11}" width="14" height="14" rx="2" fill="#fff" stroke="{ORG}" stroke-width="3"/><text x="{lx + 20}" y="{ly}" font-size="12" fill="{INK}">한국</text>'
    return (f"0 0 {14 + per * (cw + 5) + 10} {ly + 12}", b)


def svg_asia(g):
    S = sim(g)
    gl = "남자" if g == "m" else "여자"
    b = f'<text x="14" y="22" font-size="15" font-weight="700" fill="{INK}">{gl} 카약 · 2028 아시아 대륙 예선 — K2 2척(2쌍)과 K1 2명</text>'
    b += f'<text x="14" y="44" font-size="12" fill="{MUTE}">참가 자격: OQR로 {gl} 카약 쿼터를 하나도 못 딴 아시아 나라 (현재 OQR K2 순위 순)</text>'
    out = S["asia_out"]
    x = 14
    for n in out:
        b += (f'<rect x="{x}" y="56" width="104" height="40" rx="5" fill="{LGREY}" stroke="{GREY}"/>'
              f'<text x="{x + 52}" y="74" font-size="12" font-weight="700" text-anchor="middle" fill="{MUTE}">{NK.get(n, n)}</text>'
              f'<text x="{x + 52}" y="89" font-size="11" text-anchor="middle" fill="{MUTE}">OQR 확보 → 불참</text>'
              f'<path d="M{x + 6} 62L{x + 98} 90" stroke="{GREY}"/>')
        x += 112
    for i, r in enumerate(S["asia"][:7]):
        kor = r["noc"] == "KOR"
        b += (f'<rect x="{x}" y="56" width="104" height="40" rx="5" fill="{LORG if kor else "#fff"}" stroke="{ORG if kor else GREY}" stroke-width="{3 if kor else 1}"/>'
              f'<text x="{x + 52}" y="74" font-size="12" font-weight="700" text-anchor="middle" fill="{INK}">{NK.get(r["noc"], r["noc"])}</text>'
              f'<text x="{x + 52}" y="89" font-size="11" text-anchor="middle" fill="{MUTE}">K2 {r["rank"]}위</text>')
        x += 112
    # 결과 슬롯
    bx = 14
    labels = [("K2 1척", 2, "1·2위 나라"), ("K2 1척", 2, "서로 다른 나라"), ("K1", 1, "남은 상위"), ("K1", 1, "남은 상위")]
    for i, (lab, crew, sub) in enumerate(labels):
        s, w = boat(bx + 10, 128, crew, ORG)
        b += f'<rect x="{bx}" y="116" width="180" height="62" rx="6" fill="#fff" stroke="{ORG}"/>' + s
        b += f'<text x="{bx + 10 + w + 10}" y="141" font-size="13" font-weight="700" fill="{INK}">{lab}</text><text x="{bx + 10}" y="168" font-size="11" fill="{MUTE}">{sub}</text>'
        bx += 192
    b += (f'<text x="14" y="204" font-size="12" fill="{INK}">• 한 나라는 대륙 예선에서 범주당 <tspan font-weight="700">최대 2장</tspan> → K2 1척을 따면 그 나라는 K1을 더 못 받고, 아시아 2척은 반드시 서로 다른 두 나라가 가져갑니다(H.2.4).</text>'
          f'<text x="14" y="224" font-size="12" fill="{INK}">• 같은 선수가 K2와 K1을 모두 따면 K2만 인정되고 K1 자리는 다음 나라로 넘어갑니다(H.2.3) · 종목마다 3개국 이상 출전해야 유효(D.4.6).</text>')
    return fig(("0 0 " + str(max(x, 790)) + " 236", b),
               f"{gl}: 대륙 예선 순위는 2028년 실제 레이스로 정합니다. 칩의 순서는 참고용 현재 OQR K2 순위입니다. "
               + ("한국은 남자 카약 쿼터가 없는 아시아 나라 중 K2 1위(종합 27위)로, 아시아 K2 2척 중 1척이 현실적 목표입니다." if g == "m"
                  else "한국 여자는 카자흐스탄·우즈베키스탄·일본 다음입니다. K2 2척 중 1척을 두고 경쟁해야 합니다."), f"{gl} 아시아 대륙 예선")


def svg_korea():
    S = sim("m")
    k4 = {r["noc"]: r for r in O["mk4"]}
    gap = O["mk4"][10]["pts"] - k4["KOR"]["pts"]
    b = f'<text x="14" y="22" font-size="15" font-weight="700" fill="{INK}">한국 남자 카약의 두 갈래 (OQR {O["date"]})</text>'
    b += (f'<rect x="14" y="40" width="200" height="70" rx="6" fill="{NAVY}"/><text x="114" y="68" font-size="14" font-weight="700" text-anchor="middle" fill="#fff">한국 남자 카약</text>'
          f'<text x="114" y="92" font-size="12" text-anchor="middle" fill="#d9e5ec">K4 {k4["KOR"]["rank"]}위 · K2 27위 · K1 48위</text>')
    b += f'<path d="M216 60h40v-10h20" fill="none" stroke="{BLUE}" stroke-width="2"/><path d="M216 92h40v52h20" fill="none" stroke="{ORG}" stroke-width="2"/>'
    b += (f'<rect x="280" y="28" width="300" height="56" rx="6" fill="{LBLUE}" stroke="{BLUE}"/><text x="292" y="50" font-size="13" font-weight="700" fill="{INK}">A · K4 OQR 11위 안 (현재 13위, {gap}점 부족)</text>'
          f'<text x="292" y="72" font-size="12" fill="{MUTE}">4장 확보 → K4 + 같은 선수로 K2·K1에도 출전 가능</text>')
    b += (f'<rect x="280" y="112" width="300" height="64" rx="6" fill="{LORG}" stroke="{ORG}"/><text x="292" y="134" font-size="13" font-weight="700" fill="{INK}">B · OQR 카약 0장 → 2028 아시아 예선</text>'
          f'<text x="292" y="154" font-size="12" fill="{MUTE}">K2 1척(2장)이 최대 · K1까지 합쳐 범주 2장 한도</text><text x="292" y="170" font-size="12" fill="{MUTE}">아시아 2척 중 1척 → 2쌍 경쟁이 핵심</text>')
    s, w = boat(600, 40, 4, BLUE)
    b += s + f'<text x="{606 + w}" y="54" font-size="12" fill="{INK}">4명</text>'
    s, w = boat(600, 130, 2, ORG, mark=True)
    b += s + f'<text x="{606 + w}" y="144" font-size="12" fill="{INK}">2명</text>'
    b += f'<text x="14" y="200" font-size="12" fill="{INK}">A를 이루면 B에 나갈 자격이 없어집니다(D.4.1). 반대로 K4·K2·K1 어느 OQR 자리도 못 얻어야 아시아 예선 K2 2척 경쟁에 들어갑니다.</text>'
    return fig(("0 0 760 214", b), "2026 아시안게임 K2·K4 500m 금(조광희·김효빈 등)은 OQR 반영 대회가 아니지만, 2028 아시아 예선 레이스에서 겨룰 상대(우즈베키스탄·카자흐스탄 등)에 대한 경쟁력을 보여 줍니다.", "한국 남자 카약 경로")


def sel_table(g):
    S = sim(g)
    k = {ev: {r["noc"]: r for r in O[g + ev]} for ev in ("k4", "k2", "k1")}
    rows = ""
    for ev, lab, per in (("K4", "K4 500m", 4), ("K2", "K2 500m", 2), ("K1", "K1", 1)):
        for i, n in enumerate(S[ev]):
            r = k[ev.lower()][n]
            note = "4개 대륙 조건" if n in S["swapped_in"] else ""
            rows += f'<tr><td>{lab}</td><td>{i + 1}</td><td>{NK.get(n, n)} <span class="muted">({n})</span></td><td>{CK[r["cont"]]}</td><td>{r["rank"]}위 · {r["pts"]:,}점</td><td>{per}장</td><td>{note}</td></tr>'
    gl = "남자" if g == "m" else "여자"
    return (f'<table class="data csp-sel"><caption>{gl} 카약 OQR 배정 예시 (OQR {O["date"]} · ICF 잠정 배정과 일치)</caption><thead><tr><th scope="col">종목</th><th scope="col">순번</th>'
            f'<th scope="col">나라</th><th scope="col">대륙</th><th scope="col">OQR</th><th scope="col">쿼터</th><th scope="col">비고</th></tr></thead><tbody>{rows}</tbody></table>')


CAVEAT = (f'<div class="notice"><b>잠정 예시입니다.</b> ICF OQR Live({O["date"]} 갱신) 순위로 계산했으며, 랭킹 기간(2026.04.20–2027.12.31)은 27%만 지났습니다. '
          '규정상 8개 최고 성적을 더하므로 2027년 세계선수권(1.5배)·월드컵·대륙선수권 결과로 크게 바뀔 수 있습니다.</div>')


def build_sim():
    secs = ""
    for g, gl in (("m", "남자"), ("w", "여자")):
        S = sim(g)
        secs += (f'<section id="{g}"><h2>{gl} 카약</h2>'
                 + fig(ladder(g, "k4", 20, f"{gl} K4 500m OQR 1–20위 → 11개국"),
                       f"상위 11개국이 4장씩 받되 4개 대륙 이상이어야 합니다. 현재 " + (f"4개 대륙 조건 때문에 {', '.join(NK.get(n, n) for n in S['swapped_in'])} 진입, {', '.join(NK.get(n, n) for n in S['swapped_out'])} 제외." if S["swapped_in"] else "조건을 이미 충족합니다."), f"{gl} K4 사다리")
                 + fig(ladder(g, "k2", 20, f"{gl} K2 500m OQR 1–20위 → 4개국"), "K4를 받은 나라를 건너뛰고 남은 상위 4개국이 2장씩 받습니다.", f"{gl} K2 사다리")
                 + fig(ladder(g, "k1", 20, f"{gl} K1 OQR 1–20위 → 6개국"), "K4 보유국은 최대 5개국까지만 K1을 더 받을 수 있습니다.", f"{gl} K1 사다리")
                 + sel_table(g) + svg_asia(g) + "</section>")
    main = (toc([("rule", "배정 구조"), ("korea-path", "한국 남자 카약 경로"), ("m", "남자 카약"), ("w", "여자 카약"), ("sources", "출처")])
            + f'<section id="rule"><h2>배정 구조</h2>{CAVEAT}{svg_boats()}{svg_flow()}</section>'
            + f'<section id="korea-path"><h2>한국 남자 카약 경로</h2>{svg_korea()}</section>'
            + secs
            + f'<section id="sources"><h2>출처</h2><ol class="sources"><li><a href="{PDF}">ICF · LA28 Qualification System – Canoe Sprint (IOC 게시 PDF, 2026.05.12판) D.2–D.5·H</a></li>'
              f'<li><a href="{O["source"]}">ICF · Canoe Sprint Olympic Qualification Rankings (OQR Live, {O["date"]} 갱신, 2026.10.06 조회)</a></li></ol>'
              '<p class="small">개최국 미국 자리(D.5): 미국이 그 범주에서 이미 쿼터를 얻으면 K1/C1 랭킹 차순위 국가로 넘어갑니다(F.2). 현재 남자는 미국이 K4를 가져가 개최국 자리가 넘어갑니다.</p></section>')
    box = infobox("카누 · 카약 선발 예시", [("기준", f"ICF OQR {O['date']}"), ("카약 OQR", "K4 11척 · K2 4척 · K1 6명"), ("아시아 대륙 예선", "K2 2척 · K1 2명 (성별)"),
                                         ("한국 남자", "K4 13위 · 아시아 예선 자격국 중 K2 1위"), ("한국 여자", "아시아 예선 자격국 중 K2 4위")],
                  f'<p class="small"><a href="./{P}-sprint.html">스프린트 예선 규정 →</a></p>')
    tabs, _ = tabs_html(P, "카누", cur=SIM)
    nav = (f'<nav class="sport-nav" aria-label="상위 문서"><a href="./{P}.html">↑ 카누 전체 안내</a></nav>'
           + (f'<a class="athlete-link" href="./{P}-athletes.html">{ICON}<span>한국 선수</span></a>' if os.path.exists(SITE + f"{P}-athletes.html") else ""))
    t = page("카약 선발 예시 | 카누 · 올림픽예선", "LA28 카누 스프린트 카약 배정 구조 그림과 ICF OQR 기반 선발 예시", nav, "카누 스프린트 · 카약 선발 예시",
             "보트 크기 순서(K4 → K2 → K1)로 배정되는 카약 쿼터를 그림으로 풀고, 현재 ICF 올림픽 예선 랭킹(OQR)에 규정을 적용한 예시와 아시아 대륙 예선 K2 2척 경쟁을 보여 줍니다.",
             tabs, main, box, footer_nav(P, "카누"), f"카누 · 카약 선발 예시 | OQR {O['date']}")
    if not os.path.exists(SITE + f"{P}-athletes.html"):
        t = t.replace(f'<a href="./{P}-athletes.html">한국 선수</a>', "")
    open(SITE + SIM, "w", encoding="utf-8", newline="\r\n").write(t.replace("</head>", STYLE + "</head>", 1))


MS, ME = "<!-- cspfig:start -->", "<!-- cspfig:end -->"


def put(t, block, sec):
    blk = MS + block + ME
    if MS in t:
        return t[:t.index(MS)] + blk + t[t.index(ME) + len(ME):]
    i = t.index(f'<section id="{sec}">'); j = t.index("</section>", i)
    return t[:j] + blk + t[j:]


def patch():
    for f in glob.glob(SITE + P + "*.html"):
        b = os.path.basename(f)
        if b == SIM:
            continue
        t = open(f, encoding="utf-8", newline="").read(); o = t
        for nav in ("golf-nav", "footer-nav"):
            m = re.search(rf'<nav class="{nav}"[^>]*>.*?</nav>', t, re.S)
            if m and SIM not in m.group(0):
                seg = re.sub(r'(<a href="\./olcanoe-slalom\.html"[^>]*>[^<]*</a>)', r'\1' + f'<a href="./{SIM}">카약 선발 예시</a>', m.group(0), count=1)
                t = t[:m.start()] + seg + t[m.end():]
        if b in (f"{P}.html", f"{P}-sprint.html"):
            if ".csp-fig{" not in t:
                t = t.replace("</head>", STYLE + "</head>", 1)
            blk = ('<h3 id="csp-pictures">그림으로 보는 스프린트 배정</h3>' + svg_boats() + svg_flow()
                   + (svg_korea() if b == f"{P}-sprint.html" else "")
                   + f'<p class="small">현재 ICF 순위에 규정을 적용한 국가별 예시와 아시아 대륙 예선 K2 2척 경쟁은 <a href="./{SIM}">카약 선발 예시</a>에 있습니다.</p>')
            t = put(t, blk, "pathway")
        if t != o:
            open(f, "w", encoding="utf-8", newline="").write(t)
            print("patched", b)


if __name__ == "__main__":
    patch()
    build_sim()
    print("built", SIM)
