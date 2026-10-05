# -*- coding: utf-8 -*-
"""구기종목 신규 레이아웃 초안에 SVG 설명 그림 추가 + 사실 보정 + 탭별 별칭 파일 생성."""
import re, os, html as H

UP = "/root/.claude/uploads/d605e20f-a928-5cf2-a6a8-5bb76056abad/"
OUT = "/root/site/"
DARK, BLUE, LBLUE, TEAL, LTEAL, ORG, LORG, LINE, INK, MUTE = "#233e50", "#2454a6", "#eaf0fa", "#267b76", "#e6efed", "#b9734f", "#f6e9e1", "#bdc8d4", "#202122", "#54595d"
FONT = 'font-family="Arial, Malgun Gothic, sans-serif"'

CSS = (".figx{margin:22px 0 26px;padding:16px 18px 14px;background:#f8fafc;border-block:1px solid #c8ccd1}"
       ".figx .sc{overflow-x:auto}.figx svg{display:block;width:100%;height:auto;max-width:780px;margin:auto}"
       ".figx figcaption{font-size:13px;color:#54595d;margin-top:10px;line-height:1.55}.figx figcaption b{color:#202122}"
       "@media(max-width:540px){.figx{padding:12px 8px}.figx svg{min-width:560px}}")


def esc(s):
    return H.escape(s, quote=True)


