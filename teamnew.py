# -*- coding: utf-8 -*-
"""수구·야구소프트볼·크리켓·라크로스를 구기종목 신규 레이아웃(탭·Road SVG·asia-focus)으로 생성."""
import re, sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/d605e20f-a928-5cf2-a6a8-5bb76056abad/scratchpad")
from teamsvg import (T, R, A, DOT, fig, esc, sportnav,
                     DARK, BLUE, LBLUE, TEAL, LTEAL, ORG, LORG, LINE, INK, MUTE, FONT)

OUT = "/root/site/"
TPL = open(OUT + "olhockey.html", encoding="utf-8").read()
HEAD_CSS = TPL[TPL.index("<style>"):TPL.index("</head>")]
SCRIPT = TPL[TPL.index("<script>(()=>"):TPL.index("</body>")]
EDIT = "2026년 10월 5일"
STROKE = 'fill="none" stroke="#6b8582" stroke-width="1.7"'

# ------------------------------------------------------------------ 종목 아이콘 (200×134 영역)
ICONS = {
    "pool": (f'<rect x="5" y="7" width="190" height="120" rx="2" fill="#e3eef5" stroke="#6b8582" stroke-width="1.7"/>'
             f'<path d="M5 37H195M5 67H195M5 97H195" {STROKE} stroke-dasharray="6 5"/>'
             f'<path d="M5 50H14V84H5M195 50H186V84H195" {STROKE}/><circle cx="100" cy="67" r="6" fill="#b9734f"/>'
             f'<path d="M30 7V127M170 7V127" fill="none" stroke="#b9734f" stroke-width="1.2"/>'),
    "diamond": (f'<rect x="5" y="7" width="190" height="120" rx="2" fill="#e6efed" stroke="#6b8582" stroke-width="1.7"/>'
                f'<path d="M100 117L55 72L100 27L145 72Z" fill="#f2e6d9" stroke="#6b8582" stroke-width="1.7"/>'
                f'<path d="M100 117L20 37M100 117L180 37" {STROKE}/><circle cx="100" cy="76" r="5" fill="#b9734f"/>'
                f'<path d="M96 113H104V121H96Z" fill="#fff" stroke="#405553"/>'),
    "oval": (f'<ellipse cx="100" cy="67" rx="95" ry="60" fill="#e6efed" stroke="#6b8582" stroke-width="1.7"/>'
             f'<ellipse cx="100" cy="67" rx="55" ry="34" {STROKE} stroke-dasharray="5 4"/>'
             f'<rect x="92" y="45" width="16" height="44" fill="#f2e6d9" stroke="#6b8582" stroke-width="1.2"/>'
             f'<path d="M95 48H105M95 86H105" stroke="#405553" stroke-width="2"/>'),
    "field": (f'<rect x="5" y="7" width="190" height="120" rx="2" fill="#e6efed" stroke="#6b8582" stroke-width="1.7"/>'
              f'<path d="M100 7V127" {STROKE}/><circle cx="40" cy="67" r="15" {STROKE}/><circle cx="160" cy="67" r="15" {STROKE}/>'
              f'<path d="M36 61H44V73H36ZM156 61H164V73H156Z" fill="#b9734f"/><circle cx="100" cy="67" r="4" fill="#fff" stroke="#405553"/>'),
}


def road(g, label, icon, rows, total, title):
    """rows: [(경로, 수)] → 데스크톱/모바일 SVG 쌍 (초안 디자인과 동일한 형식)"""
    k = len(rows)
    H = max(300, 54 + 48 * k + 50)
    top = (H - 48 * k) / 2 - 2
    b = f'<g transform="translate(12 {H / 2 - 82:.1f})">{ICONS[icon]}</g>'
    b += f'<g {FONT} fill="#202122"><text x="112" y="{H / 2 + 77:.1f}" text-anchor="middle" font-size="18" font-weight="600">{esc(label)}</text>'
    mids = []
    for i, (name, n) in enumerate(rows):
        y = top + i * 48
        mids.append(y + 19)
        b += (f'<rect x="242" y="{y:.1f}" width="374" height="38" rx="3" fill="#fff" stroke="#bdc8d4"/>'
              f'<text x="257" y="{y + 25:.1f}" font-size="16">{esc(name)}</text>'
              f'<rect x="557" y="{y:.1f}" width="59" height="38" rx="3" fill="#eaf0fa"/>'
              f'<text x="586" y="{y + 26:.1f}" text-anchor="middle" fill="#2454a6" font-size="21" font-weight="600">{n}</text>'
              f'<path d="M616 {y + 19:.1f}H651" fill="none" stroke="#99a9bb" stroke-width="1.5"/>')
    c = H / 2
    b += (f'<path d="M651 {mids[0]:.1f}V{mids[-1]:.1f}M651 {c:.1f}H684" fill="none" stroke="#99a9bb" stroke-width="1.5"/>'
          f'<path d="M678 {c - 4:.1f}L685 {c:.1f}L678 {c + 4:.1f}" fill="none" stroke="#99a9bb" stroke-width="1.5"/>'
          f'<rect x="690" y="{c - 64:.1f}" width="175" height="128" rx="3" fill="#233e50"/>'
          f'<text x="777" y="{c - 32:.1f}" text-anchor="middle" fill="#d9e5ec" font-size="16">LOS ANGELES</text>'
          f'<text x="777" y="{c + 7:.1f}" text-anchor="middle" fill="#fff" font-size="38" font-weight="600">{total}</text>'
          f'<text x="777" y="{c + 40:.1f}" text-anchor="middle" fill="#d9e5ec" font-size="18">2028</text></g>')
    desc = "각 경로별 선발 팀 수. " + ", ".join(f"{a} {n}팀" for a, n in rows) + f". 합계 {total}."
    d = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 {H}" role="img" aria-labelledby="{g}-svg-title {g}-svg-desc">'
         f'<title id="{g}-svg-title">{esc(title)}</title><desc id="{g}-svg-desc">{esc(desc)}</desc>{b}</svg>')
    mh = 77 + 40 * k + 50
    m = f'<g transform="translate(4 0) scale(.48)">{ICONS[icon]}</g><g {FONT} fill="#202122"><text x="120" y="36" font-size="18" font-weight="600">{esc(label)}</text>'
    for i, (name, n) in enumerate(rows):
        y = 77 + i * 40
        m += (f'<rect x="1" y="{y}" width="328" height="33" rx="2" fill="#fff" stroke="#bdc8d4"/>'
              f'<text x="11" y="{y + 22}" font-size="14">{esc(name)}</text>'
              f'<text x="313" y="{y + 23}" text-anchor="end" font-size="18" fill="#2454a6" font-weight="600">{n}</text>')
    y = 77 + 40 * k + 8
    m += (f'<rect x="1" y="{y}" width="328" height="39" rx="2" fill="#233e50"/>'
          f'<text x="165" y="{y + 26}" fill="#fff" text-anchor="middle" font-size="20">LA28 · {total}</text></g>')
    mob = (f'<svg class="mobile-diagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 {mh}" role="img" '
           f'aria-label="{esc(label)} 출전권 배정">{m}</svg>')
    return d + mob


