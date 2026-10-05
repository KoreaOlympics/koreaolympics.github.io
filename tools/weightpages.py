# -*- coding: utf-8 -*-
"""체급 종목 규정 문서에 체급별 링크 + 좌석 그림 + 체급별 규정 표 삽입 (멱등).
대상: 유도·태권도·역도·레슬링·복싱. athletes.py 실행 뒤에 실행한다."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weightrules as WR
from athletes import D, EV, e

SITE = "/root/site/"
MS, ME = "<!-- wclass:start -->", "<!-- wclass:end -->"

POOL_TXT = {
    "judo": "체급마다 IJF 랭킹 직행 17명 + 개최국 1명이 고정이고, 대륙 쿼터(성별 52명)·혼성 단체 초청(6명)·보편성(10명)은 체급과 무관한 공용 풀이라 체급별 최종 인원은 예선이 끝나야 정해집니다.",
    "taekwondo": "체급마다 올림픽 랭킹 5 + 그랜드슬램 1 + 대륙 예선 9 + 개최국 또는 보편성 1 = 16명입니다.",
    "weightlifting": "체급마다 OQR 랭킹 8 + 대륙 대표 1 + 개최국 또는 보편성 1 = 10명입니다.",
    "wrestling": "체급마다 2027 세계선수권 메달 4 + UWW 랭킹 3 + 대륙 예선 8 + 세계 예선 1 = 16명입니다. 개최국 자리는 없습니다.",
    "boxingw": "체급마다 정원(16·18·20명)과 대회별 배정이 다릅니다. 앞 4개 체급에만 개최국·보편성 자리가 있습니다.",
}
# 규정 문서 → (종목 키, 그룹 이름, 삽입 방식)
GENDER_PAGES = {
    "oljudo-men.html": ("judo", "남자", "cats"), "oljudo-women.html": ("judo", "여자", "cats"),
    "oltaekwondo-men.html": ("taekwondo", "남자", "cats"), "oltaekwondo-women.html": ("taekwondo", "여자", "cats"),
    "olweightlifting-men.html": ("weightlifting", "남자", "cats"), "olweightlifting-women.html": ("weightlifting", "여자", "cats"),
    "olwrestling-freestyle.html": ("wrestling", "남자 자유형", "cats"), "olwrestling-greco.html": ("wrestling", "그레코로만형", "cats"),
    "olwrestling-women.html": ("wrestling", "여자 자유형", "cats"),
    "olboxing-men.html": ("boxingw", "남자", "after:matrix"), "olboxing-women.html": ("boxingw", "여자", "after:matrix"),
}
MAIN_PAGES = {"oljudo.html": "judo", "oltaekwondo.html": "taekwondo", "olweightlifting.html": "weightlifting", "olwrestling.html": "wrestling", "olboxing.html": "boxingw"}


def korean(key, code):
    return ", ".join(a["name"] for a in D[key]["events"].get(code, {}).get("athletes", []))


def class_block(key, code, label):
    prefix = EV[key][0]
    body = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td></tr>' for a, b, c, _ in WR.rows(key, code))
    k = korean(key, code)
    return (f'<div class="wclass" id="w-{code}"><h3><a href="./{prefix}-ev-{code}.html">{label}</a></h3>'
            + WR.figure(key, code, label, small=True)
            + f'<table class="data wrule"><thead><tr><th scope="col">경로</th><th scope="col">인원</th><th scope="col">선발 방식</th></tr></thead><tbody>{body}</tbody>'
            f'<tfoot><tr><th scope="row">체급 합계</th><td>{WR.total(key, code)}</td><td></td></tr></tfoot></table>'
            f'<p class="kor">한국 주요 선수: {e(k) if k else "<span class=muted>추후 작성</span>"} · <a href="./{prefix}-ev-{code}.html">{label} 문서 →</a></p></div>')


def cats_section(key, group):
    items = dict(EV[key][2])[group]
    nav = " · ".join(f'<a href="#w-{c}">{l.rsplit(" ", 1)[1]}</a>' for c, l in items)
    return (MS + f'<section id="cats"><h2>체급별 예선 규정</h2><p>{POOL_TXT[key]} 체급 이름을 누르면 그 체급의 규정과 한국 주요 선수를 모은 문서로 이동합니다.</p>'
            f'<p class="small">바로가기: {nav}</p>' + "".join(class_block(key, c, l) for c, l in items) + "</section>" + ME)


def index_section(key):
    prefix, name, groups = EV[key]
    rows = ""
    for gl, items in groups:
        for c, l in items:
            if key == "judo" and c == "xteam":
                fixed = "개인전 출전 선수로 구성 · 초청 6명"
            else:
                fixed = " + ".join(f"{lab} {n}" + (f"–{n + x}" if x else "") for lab, n, x, kind in WR.segs(key, c) if kind != "pool" and (n or x))
                if key == "judo":
                    fixed += " + 공용 풀"
                fixed += f" = {WR.total(key, c)}" if key != "judo" else ""
            k = korean(key, c)
            rows += f'<tr><th scope="row"><a href="./{prefix}-ev-{c}.html">{l}</a></th><td>{fixed}</td><td>{e(k) if k else "<span class=muted>—</span>"}</td></tr>'
    return (f'{MS}<section id="classes"><h2>체급별 예선 규정</h2><p>{POOL_TXT[key]} 체급을 누르면 그 체급의 좌석 그림·규정 표와 한국 주요 선수 문서로 이동합니다.</p>'
            f'<table class="data"><thead><tr><th scope="col">체급</th><th scope="col">배정</th><th scope="col">한국 주요 선수</th></tr></thead><tbody>{rows}</tbody></table></section>{ME}')


def replace_block(t, new, fallback):
    if MS in t:
        return t[:t.index(MS)] + new + t[t.index(ME) + len(ME):]
    return fallback(t, new)


def patch(f, fn):
    p = SITE + f
    t = open(p, encoding="utf-8", newline="").read()
    t2 = fn(t)
    if t2 != t:
        open(p, "w", encoding="utf-8", newline="").write(t2)
        print("patched", f)


def gender_fn(key, group, mode):
    def fb(t, new):
        if mode == "cats":
            return re.sub(r'<section id="cats">.*?</section>', lambda m: new, t, count=1, flags=re.S)
        sec = mode.split(":")[1]
        i = t.index(f'<section id="{sec}">'); j = t.index("</section>", i) + len("</section>")
        t = t[:j] + new + t[j:]
        return t.replace(f'<li><a href="#{sec}">', '<li><a href="#cats">체급별 예선 규정</a></li><li><a href="#' + sec + '">', 1) if '#cats"' not in t else t

    def fn(t):
        t = replace_block(t, cats_section(key, group), fb)
        t = t.replace('<li><a href="#cats">체급</a></li>', '<li><a href="#cats">체급별 예선 규정</a></li>')
        return t
    return fn


def main_fn(key):
    def fb(t, new):
        i = t.index('<section id="other">')
        t = t[:i] + new + t[i:]
        return t.replace('<li><a href="#other">', '<li><a href="#classes">체급별 예선 규정</a></li><li><a href="#other">', 1)
    return lambda t: replace_block(t, index_section(key), fb)


def mixed_page(t):
    link = '<p class="small"><a href="./oljudo-ev-xteam.html">혼성 단체 한국 선수·규정 문서 →</a></p>'
    if link in t:
        return t
    i = t.index('<section id="cats">'); j = t.index("</section>", i)
    return t[:j] + link + t[j:]


if __name__ == "__main__":
    for f, (key, group, mode) in GENDER_PAGES.items():
        patch(f, gender_fn(key, group, mode))
    for f, key in MAIN_PAGES.items():
        patch(f, main_fn(key))
    patch("oljudo-mixed.html", mixed_page)