def T(x, y, s, size=16, fill=INK, anchor="start", weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'


def R(x, y, w, h, fill="#fff", stroke=LINE, rx=3, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def A(x1, y1, x2, y2, color="#99a9bb", sw=1.8):
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - 8 * math.cos(ang - .45), y2 - 8 * math.sin(ang - .45)
    hx2, hy2 = x2 - 8 * math.cos(ang + .45), y2 - 8 * math.sin(ang + .45)
    return (f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M{hx1:.1f} {hy1:.1f}L{x2} {y2}L{hx2:.1f} {hy2:.1f}" fill="none" stroke="{color}" stroke-width="{sw}"/>')


def DOT(cx, cy, r=8, fill=BLUE, stroke="#fff"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'


def svg(uid, w, h, title, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc><g {FONT}>{body}</g></svg>')


def fig(uid, w, h, title, desc, body, cap):
    return f'<figure class="figx"><div class="sc">{svg(uid, w, h, title, desc, body)}</div><figcaption>{cap}</figcaption></figure>'


# ---------------------------------------------------------------- 그림들
def qseries_flag(g):
    """플래그풋볼 Q-시리즈: 5개 대륙 × 2팀 → 3자리 (최소 2개 대륙)"""
    conts = ["아프리카", "아메리카", "아시아", "유럽", "오세아니아"]
    b = T(20, 28, "2027 대륙선수권", 15, MUTE) + T(330, 28, "2028 Q-시리즈 · 10팀", 15, MUTE) + T(600, 28, "LA28", 15, MUTE)
    for i, c in enumerate(conts):
        y = 44 + i * 52
        asia = c == "아시아"
        b += R(20, y, 190, 40, LORG if asia else "#fff", ORG if asia else LINE)
        b += T(34, y + 26, c + (" (한국 경로)" if asia else ""), 15, INK, weight="600" if asia else "400")
        b += DOT(236, y + 14, 7, ORG if asia else BLUE) + DOT(256, y + 26, 7, ORG if asia else BLUE)
        b += A(270, y + 20, 322, 150 + (i - 2) * 10)
    b += R(330, 70, 220, 160, LBLUE, BLUE)
    b += T(440, 112, "몬트리올 2028.06.01–04", 15, INK, "middle") + T(440, 138, "올랜도 2028.06.08–11", 15, INK, "middle")
    b += T(440, 176, "남녀 통합 대회", 14, MUTE, "middle") + T(440, 200, "이미 확보한 팀 제외", 14, MUTE, "middle")
    b += A(552, 150, 594, 150)
    for k in range(3):
        b += R(600, 92 + k * 40, 100, 32, DARK, DARK) + T(650, 114 + k * 40, f"출전권 {k + 1}", 15, "#fff", "middle")
    b += T(650, 232, "최소 2개 대륙", 14, ORG, "middle", "600")
    n = "남자" if g == "men" else "여자"
    return fig(f"ffb-q-{g}", 720, 312, f"플래그풋볼 {n} Q-시리즈 구조", "5개 대륙선수권에서 2팀씩 10팀이 Q-시리즈에 나가 상위 3팀이 LA28 출전권을 얻는다. 3팀은 최소 2개 대륙이어야 한다.",
               b, f"<b>Q-시리즈 구조 ({n})</b> · 대륙별 2팀씩 10팀이 몬트리올·올랜도 두 대회를 치러 상위 3팀이 출전합니다. 3팀은 최소 2개 대륙이어야 합니다(IFAF 규정 D.3). 한국은 2026 세계선수권에 나가지 않아 이 경로가 유일합니다.")


def football_w():
    b = T(20, 28, "아시아 여자 올림픽 예선", 15, MUTE) + T(470, 28, "LA28", 15, MUTE)
    for i, (lab, col) in enumerate([("1위", BLUE), ("2위", BLUE), ("3위", ORG)]):
        y = 44 + i * 56
        b += R(20, y, 170, 44, LORG if col == ORG else "#fff", col) + T(40, y + 28, f"아시아 {lab}", 16, INK, weight="600")
    b += A(192, 66, 460, 66) + A(192, 122, 460, 122)
    b += R(470, 46, 210, 40, DARK, DARK) + T(575, 72, "직행 1", 16, "#fff", "middle") + R(470, 102, 210, 40, DARK, DARK) + T(575, 128, "직행 2", 16, "#fff", "middle")
    b += R(20, 214, 170, 44, "#fff", LINE) + T(40, 242, "남미 3위", 16, INK, weight="600")
    b += A(192, 178, 262, 200, ORG) + A(192, 236, 262, 214, ORG)
    b += R(268, 186, 170, 44, LORG, ORG) + T(353, 213, "대륙 간 플레이오프", 15, INK, "middle", "600")
    b += A(440, 208, 466, 208, ORG)
    b += R(470, 188, 210, 40, DARK, DARK) + T(575, 214, "승자 1팀", 16, "#fff", "middle")
    return fig("fb-w-po", 700, 278, "여자 축구 아시아 2.5장 구조", "아시아 1·2위는 직행하고 3위는 남미 3위와 대륙 간 플레이오프를 치러 승자 1팀이 출전한다.",
               b, "<b>아시아 2.5장의 뜻</b> · 0.5장은 반쪽 자리가 아니라, 아시아 3위와 남미 3위가 본선 1자리를 놓고 치르는 대륙 간 플레이오프입니다.")


def football_m():
    b = T(20, 28, "2028 AFC U23 아시안컵 (일본)", 15, MUTE)
    for i in range(4):
        y = 44 + i * 48
        top = i < 2
        b += R(20, y, 190, 38, "#fff", BLUE if top else LINE) + T(40, y + 25, f"{i + 1}위", 16, INK, weight="600" if top else "400")
        if top:
            b += A(212, y + 19, 286, y + 19)
            b += R(292, y, 150, 38, DARK, DARK) + T(367, y + 25, f"LA28 {i + 1}", 16, "#fff", "middle")
    b += T(232, 160, "플레이오프 없음", 15, MUTE) + T(232, 182, "(파리 2024의 아시아 4위 PO와 다름)", 13, MUTE)
    return fig("fb-m", 470, 240, "남자 축구 아시아 2장", "2028 AFC U23 아시안컵 1·2위가 LA28에 출전한다. 대륙 간 플레이오프는 없다.",
               b, "<b>남자 아시아 2장</b> · U23 아시안컵 상위 2팀이 직행합니다. 3위 이하에는 추가 기회가 없습니다.")


def hockey(g):
    data = [("유럽", 8, 9), ("아시아", 6, 4), ("팬아메리카", 1, 3), ("오세아니아", 1, 1), ("아프리카", 1, 0)]
    n = "남자" if g == "men" else "여자"
    idx = 1 if g == "men" else 2
    total = sum(d[idx] for d in data)
    b = T(20, 26, f"FIH 올림픽 예선 초청 몫 ({n}, 부록 1 · 2026.08.31 랭킹)", 15, MUTE)
    x = 20
    unit = 640 / total
    for name, m, w in data:
        v = (m, w)[idx - 1]
        if not v:
            continue
        asia = name == "아시아"
        b += R(round(x, 1), 40, round(v * unit - 3, 1), 46, LORG if asia else LBLUE, ORG if asia else BLUE, 2)
        b += T(round(x + v * unit / 2, 1), 69, f"{name} {v}" if v > 1 else f"{v}", 15 if v > 1 else 13, INK, "middle", "600" if asia else "400")
        x += v * unit
    asia_n = data[1][idx]
    b += T(20, 116, f"아시아 {asia_n}자리 = 아시안게임 미확보 상위 순서", 16, INK, weight="600")
    ranks = list(range(1, 9))
    for i, r in enumerate(ranks):
        cx = 40 + i * 76
        filled = 2 <= r <= asia_n + 1
        kor = r == 4
        b += R(cx - 30, 132, 60, 40, DARK if r == 1 else (LORG if kor else (LBLUE if filled else "#fff")), ORG if kor else (BLUE if filled else LINE), 3)
        b += T(cx, 158, f"{r}위", 15, "#fff" if r == 1 else INK, "middle", "600" if kor else "400")
    b += T(40, 194, "인도 · 직행", 13, MUTE, "middle") + T(268, 194, "한국", 14, ORG, "middle", "700")
    b += T(20, 230, f"→ 16팀이 8팀씩 2개 대회 · 각 상위 2팀 = 4자리 (2028 초)", 15, INK)
    return fig(f"hoc-{g}", 700, 250, f"필드하키 {n} 올림픽 예선 초청 구조", f"올림픽 예선 초청 16팀의 대륙별 몫과 아시아 몫을 아시안게임 순위로 채우는 방식. 한국은 아시안게임 4위.",
               b, f"<b>초청 계산 ({n})</b> · 부록 1의 아시아 몫 {asia_n}자리는 아시안게임에서 출전권을 얻지 못한 상위 팀 순서로 채웁니다(1위 인도 제외 → {2}–{asia_n + 1}위). 한국(4위)은 현재 기준 범위 안이지만, 2027 마지막 대륙선수권 뒤 랭킹으로 다시 계산하고 프로리그 시즌8 우승 대륙 몫이 1 줄어듭니다.")


def rugby(g):
    regions = ["아프리카", "아시아", "유럽", "북미", "오세아니아", "남미"]
    n = "남자" if g == "men" else "여자"
    b = T(20, 26, "2027 지역 올림픽 예선 (6곳)", 15, MUTE) + T(470, 26, "2028.06 최종 리페차지 · 8팀", 15, MUTE)
    for i, r in enumerate(regions):
        y = 40 + i * 40
        asia = r == "아시아"
        b += R(20, y, 150, 32, LORG if asia else "#fff", ORG if asia else LINE) + T(34, y + 22, r, 15, INK, weight="600" if asia else "400")
        b += T(184, y + 22, "우승 →", 14, MUTE) + R(238, y + 4, 70, 24, DARK, DARK) + T(273, y + 21, "LA28", 13, "#fff", "middle")
        b += A(312, y + 16, 466, 150 + (i - 2.5) * 12, "#c2ccd6", 1.4)
    b += R(472, 76, 220, 150, LBLUE, BLUE)
    b += T(582, 106, "지역별 1팀 (6)", 15, INK, "middle") + T(582, 132, "+ 추가 2개 지역 1팀씩 (미정)", 14, INK, "middle")
    b += T(582, 160, "2027 세븐스 지역 성적 기준", 13, MUTE, "middle")
    b += R(522, 178, 120, 34, DARK, DARK) + T(582, 201, "우승 1팀", 15, "#fff", "middle")
    b += T(20, 290, "북미 팀이 SVNS로 확보하면 북미 지역 1위는 리페차지로만 가고, 리페차지 2위가 출전합니다" + (" (여자는 오세아니아 3팀 확보 시도 동일)." if g == "women" else "."), 13, MUTE)
    return fig(f"ru-{g}", 720, 304, f"7인제 럭비 {n} 지역 예선과 리페차지", "6개 지역 예선 우승팀은 직행하고, 지역별 차순위 팀이 8팀 리페차지에 나가 우승 1팀이 출전한다.",
               b, f"<b>지역 예선 → 리페차지 ({n})</b> · 아시아는 2027 아시아 지역 예선 우승 1팀이 직행합니다. 리페차지 8자리 중 아시아 몫은 기본 1자리이며, 추가 2자리가 어느 지역에 갈지는 아직 정해지지 않았습니다.")


def handball(g):
    n = "남자" if g == "men" else "여자"
    rows = [("토너먼트 1", ["세계선수권 2위", "세계선수권 7위", "QS3 · 3번째 대륙", "QS4 · 4번째 대륙"]),
            ("토너먼트 2", ["세계선수권 3위", "세계선수권 6위", "QS2 · 2번째 대륙", "QS5 · 1번째 대륙 2위"]),
            ("토너먼트 3", ["세계선수권 4위", "세계선수권 5위", "QS1 · 1번째 대륙", "QS6 · 오세아니아·2번째 대륙"])]
    b = T(20, 26, "IHF 올림픽 예선 토너먼트 편성 (규정 D.3·D.7)", 15, MUTE)
    for i, (t, cells) in enumerate(rows):
        y = 40 + i * 70
        b += R(20, y, 110, 58, DARK, DARK) + T(75, y + 34, t, 15, "#fff", "middle")
        for j, c in enumerate(cells):
            x = 140 + j * 140
            qs = c.startswith("QS")
            b += R(x, y, 132, 58, LORG if qs else LBLUE, ORG if qs else BLUE)
            parts = c.split(" · ")
            b += T(x + 66, y + (26 if len(parts) > 1 else 34), parts[0], 14, INK, "middle", "600")
            if len(parts) > 1:
                b += T(x + 66, y + 46, parts[1], 11.5, MUTE, "middle")
        b += A(702, y + 29, 726, y + 29) + T(732, y + 34, "상위 2", 14, INK, weight="600")
    b += R(140, 258, 14, 14, LBLUE, BLUE) + T(160, 270, "세계선수권 경로", 13, MUTE) + R(290, 258, 14, 14, LORG, ORG) + T(310, 270, "대륙 경로 (QS) — 아시아 순위는 세계선수권 대륙 성적으로 결정", 13, MUTE)
    return fig(f"hbl-{g}", 800, 286, f"핸드볼 {n} 올림픽 예선 토너먼트 편성", "세 개 토너먼트에 세계선수권 2–7위 6팀과 대륙 몫 QS1–QS6 6팀을 배치하고 각 대회 상위 2팀이 출전한다.",
               b, f"<b>예선 토너먼트 편성 ({n})</b> · LA28 규정이 직접 정한 방식입니다. 대륙 몫 QS는 세계선수권에서 각 대륙 최상위 팀 성적순으로 1번째(2자리)·2–4번째 대륙(1자리)에 돌아가고, 해당 대륙 예선의 미확보 상위 팀이 받습니다.")


def bk_men():
    b = T(20, 26, "FIBA 올림픽 예선 (FOQT) 24팀 구성", 15, MUTE)
    segs = [("월드컵 비직행 대륙 최상위", 3, LORG, ORG), ("월드컵 성적 상위", 16, LBLUE, BLUE), ("사전예선 FOPQT", 5, LTEAL, TEAL)]
    x = 20
    for lab, v, f, s in segs:
        w = v * 27
        b += R(x, 40, w - 3, 46, f, s, 2) + T(x + w / 2, 69, f"{v}", 17, INK, "middle", "600")
        b += T(x + w / 2, 106, lab, 12.5, MUTE, "middle")
        x += w
    b += T(20, 150, "→ 6팀씩 4개 대회 (2028.06.26–07.02) · 각 우승 1팀 = 4자리", 15, INK, weight="600")
    for k in range(4):
        b += R(20 + k * 170, 166, 160, 40, "#fff", LINE)
        for d in range(6):
            b += DOT(42 + k * 170 + d * 22, 186, 7, DARK if d == 0 else "#c8d2de")
    b += T(20, 232, "사전예선 아시아 몫 1자리는 오세아니아 포함 · 한국은 월드컵 또는 사전예선을 거쳐야 함", 13, MUTE)
    return fig("bk-m", 700, 246, "남자 농구 올림픽 예선 구성", "24팀은 월드컵 경로 19팀과 사전예선 5팀으로 구성되며 6팀씩 4개 대회 우승팀이 출전한다.",
               b, "<b>남자 FOQT</b> · 월드컵에서 직행 7팀을 뺀 성적순으로 19팀, 2027 사전예선 5팀이 합류합니다. 아시아 직행은 월드컵 아시아 최상위 1팀뿐입니다.")


def bk_women():
    b = T(20, 26, "여자 올림픽 예선 (FWOQT) 16팀 — 2027 대륙컵 몫", 15, MUTE)
    segs = [("아프리카", 2), ("아메리카", 4), ("아시아·오세아니아", 4), ("유럽", 6)]
    x = 20
    for lab, v in segs:
        w = v * 40
        asia = lab.startswith("아시아")
        b += R(x, 40, w - 3, 46, LORG if asia else LBLUE, ORG if asia else BLUE, 2) + T(x + w / 2, 69, f"{v}", 17, INK, "middle", "600")
        b += T(x + w / 2, 106, lab, 12.5, ORG if asia else MUTE, "middle", "600" if asia else "400")
        x += w
    b += T(20, 148, "→ 4팀씩 4개 조 · 각 조 상위 3팀 = 12 (미국 포함 조는 미국 + 2팀)", 15, INK, weight="600")
    for k in range(4):
        b += R(20 + k * 165, 162, 155, 40, "#fff", LINE)
        for d in range(4):
            col = DARK if d < 3 else "#c8d2de"
            if k == 0 and d == 0:
                col = BLUE
            b += DOT(46 + k * 165 + d * 32, 182, 8, col)
    b += T(46, 222, "파랑: 미국 (개최국·월드컵 우승 중복) · 남은 출전권 11", 13, MUTE)
    return fig("bk-w", 700, 238, "여자 농구 올림픽 예선 구성", "2027 대륙컵에서 16팀을 뽑아 4팀씩 4개 조로 나누고 각 조 상위 3팀이 출전한다. 미국이 들어간 조는 미국과 2팀.",
               b, "<b>여자 FWOQT</b> · 한국은 2027 여자 아시아컵 4위 안(사전예선 우승국이 아시아면 그만큼 차감)에 들어야 참가합니다. 미국이 개최국과 월드컵 우승을 겹쳐 가져가 예선 출전권은 11장입니다.")


def bk_3x3(g):
    n = "남자" if g == "men3" else "여자"
    b = T(20, 26, f"3×3 NOC 랭킹 직행 5자리 ({n}, 2027.12.01)", 15, MUTE)
    zones = [("아프리카", 1), ("유럽", 1), ("아메리카", 1), ("아시아·오세아니아", 2)]
    for i, (z, v) in enumerate(zones):
        x = 20 + i * 168
        asia = z.startswith("아시아")
        b += R(x, 40, 158, 70, LORG if asia else LBLUE, ORG if asia else BLUE)
        b += T(x + 79, 66, z, 14, INK, "middle", "600")
        for d in range(v):
            b += DOT(x + 79 - (v - 1) * 13 + d * 26, 90, 9, DARK)
    b += T(20, 140, "아시아·오세아니아 2자리 중 최소 1자리는 아시아", 15, INK, weight="600")
    b += T(20, 166, "OQT 1(보편성): 최근 두 올림픽 5인제 농구 미출전 NOC만 — 한국 여자 5인제가 도쿄 2020에 출전해 한국은 대상 아님", 13, MUTE)
    b += T(20, 188, "그 밖: OQT 2(랭킹) 2자리 · Q-시리즈 2자리(도쿄·상하이 2028.05)", 13, MUTE)
    return fig(f"bk3-{g}", 700, 200, f"3x3 {n} NOC 랭킹 배정", "NOC 랭킹 직행 5자리의 권역 배정과 보편성 예선 참가 조건.",
               b, f"<b>3×3 랭킹 직행 ({n})</b> · 국내 상위 20명의 개인 랭킹 포인트 합으로 NOC 순위를 정합니다(2026.12.01·2027.12.01 이전 12개월씩).")


def volley(g):
    n = "남자" if g == "men" else "여자"
    b = T(20, 26, f"2027 FIVB {n} 월드컵 32팀 구성", 15, MUTE)
    segs = [("개최국", 1, "#fff", LINE), ("2025 세계챔피언", 1, "#fff", LINE), ("2026 대륙선수권 상위 3팀 × 5", 15, LBLUE, BLUE), ("세계랭킹", 15, LTEAL, TEAL)]
    x = 20
    for lab, v, f, s in segs:
        w = v * 20
        b += R(x, 40, w - 3, 46, f, s, 2) + T(x + w / 2, 69, f"{v}", 15, INK, "middle", "600")
        x += w
    b += T(20, 106, "개최국", 12, MUTE) + T(42, 120, "세계챔피언", 12, MUTE) + T(210, 106, "대륙선수권 상위 3팀 × 5대륙 = 15", 12.5, MUTE, "middle") + T(510, 106, "세계랭킹 = 15", 12.5, MUTE, "middle")
    kor = ("한국 남자: AVC 3위 → 대륙 몫으로 출전 확정" if g == "men" else "한국 여자: AVC 8강 탈락 → 세계랭킹 15자리 경쟁")
    b += R(20, 136, 640, 36, LORG, ORG) + T(36, 160, kor, 15, INK, weight="600")
    b += T(20, 202, "→ 월드컵 상위 3팀 LA28 · 남은 3자리는 2028 VNL 예선 종료 뒤 세계랭킹 (확보팀 없는 대륙 우선)", 14, INK)
    return fig(f"vv-{g}", 680, 218, f"배구 {n} 월드컵 구성", "2027 월드컵 32팀은 개최국 1, 세계챔피언 1, 대륙선수권 상위 3팀 15, 세계랭킹 15로 구성되며 상위 3팀이 LA28에 출전한다.",
               b, f"<b>2027 월드컵 ({n})</b> · {('2027.09.10–26 폴란드' if g == 'men' else '2027.08.20–09.05 미국·캐나다')}. 원문은 '최종 순위 상위 3팀'으로 적으며, 이미 출전권이 있는 팀이 들면 NOC당 1팀 상한 때문에 다음 순위로 넘어가는 것으로 읽힙니다.")


# ---------------------------------------------------------------- 보정
COMMON_NOTE_OLD = "IOC PDF 링크 중 이번 편집에서 원문을 불러오지 못한 문서는 기존 사이트 요약을 사용했습니다."
COMMON_NOTE_NEW = "IOC 게시 규정 PDF는 2026.10.04에 전문을 확인했습니다."
SNAP = '<p class="snapshot">{}</p>'


SPORTS = [("olfootball", "축구"), ("olbaseball", "야구·소프트볼"), ("olbasketball", "농구"), ("olvolleyball", "배구"),
          ("olhockey", "필드하키"), ("olflagfootball", "플래그풋볼"), ("olrugby", "7인제 럭비"), ("olhandball", "핸드볼"),
          ("olwaterpolo", "수구"), ("olcricket", "크리켓"), ("ollacrosse", "라크로스")]
NAV_CSS = (".sportnav{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;margin:0 0 22px}"
           ".sportnav a[aria-current]{color:#202122;font-weight:700}@media print{.sportnav{display:none}}")


def sportnav(cur):
    links = "".join(f'<a href="{f}.html"' + (' aria-current="page"' if f == cur else "") + f'>{n}</a>' for f, n in SPORTS)
    return f'<nav class="sportnav" aria-label="단체 구기종목">{links}</nav>'


def set_sportnav(name, t):
    nav = sportnav(name)
    if '<nav class="sportnav"' in t:
        return re.sub(r'<nav class="sportnav"[\s\S]*?</nav>', lambda m: nav, t, count=1)
    if ".sportnav{" not in t:
        t = t.replace("</style>", NAV_CSS + "</style>", 1)
    return t.replace('<main id="main">', '<main id="main">' + nav, 1)


def insert_before_refline(t, sec_id, block):
    i = t.index(f'<h2 id="{sec_id}">')
    j = t.index('<p class="refline">', i)
    return t[:j] + block + t[j:]


def append_after_summary_note(t, panel, text):
    i = t.index(f'<h2 id="{panel}-summary">')
    j = t.index('<div class="asia-focus">', i)
    return t[:j] + SNAP.format(text) + t[j:]


def add_css(t):
    return t.replace("</style>", CSS + "</style>", 1) if ".figx{" not in t else t


def alias(t, tab, panels):
    """메인 파일을 tab 기본 선택본으로 변환"""
    first = panels[0]
    for p in panels:
        on = p == tab
        t = re.sub(rf'(<button id="tab-{p}" role="tab" aria-controls="panel-{p}") aria-selected="(true|false)" tabindex="-?\d"',
                   rf'\1 aria-selected="{"true" if on else "false"}" tabindex="{0 if on else -1}"', t)
        t = re.sub(rf'(<section id="panel-{p}" role="tabpanel" aria-labelledby="tab-{p}") ?(hidden)?>',
                   rf'\1 {"" if on else "hidden"}>', t)
    for s in ["summary", "asia", "oqt", "others"]:
        t = t.replace(f'<a data-section="{s}" href="#{first}-{s}">', f'<a data-section="{s}" href="#{tab}-{s}">')
    return t


def fix(name, t):
    t = set_sportnav(name, add_css(t).replace(COMMON_NOTE_OLD, COMMON_NOTE_NEW))
    if name == "olflagfootball":
        t = t.replace('<li><a href="https://en.wikipedia.org/wiki/Handball_at_the_2024_Summer_Olympics_%E2%80%93_Men%27s_qualification">형식 참고 · 핸드볼 올림픽 예선</a></li>',
                      '<li><a href="https://en.wikipedia.org/wiki/2026_IFAF_Men%27s_Flag_Football_World_Championship">Wikipedia · 2026 IFAF 남자 세계선수권</a></li><li><a href="https://en.wikipedia.org/wiki/2026_IFAF_Women%27s_Flag_Football_World_Championship">Wikipedia · 2026 IFAF 여자 세계선수권</a></li>')
        for g in ["men", "women"]:
            t = insert_before_refline(t, f"{g}-oqt", qseries_flag(g))
    elif name == "olfootball":
        t = t.replace(COMMON_NOTE_NEW, "축구는 IOC 게시 PDF가 아니라 FIFA 회람(2026.02.04)과 AFC·JFA 발표를 기준으로 했습니다.")
        t = insert_before_refline(t, "men-oqt", football_m())
        t = insert_before_refline(t, "women-oqt", football_w())
        t = append_after_summary_note(t, "men", "참고(아시안게임, LA28 예선 아님): 한국 남자는 2026 아시안게임 결승에서 일본을 꺾고 4회 연속 우승했습니다.")
    elif name == "olhockey":
        for g in ["men", "women"]:
            t = insert_before_refline(t, f"{g}-oqt", hockey(g))
    elif name == "olrugby":
        for g in ["men", "women"]:
            t = insert_before_refline(t, f"{g}-oqt", rugby(g))
        t = t.replace('<p class="note">도표는 기본 1+4+6+1 배정입니다. 지역 직행 자리의 이전이 발생하면 지역 예선 선발 수가 줄고 리페차지 선발 수가 늘어납니다.</p>\n <div class="asia-focus"><h2 id="men-asia">',
                      '<p class="note">도표는 기본 1+4+6+1 배정입니다. 지역 직행 자리의 이전이 발생하면 지역 예선 선발 수가 줄고 리페차지 선발 수가 늘어납니다.</p><p class="snapshot">참고(아시안게임, LA28 예선 아님): 한국 남자는 2026 아시안게임 준결승에서 홍콩에 14–35, 3위 결정전에서 일본에 5–17로 져 4위였습니다.</p>\n <div class="asia-focus"><h2 id="men-asia">', 1)
    elif name == "olhandball":
        t = t.replace('<a class="brand" href="https://koreaolympics.github.io/">', '<a class="brand" href="https://koreaolympics.github.io/index1.html">')
        t = t.replace("<h3>누가 참가하나? — 2024년 규정을 동일하게 적용한다면</h3>", "<h3>누가 참가하나? — LA28 규정 D.3·D.7</h3>")
        t = t.replace('<p class="note">아래는 파리 2024의 선발 방식을 LA28에 적용해 설명한 가정입니다. 2024년의 실제 대륙별 배정 수나 참가국을 2028년 확정 결과로 옮긴 것은 아닙니다.</p>',
                      '<p class="note">아래 편성은 LA28 규정(D.3 남자·D.7 여자)이 직접 정한 방식입니다. 파리 2024 사례는 이해를 돕는 참고일 뿐, 2028년 대륙별 배정 결과가 아닙니다.</p>')
        for g in ["men", "women"]:
            i = t.index(f'<h2 id="{g}-oqt">')
            j = t.index("<h3>", i)
            t = t[:j] + handball(g) + t[j:]
    elif name == "olbasketball":
        t = insert_before_refline(t, "men-oqt", bk_men())
        t = insert_before_refline(t, "women-oqt", bk_women())
        for g in ["men3", "women3"]:
            t = insert_before_refline(t, f"{g}-oqt", bk_3x3(g))
        t = t.replace("한국은 남녀 5인제 출전 이력과 FIBA의 성별 적용 규정을 확인한 뒤 참가 가능성을 판단해야 합니다.",
                      "원문은 '(남자 또는 여자)' 5인제에 최근 두 올림픽 출전 이력이 없는 NOC로 정합니다. 한국 여자 5인제가 도쿄 2020에 출전했으므로 NOC 단위로 읽으면 한국은 남녀 모두 OQT 1 대상이 아닙니다.")
        t = append_after_summary_note(t, "men", "참고(아시안게임, LA28 예선 아님): 한국은 2026 아시안게임 남녀 5인제 금, 3×3 남자 금·여자 동을 땄습니다.")
    elif name == "olvolleyball":
        for g in ["men", "women"]:
            t = insert_before_refline(t, f"{g}-oqt", volley(g))
        t = t.replace("월드컵 ‘전체 3위’가 아니라 이미 올림픽에 진출한 팀을 제외한 상위 3팀</strong> 이 기준입니다.",
                      "최종 순위 상위 3팀</strong>이 출전권을 받습니다. 원문에 '미확보 팀' 문구는 없지만, NOC당 1팀 상한 때문에 이미 확보한 팀이 들면 다음 순위로 넘어가는 것으로 읽힙니다.")
        t = t.replace("월드컵 ‘전체 3위’가 아니라 이미 올림픽에 진출한 팀을 제외한 상위 3팀 이 기준입니다.",
                      "최종 순위 상위 3팀이 출전권을 받습니다. 원문에 '미확보 팀' 문구는 없지만, NOC당 1팀 상한 때문에 이미 확보한 팀이 들면 다음 순위로 넘어가는 것으로 읽힙니다.")
        t = t.replace("선수의 최소 출전 횟수와 랭킹 자격 등 참가 조건을 별도로 충족해야 합니다.",
                      "이미 출전권을 얻은 선수와 2자리를 채운 NOC는 참가할 수 없습니다(규정 D.1).")
        t = append_after_summary_note(t, "men", "한국 남자: 2026 AVC 선수권 3위(준결승 일본 0–3, 3위전 호주 3–2)로 2027 월드컵 출전권을 얻었습니다.")
        t = append_after_summary_note(t, "women", "한국 여자: 2026 AVC 선수권 8강에서 태국에 0–3으로 져 대륙 몫 월드컵 출전권을 얻지 못했습니다(세계랭킹 28위).")
    return t


FILES = {
    "olflagfootball": ("a81b2311-olflagfootball.html", ["men", "women"], {"olflagfootball-men": "men", "olflagfootball-women": "women"}),
    "olfootball": ("20beadf2-olfootball.html", ["men", "women"], {}),
    "olhockey": ("efddf629-olhockey.html", ["men", "women"], {"olhockey-men": "men", "olhockey-women": "women"}),
    "olrugby": ("bf846a29-olrugby.html", ["men", "women"], {"olrugby-men": "men", "olrugby-women": "women"}),
    "olhandball": ("71cbcca5-olhandball.html", ["men", "women", "rules"], {"olhandball-men": "men", "olhandball-women": "women"}),
    "olbasketball": ("481a83d1-olbasketball.html", ["men", "women", "men3", "women3"], {"olbasketball-men": "men", "olbasketball-women": "women", "olbasketball-3x3": "men3"}),
    "olvolleyball": ("e89a81f6-olvolleyball.html", ["men", "women", "menbeach", "womenbeach"], {"olvolleyball-indoor": "men", "olvolleyball-beach": "menbeach"}),
}

if __name__ == "__main__":
    for name, (src, panels, aliases) in FILES.items():
        t = open(UP + src, encoding="utf-8").read()
        t = fix(name, t)
        open(OUT + name + ".html", "w", encoding="utf-8", newline="\r\n").write(t)
        print("wrote", name, len(t))
        for an, tab in aliases.items():
            open(OUT + an + ".html", "w", encoding="utf-8", newline="\r\n").write(alias(t, tab, panels))
            print("  alias", an, tab)
