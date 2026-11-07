"""사설(비공식) 올림픽 예선 랭킹 집계 사이트에서 랭킹을 받아 온다.

    python tools/private_rankings.py                # 등록된 곳 목록
    python tools/private_rankings.py render         # 받아 둔 자료로 허브 표만 다시 그린다 (인터넷 없이)
    python tools/private_rankings.py totalintel     # 역도: totalintel.org 체급별 잠정 OQR 상위 10위 → data/private-rankings/totalintel.json

- 등록부는 data/private-rankings.json (사이트·종목·읽는 방법·robots.txt 확인 결과). 새 곳은 거기에 적고 아래 READERS에 읽는 함수를 더한다.
- 사이트의 robots.txt를 지킨다: 허용된 공개 페이지만 읽고, 금지된 경로(예: totalintel의 /api/)는 쓰지 않는다.
  페이지 사이에 쉬어 한 번에 몇 장만 읽는다. 출처 링크를 함께 남긴다.
- 공식 순위가 아니다. 국제연맹(IWF 등)의 공식 랭킹이 나오면 그쪽이 우선이다.
"""
import datetime as dt, html, json, re, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'data/private-rankings.json'
OUT = ROOT / 'data/private-rankings'
UA = 'KoreaOlympicsSiteBot/1.0 (+https://koreaolympics.github.io)'
KST = dt.timezone(dt.timedelta(hours=9))


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8')


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


# ── totalintel.org (역도 LA28 잠정 OQR) ─────────────────────────────

def ko_name(name):
    """'Iseul KIM' → 한글 (data/korean-names.json에 있으면 그것, 없으면 로마자에서 옮김)."""
    import korean_names as kn
    parts = name.split()
    sur = [p for p in parts if p.isupper() and len(p) > 1]
    given = [p for p in parts if p not in sur]
    if not sur or not given:
        return name
    rom = f'{sur[0].title()} {"-".join(given)}'
    d = kn.load()
    return d['names'].get(rom) or kn.guess(rom) or name


TOP = 10  # 출전권은 체급별 상위 8명 + 대륙 1명이라 10위까지만 받는다
TI_CATS = {'F53': '여자 53kg', 'F61': '여자 61kg', 'F69': '여자 69kg', 'F77': '여자 77kg', 'F86': '여자 86kg', 'F86P': '여자 +86kg',
           'M65': '남자 65kg', 'M75': '남자 75kg', 'M85': '남자 85kg', 'M95': '남자 95kg', 'M110': '남자 110kg', 'M110P': '남자 +110kg'}


def totalintel(src):
    base = src['url'].rstrip('/')
    out = {}
    for code, label in TI_CATS.items():
        url = f'{base}/c/{code}'
        page = get(url)
        rows = []
        tb = re.search(r'<table>.*?<th>Rank</th>.*?<tbody>(.*?)</tbody>', page, re.S)
        for tr in re.findall(r'<tr>(.*?)</tr>', tb.group(1) if tb else '', re.S):
            td = re.findall(r'<td>(.*?)</td>', tr, re.S)
            if len(td) < 4:
                continue
            nat = re.search(r'\(([A-Z]{3})\s*·\s*([A-Z]{2})\)', td[2])
            link = re.search(r'href="([^"]+)"', td[1])
            rank = text(td[0])
            rows.append({'rank': int(re.sub(r'\D', '', rank) or 0), 'tie': rank.startswith('='), 'name': text(td[1]), 'noc': nat.group(1) if nat else '',
                         'continent': nat.group(2) if nat else '', 'points': float(re.sub(r'[^\d.]', '', text(td[3])) or 0),
                         'url': base + link.group(1) if link else ''})
        lead = [text(p) for p in re.findall(r'<p>(.*?)</p>', page, re.S)]
        pending = not rows and 'Standings will appear once results are recorded' in page
        cut = next((r['points'] for r in rows if r['rank'] == 8), None)  # 8위 점수 (출전권 기준선)
        kor = [{**r, 'ko': ko_name(r['name']), 'gap8': round(cut - r['points'], 1) if cut is not None else None,
                'in8': r['rank'] <= 8} for r in rows if r['noc'] == 'KOR']
        rows = [r for r in rows if r['rank'] <= TOP]
        out[code] = {'label': label, 'url': url, 'rows': rows, 'korea': kor, 'cut8': cut, 'status': '결과 기록 전' if pending else '',
                     'continental': next((p for p in lead if p.startswith('One continental place')), '')}
        print(f'  {label}: ' + ('결과 기록 전' if pending else f'상위 {len(rows)}명, 8위 {cut:g}점') +
              ''.join(f' · 한국 {r["rank"]}위 {r["ko"]} {r["points"]:g}점' + (' (8위 안)' if r['in8'] else f' (8위와 {r["gap8"]:g}점 차)') for r in kor))
        time.sleep(src.get('delay', 2))
    return out