# ------------------------------------------------------------------ 설명 그림
def wp_cascade(g):
    n = "남자" if g == "men" else "여자"
    ev = [("월드컵 2027", "2027.02.24–28", 1), ("세계선수권 부다페스트", "2027.06.26–07.09", 2),
          ("5개 대륙선수권", "2027.07–2028.01", 5), ("월드퀄리파이어 2028", "2028.04 · 2개 대회", 3)]
    b = T(20, 26, "예선 순서 — 앞에서 확보한 팀은 뒤 대회 자리를 차지하지 않음", 15, MUTE)
    for i, (a, d, q) in enumerate(ev):
        x = 20 + i * 178
        b += R(x, 44, 160, 92, LORG if i == 2 else "#fff", ORG if i == 2 else BLUE)
        b += T(x + 80, 72, a, 15, INK, "middle", "600") + T(x + 80, 94, d, 13, MUTE, "middle")
        for k in range(q):
            b += DOT(x + 80 - (q - 1) * 9 + k * 18, 118, 6, ORG if i == 2 else DARK)
        if i < 3:
            b += A(x + 162, 90, x + 176, 90)
    b += A(100, 140, 100, 178, ORG) + T(112, 166, "상위 팀이 이미 확보 → 다음 순위로", 13, ORG)
    b += R(20, 186, 694, 52, LBLUE, BLUE)
    b += T(367, 210, "개최국 미국 1 + 1 + 2 + 5 + 3 = 12팀", 17, INK, "middle", "600")
    b += T(367, 230, "미사용 출전권은 부다페스트 2027 최종 순위의 다음 미확보 팀에게", 13, MUTE, "middle")
    return fig(f"wp-c-{g}", 734, 252, f"수구 {n} 예선 대회 순서", "월드컵 1팀, 세계선수권 2팀, 대륙선수권 5팀, 월드퀄리파이어 3팀이 순서대로 정해지며 개최국 1팀을 더해 12팀이다.",
               b, f"<b>예선 순서 ({n})</b> · 네 단계가 시간 순으로 이어지고, 앞 단계에서 확보한 국가는 건너뛰어 다음 순위가 받습니다(World Aquatics 규정 D.1). 재배정 기준표는 부다페스트 2027 순위입니다(F.1).")


def wp_asia(g):
    if g == "men":
        teams = ["일본", "중국", "카자흐스탄", "이란", "한국"]
        cap = ("<b>아시아 1자리의 의미</b> · 2025 아시아선수권 순위(참고)로 보면 한국은 5위입니다. 일본·중국이 세계선수권 등으로 먼저 확보해도 자리는 카자흐스탄·이란 순으로 내려가므로, "
               "한국은 대륙선수권 우승권에 들거나 월드퀄리파이어 2028(참가 자격은 World Aquatics 대회 규정)에 나가야 합니다.")
    else:
        teams = ["중국", "일본", "카자흐스탄", "—", "—"]
        cap = ("<b>아시아 1자리의 의미</b> · 2025 아시아선수권 여자는 중국·일본·카자흐스탄 순이었고 한국은 출전하지 않았습니다. 2026 아시안게임에도 불참해, "
               "2027–28 아시아 대륙선수권 참가가 첫 관문입니다.")
    b = T(20, 26, "2025 아시아선수권 순위 (참고 · LA28 예선 대회 아님)", 15, MUTE)
    for i, tname in enumerate(teams):
        x = 20 + i * 112
        kor = tname == "한국"
        b += R(x, 44, 100, 48, LORG if kor else ("#fff" if i else LBLUE), ORG if kor else (LINE if i else BLUE))
        b += T(x + 50, 64, f"{i + 1}위", 13, MUTE, "middle") + T(x + 50, 84, tname, 15, INK, "middle", "600" if kor or i == 0 else "400")
    b += R(600, 44, 120, 48, DARK, DARK) + T(660, 74, "LA28 1자리", 15, "#fff", "middle", "600")
    b += f'<path d="M70 96V112H660V96" fill="none" stroke="{BLUE}" stroke-width="1.6"/>' + A(660, 112, 660, 96, BLUE)
    b += T(360, 132, "대륙선수권 최상위 1팀 · 이미 확보 시 다음 순위", 14, BLUE, "middle")
    if g != "men":
        b += T(570, 160, "한국 여자: 2025·2026 아시아 대회 불참", 13, ORG, "end", "600")
    return fig(f"wp-a-{g}", 740, 172, "수구 아시아 대륙 출전권", "아시아 대륙선수권 최상위 1팀이 출전권을 얻는다. 참고 순위와 한국 위치.", b, cap)


def bb_premier():
    b = T(20, 26, "WBSC 프리미어12 2027 (2027.11)", 15, MUTE) + T(560, 26, "LA28", 15, MUTE)
    b += R(20, 40, 250, 70, LBLUE, BLUE) + T(145, 68, "아시아 참가국 중 최상위", 15, INK, "middle", "600") + T(145, 92, "일본·대만·한국 …", 14, MUTE, "middle")
    b += R(20, 124, 250, 70, "#fff", LINE) + T(145, 152, "유럽·오세아니아 중 최상위", 15, INK, "middle", "600") + T(145, 176, "네덜란드·호주 등", 14, MUTE, "middle")
    b += A(272, 75, 552, 75) + A(272, 159, 552, 159)
    b += R(558, 56, 150, 38, DARK, DARK) + T(633, 81, "아시아 1팀", 15, "#fff", "middle") + R(558, 140, 150, 38, DARK, DARK) + T(633, 165, "유럽·오세아니아 1팀", 14, "#fff", "middle")
    b += T(410, 64, "직행", 13, MUTE, "middle")
    b += R(300, 100, 230, 36, LORG, ORG, 3) + T(415, 123, "못 들면 → 최종 예선 경로", 14, ORG, "middle", "600")
    return fig("bb-p", 728, 210, "야구 프리미어12 출전권", "프리미어12 2027에서 아시아 최상위 1팀과 유럽·오세아니아 최상위 1팀이 LA28 출전권을 얻는다.", b,
               "<b>프리미어12 2027</b> · 아메리카 2자리는 WBC 2026으로 이미 정해졌으므로(베네수엘라·도미니카공화국), 프리미어12에서는 아시아와 유럽·오세아니아 각 최상위 1팀만 나옵니다(WBSC 규정 D.3). 한국은 아시아 참가국 중 1위를 해야 직행합니다.")


