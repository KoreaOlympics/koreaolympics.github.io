# -*- coding: utf-8 -*-
"""수영(경영) 문서 서식 개선 (멱등). athletes.py 실행 뒤에 실행한다.
1) 전체 안내: 남녀 동일 선발 경로 표를 '남녀 공통' 하나로 합침
2) 전체 안내: 세부종목별 기준기록 표(세부 문서 링크·한국 주요 선수) 추가
3) 모든 수영 문서: 세부종목 2행 탭
4) 일정 표: 연도 구분 행"""
import re, glob, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from athletes import D, e

SITE = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))) + "/"
P = "olswimming"
NAV_S, NAV_E = "<!-- swnav:start -->", "<!-- swnav:end -->"
STD_S, STD_E = "<!-- swstd:start -->", "<!-- swstd:end -->"
CSS_S, CSS_E = "/* == swimming == */", "/* == /swimming == */"

GROUPS = [("자유형", [("free50", "50"), ("free100", "100"), ("free200", "200"), ("free400", "400"), ("free800", "800"), ("free1500", "1500")]),
          ("배영", [("back50", "50"), ("back100", "100"), ("back200", "200")]),
          ("평영", [("breast50", "50"), ("breast100", "100"), ("breast200", "200")]),
          ("접영", [("fly50", "50"), ("fly100", "100"), ("fly200", "200")]),
          ("개인혼영", [("im200", "200"), ("im400", "400")]),
          ("계영", [("relay4x100free", "400"), ("relay4x200free", "800"), ("relay4x100medley", "혼계영"), ("mixed4x100medley", "혼성 혼계영")])]
# World Aquatics 규정 H (olswimming-standards.html과 동일): 남 A, 남 B, 여 A, 여 B
STD = {"free50": ("21.69", "21.91", "24.56", "24.81"), "free100": ("47.86", "48.34", "53.60", "54.14"),
       "free200": ("1:45.83", "1:46.89", "1:56.43", "1:57.59"), "free400": ("3:45.46", "3:47.71", "4:06.27", "4:08.73"),
       "free800": ("7:47.04", "7:51.71", "8:26.71", "8:31.78"), "free1500": ("14:51.62", "15:00.54", "16:08.65", "16:18.34"),
       "back100": ("53.00", "53.53", "59.49", "1:00.08"), "back200": ("1:56.05", "1:57.21", "2:08.95", "2:10.24"),
       "breast100": ("59.27", "59.86", "1:06.10", "1:06.76"), "breast200": ("2:09.35", "2:10.64", "2:23.49", "2:24.92"),
       "fly100": ("51.06", "51.57", "57.38", "57.95"), "fly200": ("1:54.69", "1:55.84", "2:08.15", "2:09.43"),
       "im200": ("1:57.54", "1:58.72", "2:09.90", "2:11.20"), "im400": ("4:11.52", "4:14.04", "4:37.33", "4:40.10")}
LABEL = {"relay4x100free": "계영 400m", "relay4x200free": "계영 800m", "relay4x100medley": "혼계영 400m", "mixed4x100medley": "혼성 혼계영 400m"}


def ev(code):
    return f"{P}-ev-{code}.html"


def subnav(cur=None):
    out = '<nav class="golf-nav sub-nav swim-sub" aria-label="경영 세부종목">'
    for gl, items in GROUPS:
        out += f'<span class="sub-label">{gl}</span>' + "".join(
            f'<a href="./{ev(c)}"' + (' aria-current="page"' if c == cur else "") + f">{s}</a>" for c, s in items)
    return NAV_S + out + "</nav>" + NAV_E


def names(code, g):
    d = D["swimming"]["events"].get(code, {})
    return ", ".join(dict.fromkeys(a["name"] for a in d.get(g, [])))


def std_table():
    rows = ""
    for gl, items in GROUPS:
        rows += f'<tr class="grp"><th scope="rowgroup" colspan="6">{gl}</th></tr>'
        for c, s in items:
            lab = LABEL.get(c, f"{gl} {s}m")
            if c in STD:
                ma, mb, wa, wb = STD[c]
                cells = f'<td class="t">{ma}</td><td class="t b">{mb}</td><td class="t">{wa}</td><td class="t b">{wb}</td>'
            elif c.endswith("50") and gl != "자유형":
                cells = '<td colspan="4" class="note-cell">신설 · 월드컵 2027(3개 대회) 결선 상위 6명 직행 — 기준기록 없음</td>'
            else:
                cells = '<td colspan="4" class="note-cell">' + ("부다페스트 2027 혼성 예선 상위 12팀" if c.startswith("mixed") else "부다페스트 2027 계영 예선 상위 12팀") + " · 개인 출전자로도 구성 가능</td>"
            m, w = names(c, "men"), names(c, "women")
            kor = "<br>".join(x for x in [f'<span class="sx">남</span> {e(m)}' if m else "", f'<span class="sx">여</span> {e(w)}' if w else ""] if x) or '<span class="muted">—</span>'
            rows += f'<tr><th scope="row"><a href="./{ev(c)}">{lab}</a></th>{cells}<td class="kor">{kor}</td></tr>'
    return (f'{STD_S}<section id="events"><h2>세부종목별 기준기록</h2><p>A 기준을 승인 대회(2027.03.01–2028.06.18)에서 달성하면 직행하고, B 기준(A+1.0%)은 정원이 남을 때 초청 대상입니다. '
            '종목 이름을 누르면 그 종목의 한국 주요 선수 문서로 이동합니다.</p>'
            '<div class="table-scroll"><table class="data swm-std"><caption>World Aquatics 규정 H · 개인 종목 기준기록</caption><colgroup><col class="c-ev"><col class="c-t"><col class="c-t"><col class="c-t"><col class="c-t"><col class="c-k"></colgroup>'
            '<thead><tr><th scope="col" rowspan="2">종목</th><th scope="colgroup" colspan="2">남자</th><th scope="colgroup" colspan="2">여자</th><th scope="col" rowspan="2">한국 주요 선수</th></tr>'
            '<tr><th scope="col">A</th><th scope="col">B</th><th scope="col">A</th><th scope="col">B</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>{STD_E}')


