# -*- coding: utf-8 -*-
"""골프 포맷 공통 생성기 (수구·스쿼시 등 배포본과 같은 마크업)."""

INDEX = "https://koreaolympics.github.io/index1.html"


def table(head, rows, caption=None, cls=""):
    cap = f"<caption>{caption}</caption>" if caption else ""
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    body = "".join(
        "<tr>" + f'<th scope="row">{r[0]}</th>' + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
        for r in rows)
    return f'<table class="data {cls}">{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def footnotes(prefix, notes):
    return '<ol class="footnotes">' + "".join(
        f'<li id="{prefix}-note-{i}"><span class="n">[{i}]</span>{t}</li>'
        for i, t in enumerate(notes, 1)) + "</ol>"


def refs(prefix, n):
    return [f'<a href="#{prefix}-note-{i}">[{i}]</a>' for i in range(1, n + 1)]


def rowsfrom(prefix, items):
    r = refs(prefix, len(items))
    return [[a, b, r[i]] for i, (a, b) in enumerate(items)]


def toc(items):
    return ('<nav class="toc" aria-label="이 문서의 목차"><strong>목차</strong><ol>'
            + "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in items) + "</ol></nav>")


def event_block(cls, label, h3, small, head, rows, prefix, notes, link=None, pre=""):
    s = (f'<div class="event {cls}"><span class="event-label">{label}</span><h3>{h3}</h3>'
         f'<p class="small">{small}</p>{pre}' + table(head, rows) + footnotes(prefix, notes))
    if link:
        s += f'<p style="margin-top:14px"><a href="./{link[0]}">{link[1]}</a></p>'
    return s + "</div>"


def quota(head_first, rows, caption):
    cols = ["일반쿼터", "개최국쿼터", "보편성쿼터", "합계"]
    desk = table([head_first] + cols, rows, caption=caption, cls="quota")
    mob = "".join(table(cols, [r[1:]], caption=r[0]) for r in rows)
    return f'<div class="desktop-quota">{desk}</div><div class="mobile-quota">{mob}</div>'


def summary(cards):
    return '<div class="summary-grid">' + "".join(
        f'<div class="summary-card"><strong>{a}</strong><span>{b}</span></div>' for a, b in cards) + "</div>"


def infobox(name, rows, pdf, label):
    dl = "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in rows)
    return (f'<aside class="infobox" aria-label="{name} 요약"><h2>{name} · LA28 예선</h2><dl>{dl}</dl>'
            f'<p class="small"><a href="{pdf}">{label} ↗</a></p></aside>')


def sources_block(items, note):
    return ('<section id="sources"><h2>공식 근거</h2><ol class="sources">'
            + "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in items)
            + f'</ol><p class="note">{note}</p></section>')


def korea_block(date, heading, lead, rows, paras, small, kind="성적"):
    return (f'<section id="korea"><h2>한국 출전 전망</h2><div class="notice"><strong>{date} 기준 참고</strong><br>현재 {kind}을 LA28 규정에 단순 적용한 참고치이며 2028 확정 전망이 아님.</div>\n'
            f'<div class="korea"><h3>{heading}</h3><p>{lead}</p>'
            + table(["선수·팀", "공개 성적", "근거"], rows, caption="근거로 확인한 성적 · 확정 대표 명단이 아님", cls="ranking")
            + "".join(f"<p>{p}</p>\n" for p in paras)
            + f'<p class="small">{small}</p></div></section>')


STD_TOC_MAIN = [("overview", "이벤트 및 출전 쿼터"), ("pathway", "예선 경로"), ("other", "개최국·보편성 쿼터"),
                ("eligibility", "참가 자격"), ("timeline", "예선 및 대회 일정"), ("sources", "공식 근거"), ("korea", "한국 출전 전망")]


def main_body(cards, overview_p, quota_html, note, pathway_intro, blocks, other, elig, tl_intro, timeline, tl_cap, SRC, KOR):
    return ('<section id="overview"><h2>이벤트 및 출전 쿼터</h2>' + summary(cards) + f'<p>{overview_p}</p>' + quota_html
            + f'<p class="note">{note}</p></section>'
            + f'<section id="pathway"><h2>예선 경로</h2><p>{pathway_intro}</p>' + blocks + '</section>'
            + f'<section id="other"><h2>개최국·보편성 쿼터</h2>{other}</section>'
            + f'<section id="eligibility"><h2>참가 자격</h2>{elig}</section>'
            + f'<section id="timeline"><h2>예선 및 대회 일정</h2><p>{tl_intro}</p>' + table(["날짜", "일정"], timeline, caption=tl_cap) + '</section>'
            + SRC + KOR)


class Sport:
    def __init__(self, name, main, tabs, desc, infobox_html, footer_line):
        self.name, self.main, self.tabs = name, main, tabs
        self.desc, self.infobox, self.footer_line = desc, infobox_html, footer_line

    def _tabs(self, cur):
        return "".join(
            f'<a href="./{f}" aria-current="page">{n}</a>' if f == cur else f'<a href="./{f}">{n}</a>'
            for f, n in self.tabs)

    def _crumb(self, cur):
        if cur == self.main:
            return f'<a href="./{self.main}" aria-current="page">{self.name}</a>'
        return f'<a href="./{self.main}">↑ {self.name} 전체 안내</a>'

    def page(self, fname, title, intro, toc_items, body):
        return (
            '<!doctype html>\n'
            '<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="description" content="{self.desc}"><title>{title} | {self.name} · 올림픽예선</title>'
            '<link rel="stylesheet" href="./css/olympic-wiki.css"></head><body>'
            '<a class="skip" href="#main">본문 바로가기</a><header class="topbar"><div class="topbar-inner">'
            f'<a href="{INDEX}">← 올림픽예선 목차</a>'
            f'<nav class="sport-nav" aria-label="상위 문서">{self._crumb(fname)}</nav>'
            '<span>LA28 · 종목별 예선</span></div></header><div class="shell">'
            f'<h1 class="title">{title}</h1><p class="intro">{intro}</p>'
            f'<nav class="golf-nav" aria-label="{self.name} 문서">{self._tabs(fname)}</nav>'
            f'<div class="columns"><main id="main">{toc(toc_items)}{body}</main>{self.infobox}</div>'
            f'<footer class="footer"><nav class="footer-nav" aria-label="하단 {self.name} 문서">'
            f'<a href="{INDEX}">← 올림픽예선 목차</a>{self._tabs(fname)}</nav>'
            f'<p>{self.name} · 올림픽예선 | {self.footer_line}</p>'
            '<a href="#main">본문 위로 ↑</a></footer></div></body></html>'
        )

    def sub(self, f, title, intro, sections, SRC, KOR):
        body = "".join(f'<section id="{i}"><h2>{h}</h2>{c}</section>' for i, h, c in sections) + SRC + KOR
        t = [(i, h) for i, h, _ in sections] + [("sources", "공식 근거"), ("korea", "한국 출전 전망")]
        return f, self.page(f, title, intro, t, body)


def write(pages):
    for fn, html in pages:
        with open(fn, "w", encoding="utf-8", newline="") as fh:
            fh.write(html.replace("\n", "\r\n"))
        print("wrote", fn, len(html.encode()))
