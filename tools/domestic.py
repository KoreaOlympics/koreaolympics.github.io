"""부록: 국내 대회 우승자 (data/domestic-winners.json → 종목 허브 맨 아래 <section id="domestic">).

    python tools/domestic.py            # 대한체육회 전국체육대회 정보 시스템에서 금메달 명세를 다시 받는다
    python tools/olympic.py build       # 허브에 부록을 다시 넣는다

자료는 대한체육회 공식 결과 시스템(meet.sports.or.kr)의 '종목별 메달명세'에서만 가져온다. 기사·검색 결과는 쓰지 않는다.
이 시스템은 가장 최근 대회만 보여 주므로, 새 대회가 열리면 다시 받아 덮어쓴다.
대상은 index에 굵게 표시된 한국 주요 종목이다 (SPORTS).
"""
import datetime as dt, html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/domestic-winners.json'
E = lambda s: html.escape(str(s), quote=True)

# 허브 파일 → (대회 구분, 종목 코드). 코드는 '종목별 메달명세'의 종목 선택 목록 값.
SPORTS = {
    'olbadminton': ('national', '26'), 'olshooting': ('national', '21'), 'olarchery': ('national', '20'),
    'oljudo': ('national', '17'), 'oltaekwondo': ('national', '27'), 'olfencing': ('national', '25'),
    'wishorttrack': ('winter', 'W2'), 'wisnowboard': ('winter', 'W9'), 'wicurling': ('winter', 'W8'),
}
BASE = 'https://meet.sports.or.kr/{meet}/'
KEEP = ('일반', '대학', '18세')  # 12세·15세이하부(초·중학생)는 싣지 않는다
COLS = ('division', 'event', 'medal', 'sido', 'name', 'team', 'grade', 'record', 'new_record', 'date')


def _get(url, data=None):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None,
                                 headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


def _cells(tr):
    return [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', c))).strip() for c in re.findall(r'<td.*?</td>', tr, flags=re.S)]


def fetch(meet, code):
    """한 종목의 금메달 명세. 같은 표가 화면 크기별로 여러 번 들어 있어 중복을 걷어낸다."""
    page = _get(BASE.format(meet=meet) + 'medal/medalClass.do',
                {'searchMenuId': '1302', 'pageIndex': '1', 'searchClassCd': code, 'searchKindCd': ''})
    seen, rows = set(), []
    for table in re.findall(r'<table.*?</table>', page, flags=re.S):
        if '선수명' not in table:
            continue
        for tr in re.findall(r'<tr.*?</tr>', table, flags=re.S):
            c = tuple(_cells(tr))
            if len(c) == len(COLS) and c not in seen:
                seen.add(c)
                rows.append(dict(zip(COLS, c)))
    events = {}
    for r in rows:
        if r['medal'] != '금' or not any(k in r['division'] for k in KEEP):
            continue
        ev = events.setdefault((r['division'], r['event']), {
            'division': r['division'], 'event': r['event'], 'sido': r['sido'], 'winners': [],
            'record': r['record'], 'new_record': r['new_record'], 'date': r['date'].replace('/', '-')})
        if r['sido'] not in ev['sido'].split(' · '):  # 공동 우승
            ev['sido'] += ' · ' + r['sido']
        ev['winners'].append({'name': r['name'], 'team': r['team']})
    return list(events.values()), len(rows)


def update():
    out = {'_source': '대한체육회 전국체육대회 정보 시스템 (meet.sports.or.kr) 종목별 메달명세', 'updated_at': dt.date.today().isoformat(), 'sports': {}}
    prev = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
    titles = {}
    for file, (meet, code) in SPORTS.items():
        if meet not in titles:
            m = re.search(r'<title>\s*([^<]+?)\s*</title>', _get(BASE.format(meet=meet) + 'main.do'))
            titles[meet] = m.group(1) if m else ''
        events, total = fetch(meet, code)
        if not events:
            old = (prev.get('sports') or {}).get(file)
            print(f'{file}: 금메달 명세 없음 ({"이전 자료 유지" if old else "건너뜀"})', file=sys.stderr)
            if old:  # 시스템 장애·새 대회 준비 중일 때 있던 자료를 지우지 않는다
                out['sports'][file] = old
            continue
        year = max(e['date'] for e in events)[:4]
        out['sports'][file] = {'festival': {'name': titles[meet], 'year': int(year), 'url': BASE.format(meet=meet) + 'main.do', 'events': events}}
        print(f'{file}: {titles[meet]} · 메달 {total}행 · 우승 {len(events)}개 세부종목')
    DATA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


# ---------- 허브 부록 ----------
def _rank(division):
    """일반부 → 대학부 → 18세이하부 → 그 밖, 같은 급에서는 남자 → 여자 → 혼성."""
    level = next((i for i, k in enumerate(KEEP) if k in division), 9)
    sex = 0 if division.startswith('남') else 1 if division.startswith('여') else 2
    return level, sex


def _winners(ev):
    teams = {}
    for w in ev['winners']:
        teams.setdefault(w['team'], []).append(w['name'])
    return ', '.join(f'{" · ".join(E(n) for n in names)} <span class="small">({E(team)})</span>' if team else ' · '.join(E(n) for n in names)
                     for team, names in teams.items())


def _table(events):
    record = any(e['record'] for e in events)
    rows = ''.join(
        f'<tr><td>{E(e["division"])}</td><td>{E(e["event"])}</td><td>{_winners(e)}</td><td>{E(e["sido"])}</td>'
        + (f'<td>{E(e["record"])}{" <b>" + E(e["new_record"]) + "</b>" if e["new_record"] else ""}</td>' if record else '') + '</tr>'
        for e in events)
    return ('<table class="wikitable"><thead><tr><th>종별</th><th>세부종목</th><th>우승 (소속)</th><th>시·도</th>'
            + ('<th>기록</th>' if record else '') + f'</tr></thead><tbody>{rows}</tbody></table>')


def hub_block(file, data=None):
    """허브 하나의 부록: 전국체전 우승자 + 국가대표 선발전 결과(tools/trials.py). 둘 다 없으면 ''."""
    from trials import hub_part
    trials = hub_part(file)
    if data is None:
        data = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
    d = (data.get('sports') or {}).get(file)
    if not d or not d.get('festival'):
        return f'<section id="domestic">\n<h2>부록: 국내 대회 우승자</h2>\n{trials}\n</section>' if trials else ''
    f = d['festival']
    events = sorted(f['events'], key=lambda e: _rank(e['division']))  # 안정 정렬: 같은 종별 안에서는 공식 순서 유지
    senior = [e for e in events if _rank(e['division'])[0] == 0]
    out = [f'<h3>{E(f["name"])} ({f["year"]}) 우승자</h3>',
           f'<p>대한체육회 공식 결과 시스템의 <a href="{E(f["url"])}">종목별 메달명세</a>에서 금메달만 옮겼다 '
           f'({E(data.get("updated_at", ""))} 기준). 단체전은 출전 선수를 소속별로 묶었다.</p>']
    if senior:
        out.append(_table(senior))
    for label, level in (('대학부', 1), ('18세이하부', 2)):
        part = [e for e in events if _rank(e['division'])[0] == level]
        if part:
            out.append(f'<details><summary>{label} 우승자 ({len(part)}개 세부종목)</summary>{_table(part)}</details>')
    if trials:
        out.append(trials)
    return '<section id="domestic">\n<h2>부록: 국내 대회 우승자</h2>\n' + '\n'.join(out) + '\n</section>'


if __name__ == '__main__':
    update()