def merge_pathway(t):
    """남자·여자 블록이 같은 내용이면 '남녀 공통' 하나로"""
    m = re.search(r'<div class="event men">(.*?)(?=<div class="event women">)', t, re.S)
    w = re.search(r'<div class="event women">(.*?)(?=<div class="event mixed">)', t, re.S)
    if not (m and w):
        return t
    norm = lambda s: re.sub(r"(women|men)", "X", re.sub(r"남자|여자", "X", s))
    if norm(m.group(1)) != norm(w.group(1)):
        return t
    blk = m.group(0)
    blk = blk.replace('<div class="event men"><span class="event-label">남자 · 개인 17 · 계영 3</span><h3>남자 선발 경로</h3>',
                      '<div class="event"><span class="event-label">남녀 공통 · 성별 개인 17 · 계영 3</span><h3>남녀 선발 경로</h3>'
                      '<p class="small">남녀는 같은 경로를 따르며, 기준기록과 계영 순위는 성별로 따로 정합니다.</p>')
    blk = re.sub(r'<p style="margin-top:14px"><a href="\./olswimming-men\.html">남자 상세 안내 →</a></p>',
                 '<p style="margin-top:14px"><a href="./olswimming-men.html">남자 상세 안내 →</a> · <a href="./olswimming-women.html">여자 상세 안내 →</a></p>', blk)
    return t[:m.start()] + blk + t[w.end():]


def year_rows(t):
    i = t.find('<section id="timeline">')
    if i < 0 or 'class="yr"' in t[i:i + 20000]:
        return t
    j = t.index("</section>", i)
    sec = t[i:j]
    last = [None]

    def f(mo):
        y = mo.group(1)[:4]
        add = ""
        if y != last[0]:
            last[0] = y
            add = f'<tr class="yr"><th scope="rowgroup" colspan="2">{y}</th></tr>'
        return add + mo.group(0)
    sec = re.sub(r'<tr><th scope="row">(\d{4}\.[^<]*)</th>', f, sec)
    return t[:i] + sec + t[j:]


CSS = (CSS_S + "\n.swim-sub .sub-label{min-width:0}.swim-sub a{padding:6px 8px}"
       ".swm-std{font-size:14px;table-layout:fixed}.swm-std col.c-ev{width:17%}.swm-std col.c-t{width:10.5%}.swm-std col.c-k{width:41%}.swm-std .sx{display:inline-block;font-size:11px;font-weight:700;color:#54595d;width:16px}.swm-std td.t{font-variant-numeric:tabular-nums;white-space:nowrap;text-align:right}.swm-std td.b{color:#54595d}"
       ".swm-std tr.grp th{background:#eaecf0;text-align:left;font-size:13px;padding:5px 10px}.swm-std td.note-cell{color:#54595d;font-size:13px}"
       ".swm-std td.kor{font-size:13px}.swm-std thead th{text-align:center}.table-scroll{overflow-x:auto}"
       ".data tr.yr th{background:#eaecf0;text-align:left;font-size:13px;padding:5px 10px}"
       ".event .small+table{margin-top:6px}"
       "@media(max-width:600px){.swm-std{font-size:13px;table-layout:auto;min-width:560px}}\n" + CSS_E + "\n")


def patch_css():
    f = SITE + "css/olympic-wiki.css"
    t = open(f, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    blk = CSS.replace("\n", nl)
    if CSS_S in t:
        t = t[:t.index(CSS_S)] + blk + t[t.index(CSS_E) + len(CSS_E) + len(nl):]
    else:
        mark = "/* == athletes"
        i = t.find(mark)
        t = (t[:i] + blk + t[i:]) if i >= 0 else (t + nl + blk)
    open(f, "w", encoding="utf-8", newline="").write(t)


def main():
    patch_css()
    for f in sorted(glob.glob(SITE + P + "*.html")):
        b = os.path.basename(f)
        if "_1" in b:
            continue
        t = open(f, encoding="utf-8", newline="").read(); o = t
        cur = b[len(P) + 4:-5] if b.startswith(P + "-ev-") else None
        if NAV_S in t:
            t = t[:t.index(NAV_S)] + subnav(cur) + t[t.index(NAV_E) + len(NAV_E):]
        else:
            m = re.search(r'<nav class="golf-nav"[^>]*>.*?</nav>', t, re.S)
            if m:
                t = t[:m.end()] + subnav(cur) + t[m.end():]
        if b == P + ".html":
            t = merge_pathway(t)
            if STD_S in t:
                t = t[:t.index(STD_S)] + std_table() + t[t.index(STD_E) + len(STD_E):]
            else:
                i = t.index('<section id="other">')
                t = t[:i] + std_table() + t[i:]
                t = t.replace('<li><a href="#other">', '<li><a href="#events">세부종목별 기준기록</a></li><li><a href="#other">', 1)
            t = year_rows(t)
        if t != o:
            open(f, "w", encoding="utf-8", newline="").write(t)
            print("patched", b)


if __name__ == "__main__":
    main()