def bb_fqe():
    comp = [("아시아선수권", "미확보 상위 2", 2, True), ("유럽선수권", "2", 2, False), ("아프리카선수권", "1", 1, False), ("오세아니아 예선", "1", 1, False)]
    b = T(20, 26, "야구 최종 예선 (2028.03까지) · 6팀", 15, MUTE)
    y = 40
    for name, lab, q, asia in comp:
        b += R(20, y, 210, 40, LORG if asia else "#fff", ORG if asia else LINE) + T(34, y + 26, name, 15, INK, weight="600" if asia else "400")
        for k in range(q):
            b += DOT(256 + k * 22, y + 20, 8, ORG if asia else BLUE)
        b += A(300, y + 20, 360, 118)
        y += 48
    b += R(366, 82, 170, 72, LBLUE, BLUE) + T(451, 112, "최종 예선", 16, INK, "middle", "600") + T(451, 136, "6팀 중 우승 1팀", 14, MUTE, "middle")
    b += A(538, 118, 584, 118) + R(590, 99, 120, 38, DARK, DARK) + T(650, 124, "LA28 1자리", 15, "#fff", "middle", "600")
    b += T(20, 248, "아시아 2자리는 '최근' 아시아선수권 기준 — 2027 대회가 열리면 그 결과를 사용", 13, ORG)
    return fig("bb-f", 728, 262, "야구 최종 예선 구성", "아시아선수권 미확보 상위 2, 유럽선수권 2, 아프리카선수권 1, 오세아니아 예선 1, 모두 6팀이 최종 예선을 치러 우승 1팀이 출전한다.", b,
               "<b>최종 예선 구성</b> · 6팀 중 우승팀 1팀만 LA28에 나갑니다(WBSC 규정 D.4). 2025 BFA 아시아선수권 기준 한국은 3위(일본·대만 다음)라, 일본·대만 중 한 팀이 프리미어12로 확보해야 한국에 최종 예선 자리가 옵니다.")


def sb_flow():
    conts = [("아메리카", "캐나다 서리"), ("아시아/오세아니아", "한국 경로"), ("유럽/아프리카", "")]
    b = T(20, 26, "2027 소프트볼 대륙 예선", 15, MUTE) + T(600, 26, "LA28", 15, MUTE)
    for i, (c, sub) in enumerate(conts):
        y = 44 + i * 70
        asia = i == 1
        b += R(20, y, 200, 56, LORG if asia else "#fff", ORG if asia else LINE)
        b += T(34, y + 25, c, 15, INK, weight="600") + T(34, y + 45, sub, 13, ORG if asia else MUTE)
        b += T(240, y + 21, "1위", 13, INK) + DOT(270, y + 17, 7, DARK) + A(282, y + 17, 592, 64 + i * 34)
        b += T(240, y + 46, "2·3위", 13, INK) + DOT(284, y + 42, 7, BLUE) + DOT(302, y + 42, 7, BLUE) + A(314, y + 42, 380, 232)
    b += R(598, 44, 120, 108, DARK, DARK) + T(658, 92, "대륙 1위", 15, "#fff", "middle", "600") + T(658, 114, "3팀 직행", 14, "#d9e5ec", "middle")
    b += R(386, 212, 180, 50, LBLUE, BLUE) + T(476, 234, "최종 예선 6팀", 15, INK, "middle", "600") + T(476, 253, "~2028.03 · 우승 1팀", 13, MUTE, "middle")
    b += A(568, 237, 592, 237) + R(598, 220, 120, 34, DARK, DARK) + T(658, 242, "최종 예선 1", 14, "#fff", "middle")
    b += T(718, 284, "+ 월드컵 파이널 1 · 개최국 미국 1 = 6팀", 13, MUTE, "end")
    return fig("sb-f", 736, 296, "소프트볼 예선 흐름", "3개 대륙 예선 1위가 직행하고 2·3위 6팀이 최종 예선에서 1자리를 다툰다. 월드컵 파이널 1팀과 개최국 1팀을 더해 6팀.", b,
               "<b>소프트볼 예선 흐름</b> · 대륙 예선 1위 3팀 직행, 2·3위 6팀이 최종 예선(WBSC 규정 D.7·D.8). 월드컵 파이널 1위(D.6)가 대륙 예선 전에 확보하면 해당 대륙 예선에서는 다음 순위가 올라갑니다. 한국은 아시아/오세아니아에서 일본·호주 등과 3위 안을 다퉈야 합니다.")


def cr_rank(g):
    n = "남자" if g == "men" else "여자"
    src = "ICC 남자 T20I 랭킹 (2026.12.31)" if g == "men" else "여자 T20 월드컵 2026 최종 순위"
    conts = ["아시아", "유럽", "오세아니아", "아프리카", "아메리카"]
    pick = {"아시아": "인도", "유럽": "영국", "오세아니아": "호주", "아프리카": "남아공"} if g == "women" else {}
    b = T(20, 26, src + " → 대륙별 최상위 4팀", 15, MUTE)
    for i, c in enumerate(conts):
        x = 20 + i * 140
        amer = c == "아메리카"
        has = c in pick
        b += R(x, 44, 128, 70, LTEAL if has else ("#f4f5f7" if amer else "#fff"), TEAL if has else LINE)
        b += T(x + 64, 70, c, 15, INK, "middle", "600") + T(x + 64, 96, pick.get(c, "개최국 미국 별도" if amer else "랭킹순 첫 팀"), 13, TEAL if has else MUTE, "middle")
    b += T(20, 140, "같은 대륙의 두 번째 팀은 건너뜀 · 서로 다른 4개 대륙 · 서인도제도는 NOC가 아니어서 제외", 13, ORG)
    b += R(20, 156, 330, 52, LBLUE, BLUE) + T(185, 180, "최종 글로벌 예선 (FOGQT)", 15, INK, "middle", "600")
    b += T(185, 199, ("다음 8개국 · " + ("2026.12.31 랭킹" if g == "men" else "2027.03.01 랭킹")), 13, MUTE, "middle")
    b += A(352, 182, 420, 182) + R(426, 163, 120, 38, DARK, DARK) + T(486, 188, "1자리", 15, "#fff", "middle", "600")
    b += T(566, 188, "대륙 제한 없음", 13, MUTE)
    cap = ("<b>대륙별 최상위 4팀</b> · 여자는 2026 T20 월드컵으로 호주·영국·인도·남아공이 확정되었습니다(ICC 2026.06.29). 아시아 자리는 인도가 차지했습니다."
           if g == "women" else
           "<b>대륙별 최상위 4팀</b> · 2026.12.31 랭킹 마감 시점에 순위표를 위에서부터 내려가며 대륙마다 첫 팀을 고릅니다(ICC 규정 D.1). 아시아 자리는 인도가 유력해 한국의 경로는 최종 글로벌 예선뿐입니다.")
    return fig(f"cr-r-{g}", 720, 222, f"크리켓 {n} 출전권 선발 구조", "대륙별 최상위 4팀과 최종 글로벌 예선 1팀, 개최국 1팀.", b, cap)


