# -*- coding: utf-8 -*-
"""체급 종목 체급별 LA28 예선 규정 (표 + 좌석 그림).
근거(IOC 게시 PDF): 유도 IJF 2026.05.12 · 태권도 WT 2026.05.12 · 역도 IWF 2026.05.12 · 레슬링 UWW 2026.08.13 · 복싱 World Boxing 2026.08.05"""
import html as H

BASE = "https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/"
PDF = {"judo": (BASE + "JUD-LA28-Qualification-System.pdf", "IJF", "2026.05.12"),
       "taekwondo": (BASE + "TKW-LA28-Qualification-System.pdf", "WT", "2026.05.12"),
       "weightlifting": (BASE + "WLF-LA28-Qualification-System.pdf", "IWF", "2026.05.12"),
       "wrestling": (BASE + "WRE-LA28-Qualification-System.pdf", "UWW", "2026.08.13"),
       "boxingw": (BASE + "BOX-LA28-Qualification-System.pdf", "World Boxing", "2026.08.05")}

COL = {"rank": ("#2454a6", "#2454a6"), "gs": ("#6f8fd1", "#6f8fd1"), "cont": ("#b9734f", "#b9734f"), "wq": ("#267b76", "#267b76"),
       "wq2": ("#7fb3ae", "#7fb3ae"), "host": ("#72777d", "#72777d"), "univ": ("#c8ccd1", "#a2a9b1"), "pool": ("#fff", "#54595d")}

# 유도 개인 체급 → 혼성 단체 체급
JUD_MIX = {"m60": ["남 -73kg"], "m66": ["남 -73kg"], "m73": ["남 -73kg", "남 -90kg"], "m81": ["남 -90kg"], "m90": ["남 -90kg", "남 +90kg"],
           "m100": ["남 +90kg"], "mo100": ["남 +90kg"], "w48": ["여 -57kg"], "w52": ["여 -57kg"], "w57": ["여 -57kg", "여 -70kg"],
           "w63": ["여 -70kg"], "w70": ["여 -70kg", "여 +70kg"], "w78": ["여 +70kg"], "wo78": ["여 +70kg"]}

# 복싱 체급별 배정 (규정 Table 1·2): 세계선수권, 대륙 예선 합, WQ1, WQ2(최소,최대), 개최국(최소,최대), 보편성, 정원
BOX = {"w51": (4, 8, 2, (2, 3), (0, 1), 1, 18), "w54": (4, 8, 2, (2, 3), (0, 1), 1, 18), "w57": (4, 8, 4, (2, 3), (0, 1), 1, 20),
       "w60": (4, 8, 2, (2, 3), (0, 1), 1, 18), "w65": (2, 8, 4, (4, 4), (0, 0), 0, 18), "w70": (2, 8, 4, (2, 2), (0, 0), 0, 16),
       "w75": (2, 8, 4, (2, 2), (0, 0), 0, 16), "m55": (4, 8, 2, (2, 3), (0, 1), 1, 18), "m60": (4, 8, 2, (2, 3), (0, 1), 1, 18),
       "m65": (4, 8, 4, (2, 3), (0, 1), 1, 20), "m70": (4, 8, 4, (2, 3), (0, 1), 1, 20), "m80": (2, 8, 4, (2, 2), (0, 0), 0, 16),
       "m90": (2, 8, 4, (2, 2), (0, 0), 0, 16), "mo90": (2, 8, 4, (2, 2), (0, 0), 0, 16)}


def e(s):
    return H.escape(str(s), quote=True)


