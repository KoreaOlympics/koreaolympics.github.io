# -*- coding: utf-8 -*-
"""14종목 공통 상수·헬퍼."""
from olgen import (Sport, table, footnotes, refs, rowsfrom, event_block, quota, summary, infobox,
                   sources_block, korea_block, main_body, STD_TOC_MAIN, write)

B = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/"
HEAD = ["경로", "쿼터", "선발 방식"]
FOOT = "규정 확인 2026.10.04 · 한국 전망 기준 2026.10.04"
STD = "올림픽 헌장(제41조 국적, 제43조 세계반도핑규약 및 경기 조작 방지 규정), 여성 카테고리 보호에 관한 IOC 정책, IOC 참가 조건"
UNIV_TXT = "IOC 초청 2027.10.01, 신청 마감 2028.01.15"
MEDALS = "https://www.olympics.com/ko/news/korea-complete-list-winners-medallists-asian-games-2026"
MEDALS_T = "Olympics.com · 아시안게임 한국 메달리스트 (2026.10.04)"


def note(ver, pages, fed, extra=""):
    return (f"규정 확인일: 2026.10.04. IOC가 게시한 {fed} 원문 PDF({pages}쪽, Version as of {ver})를 기준으로 정리했다. "
            + extra + f"본 문서는 비공식 한국어 요약이며 최종 적용은 {fed} 공지를 따른다.")


def a(url, text):
    return f'<a href="{url}">{text}</a>'


def ul(items):
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"