READERS = {'totalintel': totalintel}
HUBS = {'totalintel': 'olweightlifting'}  # 허브에 한국 현황 표를 넣을 곳
BLOCK_RE = re.compile(r'<div class="private-rank" id="private-rank">.*?</div><!-- /private-rank -->\n?', re.S)
E = lambda s: html.escape(str(s), quote=True)


def hub_block(file):
    """허브 '사설 랭킹 한국 현황' 표 (data/private-rankings/<곳>.json). 자료가 없으면 ''."""
    key = next((k for k, f in HUBS.items() if f == file), None)
    p = OUT / f'{key}.json' if key else None
    if not p or not p.exists():
        return ''
    doc = json.loads(p.read_text(encoding='utf-8'))
    rows, wait = [], []
    for code, c in doc['data'].items():
        if c.get('status'):
            wait.append(c['label'])
            continue
        top8 = ', '.join(f'{r["noc"]}' for r in c['rows'] if r['rank'] <= 8)
        if not c['korea']:
            rows.append(f'<tr><th scope="row"><a href="{E(c["url"])}">{E(c["label"])}</a></th><td class="muted" colspan="4">상위 30위 안에 한국 선수 없음</td>'
                        f'<td class="c">{c["cut8"]:g}</td><td class="small">{E(top8)}</td></tr>')
        for i, r in enumerate(c['korea']):
            state = '<b class="in8">8위 안</b>' if r['in8'] else f'8위와 {r["gap8"]:g}점 차'
            rows.append(f'<tr class="{"in" if r["in8"] else "out"}"><th scope="row"><a href="{E(c["url"])}">{E(c["label"])}</a></th>'
                        f'<td class="kor"><a href="{E(r["url"])}" title="{E(r["name"])}">{E(r["ko"])}</a></td><td class="c">{"=" if r.get("tie") else ""}{r["rank"]}</td>'
                        f'<td class="c">{r["points"]:g}</td><td>{state}</td><td class="c">{c["cut8"]:g}</td><td class="small">{E(top8) if i == 0 else ""}</td></tr>')
    inn = sum(1 for c in doc['data'].values() for r in c['korea'] if r['in8'])
    return (f'<div class="private-rank" id="private-rank"><h2>잠정 OQR 한국 현황 <span class="asof">{E(doc["fetched"])} · 비공식</span></h2>'
            f'<p class="small">사설 집계 <a href="{E(doc["source"])}">{E(doc["source"].split("//")[-1])}</a>의 체급별 잠정 올림픽예선랭킹(OQR). '
            f'체급마다 상위 8명(NOC당 1명)과 대륙 배정 1명이 출전권을 받는다. 현재 한국 선수 <b>{inn}명</b>이 8위 안에 있다. '
            f'공식 순위가 아니며 출전권은 예선 기간(2028.05.07) 종료 뒤 IWF가 정한다.</p>'
            '<div class="tw"><table class="wikitable"><thead><tr><th>체급</th><th>한국 선수</th><th>순위</th><th>OQR 점수</th><th>8위와 비교</th><th>8위 점수</th><th>현재 1~8위 국가</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
            + (f'<p class="small">결과 기록 전: {E(" · ".join(wait))}</p>' if wait else '') + '</div><!-- /private-rank -->')