# ------------------------------------------------------------------ 좌석 그림
def seat_svg(title, segs, total_txt, small=False):
    """segs: [(label, n_fixed, n_dashed, kind)] ; kind 'pool' → '+ 공용 풀' 상자 하나"""
    s, gap, per = (18, 4, 20) if small else (24, 5, 20)
    x0, y0 = 10, 34
    cells = []
    for lab, n, extra, kind in segs:
        if kind != "pool":
            cells += [(kind, k >= n) for k in range(n + extra)]
    rows_ = max(1, (len(cells) + per - 1) // per)
    w_cells = min(len(cells), per) * (s + gap)
    has_pool = any(k == "pool" for *_, k in segs)
    pool_w = 110 if has_pool else 0
    W = max(x0 + w_cells + pool_w + 14, 560)
    lrows = (len(segs) + 2) // 3
    Hh = y0 + rows_ * (s + gap) + 14 + lrows * 22 + 4
    b = (f'<text x="{x0}" y="20" font-size="14" font-weight="700" fill="#202122">{e(title)}</text>'
         f'<text x="{W - 10}" y="20" font-size="13" text-anchor="end" fill="#54595d">{e(total_txt)}</text>')
    for idx, (kind, dashed) in enumerate(cells):
        r, c = divmod(idx, per)
        x, y = x0 + c * (s + gap), y0 + r * (s + gap)
        fill, stroke = COL[kind]
        if dashed:
            b += f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="3" fill="#fff" stroke="{stroke}" stroke-width="1.6" stroke-dasharray="3 2"/>'
        else:
            b += f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="3" fill="{fill}" stroke="{stroke}"/>'
    if has_pool:
        px = x0 + w_cells + 6
        b += (f'<rect x="{px}" y="{y0}" width="{pool_w - 12}" height="{s}" rx="3" fill="#fff" stroke="#54595d" stroke-width="1.4" stroke-dasharray="4 3"/>'
              f'<text x="{px + (pool_w - 12) / 2:.0f}" y="{y0 + s * 0.7:.0f}" font-size="12" text-anchor="middle" fill="#202122">+ 공용 풀</text>')
    ly = y0 + rows_ * (s + gap) + 16
    for j, (lab, n, extra, kind) in enumerate(segs):
        r, c = divmod(j, 3)
        x, y = x0 + c * ((W - 20) / 3), ly + r * 22
        fill, stroke = COL[kind]
        dash = ' stroke-dasharray="3 2"' if (kind == "pool" or (extra and not n)) else ""
        cnt = "변동" if kind == "pool" else (f"{n}–{n + extra}" if extra and n else (f"0–{extra}" if extra else str(n)))
        b += (f'<rect x="{x:.0f}" y="{y - 10}" width="12" height="12" rx="2" fill="{"#fff" if dash else fill}" stroke="{stroke}"{dash}/>'
              f'<text x="{x + 17:.0f}" y="{y}" font-size="12" fill="#202122">{e(lab)} <tspan font-weight="700">{cnt}</tspan></text>')
    cap = "" if small else '<figcaption>칸 하나가 출전권 1장입니다. 점선 칸은 결과나 다른 경로 사용 여부에 따라 생기는 자리, 「공용 풀」은 체급을 가리지 않고 나눠 쓰는 자리입니다.</figcaption>'
    return (f'<figure class="seat"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {Hh:.0f}" role="img" aria-label="{e(title)}">'
            f'<g font-family="Arial, Malgun Gothic, sans-serif">{b}</g></svg>{cap}</figure>')


# ------------------------------------------------------------------ 종목별 규정
def segs(key, code):
    if key == "judo":
        return [("IJF 랭킹 직행", 17, 0, "rank"), ("개최국", 1, 0, "host"), ("대륙·혼성 초청·보편성", 0, 0, "pool")]
    if key == "taekwondo":
        return [("올림픽 랭킹", 5, 0, "rank"), ("그랜드슬램", 1, 0, "gs"), ("대륙 예선", 9, 0, "cont"), ("개최국 또는 보편성", 1, 0, "host")]
    if key == "weightlifting":
        return [("OQR 랭킹", 8, 0, "rank"), ("대륙 대표", 1, 0, "cont"), ("개최국 또는 보편성", 1, 0, "host")]
    if key == "wrestling":
        return [("2027 세계선수권 메달", 4, 0, "rank"), ("UWW 랭킹", 3, 0, "gs"), ("대륙 예선 4개 × 2", 8, 0, "cont"), ("세계 예선", 1, 0, "wq")]
    if key == "boxingw":
        wc, ct, q1, (a2, b2), (ha, hb), un, tot = BOX[code]
        out = [("2027 세계선수권", wc, 0, "rank"), ("대륙 예선 5개", ct, 0, "cont"), ("세계 예선 1", q1, 0, "wq"), ("세계 예선 2", a2, 0, "wq2")]
        if hb:
            out.append(("개최국 또는 세계 예선 2", 0, 1, "host"))
        if un:
            out.append(("보편성", un, 0, "univ"))
        return out


def total(key, code):
    if key == "boxingw":
        return f"{BOX[code][6]}명"
    return {"judo": "최소 18명 + 공용 풀", "taekwondo": "16명", "weightlifting": "10명", "wrestling": "16명"}[key]


def _g(code):
    return "남자" if code[0] == "m" or code[:2] in ("fs", "gr") else "여자"


def rows(key, code):
    g = _g(code)
    if key == "judo":
        return [("직행 · IJF 올림픽 랭킹", "<b>17명</b>", "랭킹 기간(2026.06.15–2028.06.12) 최종 랭킹 체급 상위 17명. NOC당 체급 1명 — 같은 국가 선수가 여럿이면 NOC가 선택", "D.1.1"),
                ("개최국 (미국)", "1명", "미국에 체급마다 1명 보장", "D.2"),
                ("대륙 쿼터", "변동", f"{g} 52명 공용 풀(아프리카 12·유럽 13·<b>아시아 12</b>·오세아니아 4·아메리카 11). 대륙 랭킹(전 체급·성별 통합 점수)순, NOC당 전체 1명", "D.1.2"),
                ("혼성 단체 초청", "변동", "전체 6명 공용. 혼성 6개 체급 중 5개만 채운 국가에 빠진 체급 1명(대륙별 1 + 혼성 랭킹 1)", "D.1.3"),
                ("보편성", "변동", "전체 10명 공용(체급·성별 무관). 신청 2027.10.01–2028.01.15", "D.3")]
    if key == "taekwondo":
        return [("WT 올림픽 랭킹", "<b>5명</b>", "2028.01 공표 랭킹(2027 GP 파이널 반영) 체급 상위 5명", "D.1"),
                ("WT 그랜드슬램 챔피언스 시리즈", "1명", "2027 시리즈 후 메리트 포인트 1위. 이미 랭킹으로 확보했으면 2위까지만", "D.2"),
                ("대륙 예선 (2028.02–04)", "9명", "아프리카 2·<b>아시아 2</b>·유럽 2·팬암 2·오세아니아 1. 랭킹·GS로 성별 2장 이상 얻은 NOC는 불참", "D.3"),
                ("개최국 또는 보편성", "1명", "미국 성별 2장(체급 지정 2027.09.30) · 보편성 성별 2장 중 이 체급 몫", "D.4·D.5")]
    if key == "weightlifting":
        return [("IWF 올림픽 예선 랭킹 (OQR)", "<b>8명</b>", "2026.07.27–2028.05.07. 1기 최고 합계 3회 + 2기 최고 합계 2회 점수로 체급 상위 8명(NOC당 체급 1명)", "D.1"),
                ("OQR 대륙 대표", "1명", "상위 8명 안에 없는 대륙의 최상위 선수 1명. 모든 대륙이 이미 있으면 같은 체급 다음 순위", "D.2"),
                ("개최국 또는 보편성", "1명", f"미국 {g} 3장 + 보편성 {g} 3장을 6개 체급에 배분(체급 정원 10명)", "D.3·D.4")]
    if key == "wrestling":
        return [("1단계 · 2027 세계선수권 (라스베이거스, 2027.09.11–19)", "<b>4명</b>", "체급 메달리스트 4명(금·은·동·동)의 NOC", "D.1.1"),
                ("2단계 · UWW 랭킹", "3명", "1단계 미확보 랭킹 상위 3명. 대륙선수권·랭킹 시리즈·세계선수권 7개 대회 중 최고 5개 성적", "D.1.2"),
                ("3단계 · 대륙 예선 (2028.03–04)", "8명", "아시아·유럽·팬암·아프리카+오세아니아 예선 각 상위 2명. <b>아시아 예선 2028.04.14–16</b>", "D.1.3"),
                ("4단계 · 세계 예선 (2028.05.18–21)", "1명", "앞 단계에서 한 장도 못 딴 NOC만 출전(전 스타일 합쳐 최대 2명). 체급 1위", "D.1.4")]
    if key == "boxingw":
        wc, ct, q1, (a2, b2), (ha, hb), un, tot = BOX[code]
        r = [("2027 세계선수권 (아스타나, 2027.04)", f"<b>{wc}명</b>", "체급 상위 입상자, NOC 체급 1명", "D.1"),
             ("대륙 예선 5개 (2027–28)", f"{ct}명", "아프리카 1·<b>아시아 2</b>·유럽 2·오세아니아 1·팬암 2. 세계선수권에서 이 체급을 딴 NOC는 불참", "D.1"),
             ("세계 예선 1 (2028)", f"{q1}명", "앞 대회에서 이 체급 출전권이 없는 NOC", "D.1"),
             ("세계 예선 2 (2028)", f"{a2}–{b2}명" if b2 != a2 else f"{a2}명", "개최국이 이 체급을 쓰지 않으면 1장 늘어남" if b2 != a2 else "앞 대회에서 이 체급 출전권이 없는 NOC", "D.1")]
        if hb:
            r.append(("개최국 (미국)", "0–1명", f"미국 {g} 최대 3장을 이 성별 앞 4개 체급 중에서 지정", "D.2"))
        if un:
            r.append(("보편성", f"{un}명", f"{g} 4장은 앞 4개 체급에 1장씩", "D.3"))
        return r


def notes(key, code):
    if key == "judo":
        mix = ", ".join(JUD_MIX.get(code, []))
        return ["모든 경로는 하나의 IJF 올림픽 랭킹으로 정해지며, IJF가 2028.06.15 통보 → NOC 확인 06.22 → 재배정 06.23.",
                "직행 자리를 쓰지 않으면 <b>같은 체급</b> 차순위(대륙 무관)에게, 대륙 쿼터 자리는 같은 대륙 차순위(체급 무관)에게 넘어갑니다(F.1).",
                f"혼성 단체에서 이 체급 선수가 나갈 수 있는 체급: <b>{mix}</b>.", "출전 연령: 2013.12.31 이전 출생(C.1)."]
    if key == "taekwondo":
        return ["쿼터는 <b>NOC</b>에 배정되고 선수는 NOC가 정합니다. 단, 랭킹으로 딴 자리에는 WT 올림픽 랭킹 20위 안에 든 적이 있는 선수만 나갈 수 있습니다(C.3).",
                "NOC는 랭킹·그랜드슬램으로 성별 최대 4장, 대륙 예선으로 성별 최대 2장(체급당 1명)을 얻을 수 있습니다(B.2).",
                "대륙 예선 자리를 쓰지 않으면 같은 대회 같은 체급 차순위에게 넘어갑니다(F.1).",
                "출전 연령: 2011.12.31 이전 출생 · 국기원 단증 · WT 글로벌 선수 라이선스 필요(C.1·C.2)."]
    if key == "weightlifting":
        return ["쿼터는 선수 이름으로 배정되고, NOC는 성별 최대 3명(체급당 1명)입니다. 기간 최고 역사(Best Lifter) 국가는 1장 추가(B.2).",
                "IWF가 2028.05.29 최종 OQR 공표·통보 → NOC 확인 06.05. 쓰지 않는 자리는 같은 체급 차순위(대륙 대표 자리는 미대표 대륙 우선)에게(F.1).",
                "출전 연령: 2013.12.31 이전 출생. 예선 대회 3개월 전 명단 제출과 도핑 검사 소재지 의무를 지켜야 합니다(C.2)."]
    if key == "wrestling":
        return ["쿼터는 <b>NOC</b>에 배정됩니다. 개최국 자리는 없고, 보편성 자리는 재배정 과정에서만 생깁니다(D.2·D.3).",
                "1·3단계에서 확보한 체급에는 같은 NOC가 다른 선수를 다시 내보낼 수 없습니다(D.1.3).",
                "출전 연령: 2010.12.31 이전 출생(C.1)."]
    if key == "boxingw":
        return ["쿼터는 선수 이름으로 배정되며, 예선 기간은 2027.04.01–2028.05.31입니다. 개최국·보편성 선수도 예선 대회에 한 번 이상 나가야 합니다(C.2).",
                "대륙 예선은 체급에 4명 이상 출전하고 1위가 1승 이상 거둬야 유효합니다(D.1).",
                "출전 연령: 1988.01.01–2009.12.31 출생(C.1)."]
    return []


def table(key, code, label):
    body = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows(key, code))
    src, org, ver = PDF[key]
    return (f'<table class="data wrule"><caption>{label} · LA28 예선 규정 ({org} {ver}판)</caption><thead><tr><th scope="col">경로</th>'
            f'<th scope="col">이 체급 인원</th><th scope="col">선발 방식</th><th scope="col">규정</th></tr></thead><tbody>{body}</tbody>'
            f'<tfoot><tr><th scope="row">체급 합계</th><td>{total(key, code)}</td><td colspan="2"></td></tr></tfoot></table>')


