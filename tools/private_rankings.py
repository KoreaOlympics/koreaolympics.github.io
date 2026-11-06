"""사설(비공식) 올림픽 예선 랭킹 집계 사이트에서 랭킹을 받아 온다.

    python tools/private_rankings.py                # 등록된 곳 목록
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


def main(argv):
    reg = json.loads(REG.read_text(encoding='utf-8'))
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


if __name__ == '__main__':
    main(sys.argv[1:])