TI_DOC = {'F53': ('women', '53 kg', 'women53kg'), 'F61': ('women', '61 kg', 'women61kg'), 'F69': ('women', '69 kg', 'women69kg'),
          'F77': ('women', '77 kg', 'women77kg'), 'F86': ('women', '86 kg', 'women86kg'), 'F86P': ('women', '+86 kg', 'womenover86kg'),
          'M65': ('men', '65 kg', 'men65kg'), 'M75': ('men', '75 kg', 'men75kg'), 'M85': ('men', '85 kg', 'men85kg'),
          'M95': ('men', '95 kg', 'men95kg'), 'M110': ('men', '110 kg', 'men110kg'), 'M110P': ('men', '+110 kg', 'menover110kg')}
HEAVY = {'M110', 'M110P', 'F86', 'F86P'}  # 중량급: 한국 선수 정리를 사람이 정할 때까지 옛 문장을 둔다
HEAVY_OLD = {  # 중량급 종전 기재 (정리 전까지 그대로 보여 준다)
    'M110': '종전 기재 없음 · 옛 후보 진윤성, 장연학', 'M110P': '송영환, 황우만 · 옛 후보 이양재',
    'F86': '김수현, 전희수 · 옛 후보 장현주', 'F86P': '박혜정, 김효언, 임정희'}
SQUAD_RE = re.compile(r'<div class="korea-squad" id="korea-squad">.*?</div><!-- /korea-squad -->', re.S)
OQR_RE = re.compile(r'<p class="note oqr"[^>]*>.*?</p>')


def oqr_note(code, c, fetched):
    """체급 하나의 한국 현황 한 줄 (허브 체급 제목 아래·세부종목 문서 '한국 주요 선수' 아래)."""
    day = fetched[5:10].replace('-', '.')
    if c['korea']:
        who = ', '.join(f'{r["ko"]} {r["rank"]}위 {r["points"]:g}점 (' + ('8위 안' if r['in8'] else f'8위와 {r["gap8"]:g}점 차') + ')' for r in c['korea'])
    else:
        who = '상위 30위 안에 한국 선수 없음'
    return (f'<p class="note oqr" data-oqr="{code}">한국 · 잠정 OQR {day} (비공식, <a href="{E(c["url"])}">totalintel</a>): {E(who)} '
            f'· 8위 {c["cut8"]:g}점</p>')


def render_notes(doc):
    """결과가 기록된 체급: 허브의 옛 '한국 주요 선수(2026.10 현황)'·'옛 자료 후보' 문장을 OQR 한 줄로 바꾸고,
    세부종목 문서 '한국 주요 선수' 아래에도 같은 줄을 둔다. 결과 기록 전 체급은 건드리지 않는다."""
    hub = ROOT / 'olweightlifting.html'
    text = orig = hub.read_text(encoding='utf-8')
    for code, (sec, h3, ev) in TI_DOC.items():
        c = doc['data'].get(code)
        if not c or c.get('status') or code in HEAVY:
            continue
        note = oqr_note(code, c, doc['fetched'])
        m = re.search(rf'(<section id="{sec}">.*?<h3>{re.escape(h3)}</h3>\n)((?:<p class="note[^"]*"[^>]*>.*?</p>)*)', text, re.S)
        if m:
            text = text[:m.start(2)] + note + text[m.end(2):]
        p = ROOT / 'olweightlifting' / f'{ev}.html'
        if p.exists():
            t = p.read_text(encoding='utf-8')
            t2 = OQR_RE.sub('', t)
            t2 = t2.replace('<h3>한국 주요 선수</h3>\n', '<h3>한국 주요 선수</h3>\n' + note + '\n', 1)
            if t2 != t:
                p.write_text(t2, encoding='utf-8', newline='\n')
    if SQUAD_RE.search(text):
        text = SQUAD_RE.sub(lambda _: squad_table(doc), text, 1)
    if text != orig:
        hub.write_text(text, encoding='utf-8', newline='\n')