def figure(key, code, label, small=False):
    return seat_svg(f"{label} 출전권 구성", segs(key, code), total(key, code), small)


def rule_html(key, code, label):
    if key == "judo" and code == "xteam":
        rows_ = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td></tr>" for a, b in [
            ("여 -57kg", "-48 · -52 · -57kg"), ("여 -70kg", "-57 · -63 · -70kg"), ("여 +70kg", "-70 · -78 · +78kg"),
            ("남 -73kg", "-60 · -66 · -73kg"), ("남 -90kg", "-73 · -81 · -90kg"), ("남 +90kg", "-90 · -100 · +100kg")])
        return ('<table class="data wrule"><caption>혼성 단체 체급 구성 (IJF 규정 D)</caption><thead><tr><th scope="col">혼성 체급</th><th scope="col">출전 가능한 개인 체급</th></tr></thead>'
                f'<tbody>{rows_}</tbody></table>'
                '<ul class="wnotes"><li>별도 쿼터는 없습니다. 개인전 출전 선수로 혼성 6개 체급을 모두 채운 NOC가 출전합니다(성별 최대 7명).</li>'
                '<li><b>혼성 단체 초청 6명</b>: 5개 체급만 채운 국가 중 대륙별 혼성 랭킹 최상위 1개국 + 혼성 세계랭킹 최상위 1개국에 빠진 체급 1명(D.1.3).</li>'
                '<li>개최국 미국은 혼성 단체 출전권을 받습니다(D.2).</li></ul>')
    return figure(key, code, label) + table(key, code, label) + '<ul class="wnotes">' + "".join(f"<li>{n}</li>" for n in notes(key, code)) + "</ul>"