def lac_funnel(g):
    n = "남자" if g == "men" else "여자"
    conts = [("아프리카", 1), ("아시아태평양", 5), ("유럽", 5), ("팬암", 5)]
    b = T(20, 26, "2026 대륙 예선 (쿼터 없음)", 15, MUTE) + T(270, 26, "2027 식스 세계선수권 · 16팀", 15, MUTE) + T(590, 26, "LA28", 15, MUTE)
    for i, (c, q) in enumerate(conts):
        y = 40 + i * 50
        asia = c == "아시아태평양"
        b += R(20, y, 168, 40, LORG if asia else "#fff", ORG if asia else LINE) + T(32, y + 26, c, 15, INK, weight="600" if asia else "400")
        b += T(176, y + 26, str(q), 16, ORG if asia else BLUE, "end", "600") + A(190, y + 20, 262, 120)
    b += R(268, 40, 250, 190, LBLUE, BLUE)
    b += T(393, 70, "16팀 최종 순위", 16, INK, "middle", "600")
    for k in range(16):
        b += DOT(296 + (k % 8) * 28, 94 + (k // 8) * 26, 7, DARK if k < 4 else (BLUE if k < 10 else "#c8ccd1"))
    b += T(393, 160, "● 미국 제외 상위 4팀 → 직행", 13, INK, "middle") + T(393, 180, "대륙별 최소 1 · 최대 3 · 12위 이내", 13, MUTE, "middle")
    b += T(393, 204, "● 다음 6팀 → 최종 예선", 13, BLUE, "middle")
    b += A(520, 92, 580, 92) + R(586, 66, 130, 50, DARK, DARK) + T(651, 89, "세계선수권 4", 15, "#fff", "middle", "600") + T(651, 108, "+ 개최국 미국 1", 12, "#d9e5ec", "middle")
    b += A(520, 196, 580, 196) + R(586, 172, 130, 50, LBLUE, BLUE) + T(651, 194, "최종 예선 6팀", 14, INK, "middle", "600") + T(651, 212, "2028.03–04", 12, MUTE, "middle")
    b += A(651, 224, 651, 246) + R(586, 248, 130, 34, DARK, DARK) + T(651, 270, "우승 1팀", 14, "#fff", "middle", "600")
    b += T(20, 270, "한국: 아시아태평양 예선(호주 선샤인코스트 2026.10.05–10)에서 5위 안", 13, ORG, weight="600")
    return fig(f"lac-f-{g}", 730, 292, f"라크로스 {n} 예선 흐름", "대륙 예선으로 16팀을 정해 2027 식스 세계선수권을 치르고 상위 4팀이 직행, 다음 6팀이 최종 예선에서 1팀을 가린다. 개최국 1팀 포함 6팀.", b,
               f"<b>예선 흐름 ({n})</b> · 대륙 예선에는 올림픽 쿼터가 없고 세계선수권 출전권만 걸려 있습니다(World Lacrosse 규정 D.2). 세계선수권 상위 4팀은 대륙별 최소 1팀(미국이 쓰면 아프리카·아시아태평양·유럽만), 대륙당 최대 3팀, 12위 이내 조건을 따릅니다(D.3).")


# ------------------------------------------------------------------ 페이지 조립
def table(caption, rows):
    head = "<thead><tr><th scope=\"col\">선발 경로</th><th scope=\"col\">대회·시기</th><th scope=\"col\">본선 배정</th><th scope=\"col\">선발 기준</th></tr></thead>"
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table><caption>{caption}</caption>{head}<tbody>{body}</tbody></table></div>'


def steps(items):
    return '<div class="steps">' + "".join(f'<div class="step"><span>경로 0{i + 1}</span><strong>{a}</strong><p>{b}</p></div>' for i, (a, b) in enumerate(items)) + "</div>"


def panel(s, p, first):
    g = p["id"]
    L = s["labels"]
    links = "".join(f'<a href="#{g}-{k}">{L[k][1]}</a>' for k in ["summary", "asia", "oqt", "others"])
    return (f'<section id="panel-{g}" role="tabpanel" aria-labelledby="tab-{g}" {"" if first else "hidden"}>\n'
            f' <h2 class="panel-title">{p["title"]}</h2>\n'
            f' <nav class="section-links" aria-label="{p["title"]} 목차">{links}</nav>\n'
            f' <figure class="road"><figcaption><strong>Road to LA28</strong><span>{p["title"]} · 기본 배정 · 단위: 팀</span></figcaption>'
            f'<div class="diagram-scroll">{road(g, p["title"], s["icon"], p["road"], p["total"], s["sport"] + " " + p["title"] + " 본선 배정")}</div>'
            f'<p class="legend">각 줄은 별도의 출전권 배정 경로입니다. 중복 자격과 재배정 조건은 아래 설명을 따릅니다.</p></figure>\n'
            f' <h2 id="{g}-summary">{L["summary"][0]}</h2>{table(p["title"] + " 본선 출전권", p["rows"])}\n'
            f' <p class="note">{p["note"]}</p><p class="snapshot">{p["snapshot"]}</p>\n'
            f' <div class="asia-focus"><h2 id="{g}-asia">{L["asia"][0]}</h2><p>{p["asia"]}</p>{steps(p["steps"])}{p.get("asia_more", "")}</div>\n'
            f' <h2 id="{g}-oqt">{L["oqt"][0]}</h2>{p["oqt"]}<p class="refline">근거: <a href="#references">{s["refline"]}</a></p>\n'
            f' <h2 id="{g}-others">{L["others"][0]}</h2>{p["others"]}</section>')


def build(s):
    P = s["panels"]
    first = P[0]["id"]
    toc = ('<aside class="toc" aria-label="문서 목차"><h2>목차</h2><a href="#main">개요</a>'
           + "".join(f'<a data-section="{k}" href="#{first}-{k}">{s["labels"][k][1]}</a>' for k in ["summary", "asia", "oqt", "others"])
           + f'<a href="#eligibility">참가 자격</a><a href="#references">출처·자료 기준</a><p class="small">편집 기준<br>{EDIT}</p></aside>')
    facts = '<div class="facts">' + "".join(f"<div><strong>{a}</strong><span>{b}</span></div>" for a, b in s["facts"]) + "</div>"
    tabs = ('<div class="tabs" role="tablist" aria-label="성별·세부종목">'
            + "".join(f'<button id="tab-{p["id"]}" role="tab" aria-controls="panel-{p["id"]}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}" data-tab="{p["id"]}">{p["title"]}</button>'
                      for i, p in enumerate(P)) + "</div>")
    panels = "".join(panel(s, p, i == 0) for i, p in enumerate(P))
    refs = '<ol class="source-list">' + "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in s["refs"]) + "</ol>"
    old = " · ".join(f'<a href="{a}.html">{a}.html</a>' for a in s["aliases"])
    page = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>2028 로스앤젤레스 올림픽 {s["sport"]} 예선</title><meta name="description" content="{esc(s["desc"])}">'
            f'<link rel="canonical" href="https://koreaolympics.github.io/{s["name"]}.html">{HEAD_CSS}</head><body>'
            f'<a class="skip" href="#main">본문 바로가기</a><header class="topbar"><a class="brand" href="https://koreaolympics.github.io/index1.html">KOREA OLYMPICS</a><span>LA28 · 종목별 예선</span></header>'
            f'<div class="layout">{toc}<main id="main">{sportnav(s["name"])}<p class="eyebrow">ROAD TO LA28 / {s["eyebrow"]}</p>'
            f'<h1>2028 로스앤젤레스 올림픽 {s["sport"]} 예선</h1><p class="subtitle">본선 출전권 · 아시아 예선 · 대한민국의 진출 경로</p>'
            f'<p class="lead">{s["lead"]}</p>{facts}{tabs}{panels}'
            f'<section id="eligibility"><h2>참가 자격</h2>{s["elig"]}</section>'
            f'<section id="references"><h2>출처·자료 기준</h2>{refs}<p class="note">{s["refnote"]}</p></section>'
            f'<details class="compact"><summary>기존 상세 문서 주소</summary><p>{old}</p></details>'
            f'<footer class="footer"><a href="https://koreaolympics.github.io/index1.html">← 올림픽 예선 전체 목차</a> · <a href="#main">본문 위로</a>'
            f'<p>Korea Olympics · 비공식 한국어 안내 · 편집 2026.10.05</p></footer></main></div>{SCRIPT}</body></html>')
    return page


def alias(t, tab, ids):
    for p in ids:
        on = p == tab
        t = re.sub(rf'(<button id="tab-{p}" role="tab" aria-controls="panel-{p}") aria-selected="(true|false)" tabindex="-?\d"',
                   rf'\1 aria-selected="{"true" if on else "false"}" tabindex="{0 if on else -1}"', t)
        t = re.sub(rf'(<section id="panel-{p}" role="tabpanel" aria-labelledby="tab-{p}") ?(hidden)?>', rf'\1 {"" if on else "hidden"}>', t)
    for k in ["summary", "asia", "oqt", "others"]:
        t = t.replace(f'<a data-section="{k}" href="#{ids[0]}-{k}">', f'<a data-section="{k}" href="#{tab}-{k}">')
    return t


ELIG_COMMON = "올림픽 헌장(제41조 국적, 제43조 세계반도핑규약 및 경기 조작 방지 규정), 여성 카테고리 보호에 관한 IOC 정책, IOC 참가 조건 및 {}을 충족해야 합니다."

# ------------------------------------------------------------------ 수구
WP_PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/WPO-LA28-Qualification-System.pdf"


def wp_panel(g):
    n = "남자" if g == "men" else "여자"
    dates = "2028.07.12–22" if g == "men" else "2028.07.13–23"
    snap = ("2025 아시아선수권(자오칭) 5위 · 2026 아시안게임 8강에서 카자흐스탄에 14–18 패, 5위 결정전 홍콩 16–15 승 → 최종 5위(SBS 2026.10.03)."
            if g == "men" else
            "2025 아시아선수권(6개국)과 2026 아시안게임(6개국) 모두 불참. 대표팀은 2019 광주 세계선수권을 위해 처음 구성되었습니다.")
    return {
        "id": g, "title": f"{n} 예선", "total": "12팀",
        "road": [("개최국", 1), ("월드컵 2027", 1), ("세계선수권 부다페스트 2027", 2), ("대륙 예선", 5), ("월드퀄리파이어 2028", 3)],
        "rows": [["개최국", "미국", "1팀", "성별당 1팀 보장(D.2)"],
                 ["월드컵 2027", "2027.02.24–28 · 장소 미정", "1팀", "최상위 1팀"],
                 ["세계선수권", "부다페스트 2027.06.26–07.09", "2팀", "미확보 상위 2팀"],
                 ["대륙 예선", "2027.07–2028.01", "5팀", "5개 대륙선수권 최상위 각 1팀"],
                 ["월드퀄리파이어", "2028.04.03–09 · 04.17–23", "3팀", "미확보 상위 3팀"],
                 ["<strong>합계</strong>", f"본선 {dates}", "<strong>12팀</strong>", "NOC당 성별 1팀"]],
        "note": "앞 경로에서 확보한 팀은 뒤 경로 자리를 차지하지 않고 다음 순위로 넘깁니다. 미사용 출전권과 미사용 개최국 출전권은 부다페스트 2027 최종 순위의 다음 미확보 팀에게 재배정합니다(F.1·F.2).",
        "snapshot": "한국 현황(2026.10.05): " + snap,
        "asia": "<strong>아시아 대륙선수권(2027.07–2028.01 사이, 일정·장소 미정)</strong>의 최상위 1팀이 직행합니다. 아시안게임은 수구 LA28 예선 경로가 아닙니다. 대륙에서 놓치면 월드퀄리파이어 2028이 마지막 기회입니다.",
        "steps": [("아시아 대륙선수권", "아시아 1자리 · 이미 확보 시 차순위"), ("월드컵·세계선수권", "세계 상위권 3자리"), ("월드퀄리파이어 2028", "미확보 상위 3팀")],
        "oqt": ("<p>세계 대회는 월드컵 2027 → 세계선수권 부다페스트 2027 → (대륙 예선) → 월드퀄리파이어 2028 순서입니다. 월드퀄리파이어 참가 자격은 World Aquatics 대회 규정이 정하며, 대륙연맹이 2028.01.31까지 참가팀을 통보합니다.</p>"
                + wp_cascade(g) + wp_asia(g)),
        "others": ("<p>아프리카·아메리카·유럽·오세아니아 대륙선수권에서 각 최상위 1팀이 나옵니다. 대륙선수권이 열리지 않으면 월드퀄리파이어 2028의 해당 대륙 최상위 팀이, 대륙 대표가 한 팀뿐이면 그 팀이 출전권을 얻습니다. "
                   "대표 팀이 없는 대륙의 빈자리는 부다페스트 2027 다음 순위가 채웁니다.</p>"
                   '<p class="note">재배정 일정: 2028.01.31 대륙 결과 통보 → 02.01 NOC 통보 → 02.14 사용 확정. 각 예선 대회 뒤 NOC는 14일 안에 사용 여부를 확정합니다(E.1).</p>'),
    }


WATERPOLO = {
    "name": "olwaterpolo", "sport": "수구", "eyebrow": "WATER POLO", "icon": "pool",
    "desc": "LA28 수구 남녀 예선. 월드컵·세계선수권·대륙 예선·월드퀄리파이어 출전권 배정과 아시아·한국의 경로.",
    "lead": "남녀 각 12팀으로 LA28에서 처음 남녀 팀 수가 같아졌습니다. 월드컵·세계선수권·대륙 예선·월드퀄리파이어가 순서대로 자리를 채우며, 아시아에는 대륙 몫 1자리가 있습니다.",
    "facts": [("12팀", "남자 예선"), ("12팀", "여자 예선"), ("2027.02", "첫 예선 · 월드컵")],
    "labels": {"summary": ("출전권 요약", "출전권 요약"), "asia": ("아시아 예선과 대한민국의 경로", "아시아·대한민국"),
               "oqt": ("세계 예선 대회 · 배정 순서", "세계 예선 대회"), "others": ("기타 대륙 예선", "기타 대륙")},
    "panels": [wp_panel("men"), wp_panel("women")],
    "refline": "World Aquatics 규정 D·E·F",
    "elig": ("<p>" + ELIG_COMMON.format("World Aquatics 규정") + " 2028.12.31 기준 만 14세 이상이며 등록 여권으로 확인합니다(C.1). "
             "출전권은 NOC에 팀 단위로 배정되며 NOC당 남녀 각 1팀입니다. Ap(교체) 선수 정책은 팀당 인원을 포함해 늦어도 2026년 12월까지 갱신됩니다(G).</p>"),
    "refs": [(WP_PDF, "World Aquatics · LA28 Qualification System, Water Polo (IOC 게시 PDF, 2026.05.06판)"),
             ("https://www.worldaquatics.com/news/4498571/la28-olympic-games-angeles-2028-water-polo-qualification-system-finalised-ioc-world-aquatics", "World Aquatics · LA28 수구 예선 시스템 확정 발표"),
             ("https://total-waterpolo.com/japan-and-china-claim-gold-medals-at-asian-championships/", "Total Waterpolo · 2025 아시아선수권 최종 순위 (2025.03.03)"),
             ("https://news.sbs.co.kr/english/article.do?news_id=N1008775496", "SBS · 아시안게임 남자 8강 한국–카자흐스탄 (2026.09.29)"),
             ("https://news.sbs.co.kr/english/article.do?news_id=N1008782073", "SBS · 아시안게임 남자 5위 결정전 (2026.10.03)"),
             ("https://en.wikipedia.org/wiki/Water_polo_at_the_2026_Asian_Games_%E2%80%93_Women%27s_tournament", "Wikipedia · 2026 아시안게임 여자 수구")],
    "refnote": "IOC 게시 World Aquatics 규정 PDF(5쪽, Version as of 06 May 2026)는 2026.10.04에 전문을 확인했습니다. 아시아 대회 성적은 LA28 예선이 아닌 참고 자료이며, 최종 적용은 World Aquatics 공지를 따릅니다.",
    "aliases": {"olwaterpolo-men": "men", "olwaterpolo-women": "women", "olwaterpolo-events": "men", "olwaterpolo-continental": "men"},
}

# ------------------------------------------------------------------ 야구·소프트볼
BSB_PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/BSB-LA28-Qualification-System.pdf"
BASEBALL = {
    "name": "olbaseball", "sport": "야구·소프트볼", "eyebrow": "BASEBALL · SOFTBALL", "icon": "diamond",
    "desc": "LA28 야구·소프트볼 예선. WBC 2026·프리미어12·최종 예선과 소프트볼 대륙 예선, 아시아·한국의 경로.",
    "lead": "야구(남) 6팀·소프트볼(여) 6팀. 야구는 WBC 2026으로 베네수엘라·도미니카공화국이 이미 확정했고, 아시아 직행 1자리는 2027 프리미어12에서 정합니다. 소프트볼은 2027 대륙 예선이 중심입니다.",
    "facts": [("6팀", "야구 · 팀당 24명"), ("6팀", "소프트볼 · 팀당 15명"), ("3팀", "야구 확정 (미국·VEN·DOM)")],
    "labels": {"summary": ("출전권 요약", "출전권 요약"), "asia": ("아시아 예선과 대한민국의 경로", "아시아·대한민국"),
               "oqt": ("최종 예선 · 누가 나가나?", "최종 예선"), "others": ("확정 현황·기타 대륙", "현황·기타 대륙")},
    "panels": [
        {"id": "baseball", "title": "야구", "total": "6팀",
         "road": [("개최국", 1), ("WBC 2026 · 아메리카", 2), ("프리미어12 2027", 2), ("최종 예선", 1)],
         "rows": [["개최국", "미국", "1팀", "자동(D.1)"],
                  ["WBC 2026", "2026.03 · 종료", "2팀", "아메리카 상위 2팀 — 베네수엘라·도미니카공화국"],
                  ["프리미어12", "2027.11", "2팀", "아시아 최상위 1 · 유럽·오세아니아 최상위 1"],
                  ["최종 예선", "2028.03까지", "1팀", "6팀 중 우승"],
                  ["<strong>합계</strong>", "본선 2028.07", "<strong>6팀</strong>", "팀당 24명 · Ap 4명"]],
         "note": "미국이 개최국 자리를 쓰지 않으면 프리미어12의 미확보 차순위 팀이 받습니다. 미사용 쿼터 재배정은 2028.05.26입니다.",
         "snapshot": "한국 현황(2026.10.05): WBC 2026 최종 8위 · 2025 BFA 아시아선수권 3위(일본 1·대만 2). 아시안게임은 야구 예선 경로가 아닙니다.",
         "asia": "<strong>WBSC 프리미어12 2027</strong>에서 아시아 참가국 중 1위를 하면 직행합니다. 놓치면 '최근' 아시아선수권의 미확보 상위 2팀으로 최종 예선에 나갑니다.",
         "steps": [("프리미어12 2027", "아시아 최상위 1팀 직행"), ("아시아선수권", "미확보 상위 2팀 → 최종 예선"), ("최종 예선 · 6팀", "우승 1팀만 LA28")],
         "oqt": "<p>야구 최종 예선은 각 대륙의 최신 선수권 결과로 6팀을 모읍니다. 쓰지 않는 자리는 그 대회 차순위 팀에게 갑니다.</p>" + bb_premier() + bb_fqe(),
         "others": ('<div class="table-wrap"><table><caption>야구 확정 현황</caption><thead><tr><th scope="col">팀</th><th scope="col">경로</th><th scope="col">확정</th></tr></thead><tbody>'
                    "<tr><td>미국</td><td>개최국</td><td>자동</td></tr><tr><td>베네수엘라</td><td>WBC 2026 우승</td><td>2026.03</td></tr>"
                    "<tr><td>도미니카공화국</td><td>WBC 2026 3위</td><td>2026.03</td></tr><tr><td>미정</td><td>프리미어12 아시아 / 유럽·오세아니아</td><td>2027.11</td></tr>"
                    "<tr><td>미정</td><td>최종 예선</td><td>2028.03 이전</td></tr></tbody></table></div>"
                    '<p class="note">유럽·오세아니아는 프리미어12 1자리와 최종 예선 3자리(유럽 2·오세아니아 1), 아프리카는 최종 예선 1자리가 있습니다.</p>')},
        {"id": "softball", "title": "소프트볼", "total": "6팀",
         "road": [("개최국", 1), ("소프트볼 월드컵 파이널 2027", 1), ("2027 대륙 예선 (1위)", 3), ("최종 예선", 1)],
         "rows": [["개최국", "미국", "1팀", "자동(D.5)"],
                  ["월드컵 파이널", "2027", "1팀", "최상위 1팀"],
                  ["대륙 예선", "2027 · 3개 대륙", "3팀", "아메리카·아시아/오세아니아·유럽/아프리카 각 1위"],
                  ["최종 예선", "2028.03까지", "1팀", "대륙 예선 2·3위 6팀 중 우승"],
                  ["<strong>합계</strong>", "본선 2028.07", "<strong>6팀</strong>", "팀당 15명"]],
         "note": "미국이 개최국 자리를 쓰지 않으면 월드컵 파이널의 미확보 차순위 팀이 받습니다. 대륙 예선 일정은 규정 원문에 'XXX 2027'로 미정입니다(아메리카는 캐나다 서리).",
         "snapshot": "한국 현황(2026.10.05): 아시아/오세아니아 대륙 예선에서 일본·호주 등 강호와 경쟁합니다. 아시안게임은 소프트볼 예선 경로가 아닙니다.",
         "asia": "<strong>2027 아시아/오세아니아 대륙 예선</strong> 1위가 직행, 2·3위가 최종 예선에 나갑니다. 한국은 최소 3위 안이 첫 목표입니다.",
         "steps": [("아시아/오세아니아 예선", "1위 직행"), ("2·3위", "최종 예선 진출"), ("최종 예선 · 6팀", "우승 1팀만 LA28")],
         "oqt": "<p>소프트볼 최종 예선은 3개 대륙 예선 2·3위 6팀(대륙별 2팀)으로 구성되고 우승 1팀이 출전합니다(D.8).</p>" + sb_flow(),
         "others": "<p>아메리카 예선은 캐나다 서리에서 열리며, 유럽과 아프리카는 하나의 대륙 예선으로 묶입니다. 월드컵 파이널 1위가 먼저 확보하면 대륙 예선에서는 다음 순위가 직행합니다.</p>"},
    ],
    "refline": "WBSC 규정 D·E·F",
    "elig": ("<p>" + ELIG_COMMON.format("WBSC 규정") + " 야구는 대회 연도에 만 18세, 소프트볼은 만 16세가 되어야 합니다. "
             "쿼터는 NOC에 팀 단위로 배정되며 종목별 1팀입니다. 야구는 팀당 Ap(교체 대기) 선수 4명을 둘 수 있습니다.</p>"),
    "refs": [(BSB_PDF, "WBSC · LA28 Qualification System, Baseball/Softball (IOC 게시 PDF, 2026.05.12판)"),
             ("https://www.wbsc.org/en/news/dominican-republic-and-venezuela-make-history-as-first-teams-to-qualify-for-la28-olympic-baseball", "WBSC · 도미니카공화국·베네수엘라 LA28 첫 진출"),
             ("https://www.wbsc.org/en/news/japan-win-xxxi-bfa-asian-baseball-championship-qualify-for-wbsc-u-23-baseball-world-cup-2026-with-runner-up-chinese-taipei-and-third-place-korea", "WBSC · 2025 BFA 아시아선수권 결과"),
             ("https://en.wikipedia.org/wiki/Baseball_at_the_2028_Summer_Olympics_%E2%80%93_Qualification", "Wikipedia · 2028 올림픽 야구 예선")],
    "refnote": "IOC 게시 WBSC 규정 PDF(5쪽, Version as of 12 May 2026)는 2026.10.04에 전문을 확인했습니다. 최종 적용은 WBSC 공지를 따릅니다.",
    "aliases": {"olbaseball-baseball": "baseball", "olbaseball-softball": "softball", "olbaseball-fqe": "baseball"},
}

# ------------------------------------------------------------------ 크리켓
CRT_PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/CRT-LA28-Qualification-System.pdf"


def cr_panel(g):
    men = g == "men"
    n = "남자" if men else "여자"
    return {
        "id": g, "title": f"{n} 예선", "total": "6팀",
        "road": [("개최국", 1), ("ICC 남자 T20I 랭킹 · 대륙별 최상위" if men else "여자 T20 월드컵 2026 · 대륙별 최상위", 4), ("최종 글로벌 예선 (FOGQT)", 1)],
        "rows": [["개최국", "미국", "1팀", f"예선 기간 중 ICC {n} T20 랭킹 15위 이내 이력"],
                 (["ICC T20I 랭킹", "2026.12.31 마감", "4팀", "서로 다른 대륙 최상위 4개국"] if men else
                  ["T20 월드컵 2026", "2026.06.12–07.06 · 종료", "4팀", "호주·영국·인도·남아공 확정"]),
                 ["최종 글로벌 예선", "2027 (미정)", "1팀", "다음 8개 미확보국 중 우승 · 대륙 제한 없음"],
                 ["<strong>합계</strong>", "본선 2028.07.12–29", "<strong>6팀</strong>", "팀당 15명"]],
        "note": ("최종 예선 8개국은 2026.12.31 랭킹으로 정합니다. 서인도제도가 들어가면 지역 예선으로 대표 국가를 정합니다(서인도제도는 NOC가 아님)." if men else
                 "최종 예선 8개국은 2027.03.01 여자 랭킹으로 정합니다."),
        "snapshot": ("현황(2026.10.05): 남자 4자리는 2026.12.31 랭킹 마감 때 정해집니다. 아시아 자리는 인도가 유력합니다." if men else
                     "확정(ICC 2026.06.29): 호주(오세아니아)·영국(유럽)·인도(아시아)·남아공(아프리카)."),
        "asia": ("아시아 대륙 자리는 ICC 랭킹 아시아 최상위국 1팀입니다. " + ("인도가 유력하므로" if men else "인도가 확정했으므로")
                 + " 한국을 포함한 다른 아시아 국가는 <strong>최종 글로벌 예선(다음 8개국)</strong>에 들어야 합니다. 한국은 ICC 준회원국이며 현재 T20I 순위는 이번 편집에서 확인하지 않았습니다."),
        "steps": [("ICC 랭킹 · 아시아 1위", "인도 " + ("유력" if men else "확정")), ("랭킹 다음 8개국", "최종 글로벌 예선 진출"), ("최종 글로벌 예선", "우승 1팀만 LA28")],
        "oqt": "<p>대륙별 최상위 4팀은 서로 다른 대륙이어야 하며, 최종 글로벌 예선에는 대륙 제한이 없습니다(ICC 규정 D.1·D.3·D.4·D.6).</p>" + cr_rank(g),
        "others": ("<p>유럽 자리는 영국(잉글랜드 1개 팀만 반영), 오세아니아는 호주·뉴질랜드, 아프리카는 남아공 등이 경쟁합니다. 아메리카는 서인도제도가 NOC가 아니어서 랭킹 계산에서 빠지고, 미국은 개최국 자리를 씁니다.</p>"
                   if men else
                   "<p>여자 4개 대륙 자리는 이미 확정되었습니다. 남은 1자리는 2027.03.01 랭킹 기준 8개국이 겨루는 최종 글로벌 예선에서 정합니다.</p>"),
    }


CRICKET = {
    "name": "olcricket", "sport": "크리켓", "eyebrow": "CRICKET (T20)", "icon": "oval",
    "desc": "LA28 크리켓 남녀 T20 예선. ICC 랭킹·T20 월드컵·최종 글로벌 예선 출전권 배정과 아시아·한국의 경로.",
    "lead": "1900년 이후 처음 올림픽에 돌아오는 크리켓은 20오버(T20) 방식 남녀 6팀씩입니다. 대륙별 최상위 4팀과 개최국, 최종 글로벌 예선 우승팀이 출전합니다. 여자 4팀은 이미 확정되었습니다.",
    "facts": [("6팀", "남자 · 팀당 15명"), ("6팀", "여자 · 팀당 15명"), ("4팀", "여자 확정")],
    "labels": {"summary": ("출전권 요약", "출전권 요약"), "asia": ("아시아와 대한민국의 경로", "아시아·대한민국"),
               "oqt": ("대륙별 최상위 · 최종 글로벌 예선", "선발 구조"), "others": ("기타 대륙", "기타 대륙")},
    "panels": [cr_panel("men"), cr_panel("women")],
    "refline": "ICC 규정 D·H",
    "elig": ("<p>" + ELIG_COMMON.format("ICC 규정") + " 명단 제출일 또는 첫 경기일에 만 15세 이상이어야 합니다. "
             "쿼터는 NOC에 팀 단위(15명)로 배정됩니다. 영국은 잉글랜드 1개 팀만 반영하며, 서인도제도는 IOC 회원 NOC가 아니어서 출전할 수 없습니다.</p>"),
    "refs": [(CRT_PDF, "ICC · LA28 Qualification System (IOC 게시 PDF, 2026.06.22판)"),
             ("https://www.icc-cricket.com/news/first-four-teams-confirmed-for-women-s-cricket-at-la28", "ICC · LA28 여자 크리켓 첫 4팀 확정 (2026.06.29)")],
    "refnote": "IOC 게시 ICC 규정 PDF(6쪽, Version as of 22 June 2026)는 2026.10.04에 전문을 확인했습니다. 최종 적용은 ICC 공지를 따릅니다.",
    "aliases": {"olcricket-men": "men", "olcricket-women": "women"},
}

# ------------------------------------------------------------------ 라크로스
LAC_PDF = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/LAC-LA28-Qualification-System.pdf"


def lac_panel(g):
    n = "남자" if g == "men" else "여자"
    return {
        "id": g, "title": f"{n} 예선", "total": "6팀",
        "road": [("개최국", 1), ("2027 식스 세계선수권", 4), ("최종 예선 2028", 1)],
        "rows": [["개최국", "미국", "1팀", "대륙 예선·세계선수권 출전 조건(D.1)"],
                 ["대륙 예선", "2026.09–12", "0팀", "세계선수권 16팀 선발만"],
                 ["식스 세계선수권", "2027.10–11", "4팀", "미국 제외 상위 4 · 대륙별 최소 1 · 최대 3 · 12위 이내"],
                 ["최종 예선", "2028.03–04", "1팀", "세계선수권 다음 6팀 · 리그전 후 결승"],
                 ["<strong>합계</strong>", "본선 2028.07", "<strong>6팀</strong>", "팀당 11명 (식스)"]],
        "note": "미국은 세계선수권 출전이 곧 개최국 자리 사용 확인입니다. 쓰지 않는 자리는 세계선수권 차순위로 넘어가며, 재배정은 2028.05입니다.",
        "snapshot": f"한국 현황(2026.10.05): {n} 대표팀이 호주 선샤인코스트 아시아태평양 식스 선수권(2026.10.05–10)에 출전 중입니다. 결과는 10.10 이후 반영합니다.",
        "asia": "<strong>아시아태평양 식스 선수권(APLU)</strong>은 올림픽 쿼터가 아니라 2027 세계선수권 출전권 5자리를 정합니다. 한국은 5위 안에 들어야 세계선수권에 나가고, 거기서 상위 4팀(대륙별 최소 1) 또는 다음 6팀(최종 예선)에 들어야 합니다.",
        "steps": [("APAC 선수권 · 2026.10", "상위 5팀 → 세계선수권"), ("2027 세계선수권", "상위 4팀 직행"), ("최종 예선 · 6팀", "우승 1팀")],
        "asia_more": "<p class=\"compact\">아시아태평양 경쟁국: 호주·뉴질랜드·일본·인도·중국·싱가포르·필리핀·홍콩·대만" + (" · 사우디아라비아 (남자 11개국)" if g == "men" else " (여자 10개국)") + ".</p>",
        "oqt": "<p>세계선수권 16팀 순위가 직행 4팀과 최종 예선 6팀을 모두 정합니다. 최종 예선은 6팀 리그전 뒤 1·2위 결승으로 우승 1팀을 가립니다(D.4).</p>" + lac_funnel(g),
        "others": ('<div class="table-wrap"><table><caption>대륙 예선 → 세계선수권 진출 (쿼터 없음)</caption><thead><tr><th scope="col">대륙연맹</th><th scope="col">세계선수권 진출</th><th scope="col">대륙 예선</th></tr></thead><tbody>'
                   "<tr><td>아프리카 (AAL)</td><td>1</td><td>2026.12 (미정)</td></tr><tr><td>아시아태평양 (APLU)</td><td>5</td><td>2026.10.05–10 · 선샤인코스트</td></tr>"
                   "<tr><td>유럽 (ELF)</td><td>5</td><td>2026.11.02–18</td></tr><tr><td>팬암 (PALA)</td><td>5</td><td>2026.09–10 (미정)</td></tr></tbody></table></div>"),
    }


LACROSSE = {
    "name": "ollacrosse", "sport": "라크로스", "eyebrow": "LACROSSE SIXES", "icon": "field",
    "desc": "LA28 라크로스 식스 남녀 예선. 대륙 예선·2027 세계선수권·최종 예선 구조와 아시아태평양·한국의 경로.",
    "lead": "라크로스는 6명씩 뛰는 식스(Sixes) 방식으로 남녀 6팀씩 출전합니다. 2026 대륙 예선 → 2027 식스 세계선수권 → 2028 최종 예선 순서이며, 한국은 오늘(10.05) 시작한 아시아태평양 예선에 남녀 모두 출전 중입니다.",
    "facts": [("6팀", "남자 · 팀당 11명"), ("6팀", "여자 · 팀당 11명"), ("16팀", "2027 세계선수권")],
    "labels": {"summary": ("출전권 요약", "출전권 요약"), "asia": ("아시아태평양 예선과 대한민국의 경로", "아시아·대한민국"),
               "oqt": ("세계선수권 · 최종 예선", "세계선수권·최종 예선"), "others": ("대륙 예선 일정", "대륙 예선")},
    "panels": [lac_panel("men"), lac_panel("women")],
    "refline": "World Lacrosse 규정 D·G",
    "elig": ("<p>" + ELIG_COMMON.format("World Lacrosse 규정") + " 경기 시작 전날 기준 남자 16세·여자 15세 이상이어야 합니다. "
             "World Lacrosse 정회원 또는 다국가 회원 소속이며 그 회원이 IOC 승인 NOC 안에 있어야 합니다. 쿼터는 NOC에 배정되며 성별 1팀, 영국은 Great Britain 한 팀만 인정합니다.</p>"),
    "refs": [(LAC_PDF, "World Lacrosse · LA28 Qualification System (IOC 게시 PDF, 2026.05.12판)"),
             ("https://lacrosse.com.au/news/2026/08/11/olympic-qualifier-to-bring-asia-pacifics-best-lacrosse-teams-to-the-sunshine-coast/", "Lacrosse Australia · 아시아태평양 식스 선수권 안내 (2026.08.11)")],
    "refnote": "IOC 게시 World Lacrosse 규정 PDF(5쪽, Version as of 12 May 2026)는 2026.10.04에 전문을 확인했습니다. 아시아태평양 예선 결과는 2026.10.10 이후 반영합니다.",
    "aliases": {"ollacrosse-men": "men", "ollacrosse-women": "women"},
}

if __name__ == "__main__":
    for s in [WATERPOLO, BASEBALL, CRICKET, LACROSSE]:
        t = build(s)
        ids = [p["id"] for p in s["panels"]]
        open(OUT + s["name"] + ".html", "w", encoding="utf-8", newline="\r\n").write(t)
        print("wrote", s["name"], len(t))
        for a, tab in s["aliases"].items():
            open(OUT + a + ".html", "w", encoding="utf-8", newline="\r\n").write(alias(t, tab, ids))
            print("  alias", a, tab)