def squad_table(doc):
    """'한국 역도 역사와 현황' 아래 체급별 한국 대표선수 표."""
    order = ['M65', 'M75', 'M85', 'M95', 'M110', 'M110P', 'F53', 'F61', 'F69', 'F77', 'F86', 'F86P']
    rows = []
    for code in order:
        c = doc['data'].get(code, {})
        label = TI_CATS[code]
        ev = TI_DOC[code][2]
        head = f'<th scope="row"><a href="olweightlifting/{ev}.html">{E(label)}</a></th>'
        if code in HEAVY:
            rows.append(f'<tr>{head}<td>{E(HEAVY_OLD[code])}</td><td colspan="2" class="muted">정리 중 (중량급)</td></tr>')
        elif c.get('korea'):
            for k, r in enumerate(c['korea']):
                state = '<b class="in8">8위 안</b>' if r['in8'] else f'8위와 {r["gap8"]:g}점 차'
                rows.append(f'<tr>{head if k == 0 else "<th></th>"}<td class="kor">{E(r["ko"])}</td><td class="c">{r["rank"]}위 · {r["points"]:g}점</td><td>{state}</td></tr>')
        else:
            rows.append(f'<tr>{head}<td class="muted">—</td><td colspan="2" class="muted">잠정 OQR 상위 30위 안 한국 선수 없음</td></tr>')
    day = doc['fetched'][:10].replace('-', '.')
    return ('<div class="korea-squad" id="korea-squad"><h3>체급별 한국 대표선수</h3>'
            '<div class="tw"><table class="wikitable narrow"><thead><tr><th>체급</th><th>대표선수</th><th>잠정 OQR</th><th>출전권선(8위)</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div><p class="small">{day} 잠정 OQR(비공식, totalintel) 기준으로 자동 갱신. '
            '중량급(남자 110kg·+110kg, 여자 86kg·+86kg)은 대표선수 정리 전이라 종전 기재를 그대로 둔다.</p></div><!-- /korea-squad -->')


def render():
    p = OUT / 'totalintel.json'
    if p.exists():
        render_notes(json.loads(p.read_text(encoding='utf-8')))
    for key, file in HUBS.items():
        page = ROOT / f'{file}.html'
        orig = page.read_text(encoding='utf-8')
        text = BLOCK_RE.sub('', orig)
        b = hub_block(file)
        if b and '<nav class="toc">' in text:  # 대회 결과 → 사설 랭킹 → 목차
            text = text.replace('<nav class="toc">', b + '\n<nav class="toc">', 1)
        if text != orig:
            page.write_text(text, encoding='utf-8', newline='\n')


def main(argv):
    reg = json.loads(REG.read_text(encoding='utf-8'))
    if argv[:1] == ['render']:
        render()
        return
    if not argv:
        for k, s in reg['sites'].items():
            print(f'{k:12} {s["sport"]:6} {s["url"]}  {s["what"]}' + ('' if k in READERS else '  (읽는 함수 없음)'))
        return
    key = argv[0]
    src = reg['sites'][key]
    print(f'{src["url"]} 읽는 중 …')
    data = READERS[key](src)
    OUT.mkdir(exist_ok=True)
    doc = {'source': src['url'], 'what': src['what'], 'note': src.get('note', ''),
           'fetched': dt.datetime.now(KST).strftime('%Y-%m-%d %H:%M KST'), 'data': data}
    if key == 'totalintel':  # 한국 요약: 체급별 최고 순위 선수
        doc['korea'] = [{'cat': v['label'], **r} for v in data.values() for r in v['korea'][:1]]
    (OUT / f'{key}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'→ data/private-rankings/{key}.json')
    render()


if __name__ == '__main__':
    main(sys.argv[1:])