def rule_pdf(key):
    return PDF[key][0]


def src_title(key):
    src, org, ver = PDF[key]
    return f"{org} · LA28 Qualification System (IOC 게시 PDF, {ver}판)"


CSS = (".wrule caption{font-weight:600}.wrule th:first-child{width:28%}.wrule td:nth-child(2){white-space:nowrap;width:13%}.wnotes{font-size:14px;margin:6px 0 4px}"
       ".wclass{border-top:1px solid #eaecf0;margin-top:16px;padding-top:2px}.wclass h3{margin:12px 0 6px}.wclass .kor{font-size:14px;margin:6px 0}"
       ".seat{margin:10px 0 14px;padding:10px 12px;background:#f8f9fa;border:1px solid #eaecf0}.seat svg{display:block;width:100%;max-width:640px;height:auto}"
       ".seat figcaption{font-size:12px;color:#54595d;margin-top:6px}.wclass .seat{padding:8px 10px}.wclass .seat svg{max-width:560px}"
       ".golf-nav.sub-nav{margin-top:-20px;margin-bottom:20px;border-bottom:1px solid #eaecf0}.golf-nav.sub-nav a{padding:6px 11px;font-size:13px}"
       ".golf-nav.sub-nav .sub-label{padding:6px 11px 6px 0;color:#54595d;font-size:12px;font-weight:700;align-self:center}"
       "@media(max-width:600px){.seat{overflow-x:auto}.seat svg{min-width:520px}.wclass .seat svg{min-width:480px}.golf-nav.sub-nav{margin-top:-12px}}")
