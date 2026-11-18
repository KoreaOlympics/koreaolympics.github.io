"""부록: 국가대표 선발전 결과 (data/trials-winners.json → 종목 허브 '부록: 국내 대회 우승자' 안).

    python tools/trials.py              # 대한체육회 경기운영 정보 시스템에서 최근 선발전 결과를 다시 받는다
    python tools/olympic.py build       # 허브에 부록을 다시 넣는다

자료는 대한체육회 종목별 경기운영 정보 시스템(result.sports.or.kr)에 올라온 결과에서만 가져온다. 기사·검색 결과는 쓰지 않는다.
이 시스템에 최근 선발전 결과가 없는 종목(양궁·유도·펜싱·사격·태권도·배드민턴·탁구 성인부 등)은 싣지 않는다.
대회 목록에서 이름으로 가장 최근 선발전을 찾으므로, 새 선발전이 올라오면 다시 실행만 하면 된다.
결과가 하나도 없는 대회(등록만 되어 있는 대회)는 건너뛴다.
"""
import datetime as dt, html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/trials-winners.json'
BASE = 'https://result.sports.or.kr'
SOURCE = '대한체육회 종목별 경기운영 정보 시스템 (result.sports.or.kr)'


def _req(path, data=None, js=False):
    if js:
        body, ctype = json.dumps(data).encode(), 'application/json; charset=UTF-8'
    else:
        body, ctype = urllib.parse.urlencode(data or {}).encode(), 'application/x-www-form-urlencoded'
    req = urllib.request.Request(BASE + path, data=body, headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': ctype})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode('utf-8', 'replace')
    return json.loads(raw) if js else raw


def _txt(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def _time(s):
    """'00:41.606' → '41.606', '01:46.22' → '1:46.22'."""
    s = re.sub(r'^00:', '', s.strip())
    return re.sub(r'^0(\d:)', r'\1', s)


def _cells(tr):
    return [_txt(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]


def competitions(code, keyword, pages=2):
    """종목 포털의 대회 목록 [(classCd, toCd, 대회명, 장소, 시작일, 종료일)] — 최근 순."""
    out = []
    for page in range(1, pages + 1):
        t = _req(f'/{code}/INF201.do', {'pageIndex': page, 'searchEventNm': keyword})
        for attrs, tr in re.findall(r'<tr([^>]*)>(.*?)</tr>', t, re.S):
            a = re.search(r'fnEventInfo\(([^)]*)\)', attrs + tr)  # onclick이 <tr>에 붙은 포털도 있다
            if not a:
                continue
            args = [x.strip(" '\"") for x in html.unescape(a.group(1)).split(',')]
            c = [x for x in _cells(tr) if x]
            # "2026.04.07~2026.04.09", "2026. 09.04 ~ 09.05", "2026.02.20 ~ 02.23" (뒤에 참가신청 기간이 붙기도 한다)
            d = re.search(r'(20\d\d)\.\s*(\d\d)\.(\d\d)\s*~\s*(?:(20\d\d)\.\s*)?(\d\d)\.(\d\d)', _txt(tr))
            if len(args) < 2 or len(c) < 3 or not d:
                continue
            start = f'{d.group(1)}-{d.group(2)}-{d.group(3)}'
            end = f'{d.group(4) or d.group(1)}-{d.group(5)}-{d.group(6)}'
            row = (args[-2], args[-1], c[1], c[2], start, end)
            if row not in out:
                out.append(row)
    return out


# ---------- 쇼트트랙 (빙상 포털 /SK, 거리별 결승 A) ----------
def shorttrack(class_cd, to_cd):
    info = _req('/SK/INF202.do', {'classCd': class_cd, 'toCd': to_cd})
    events = []
    for kind, detail in re.findall(r'fnEventSchedule\(&#34;(\w+)&#34;,&#34;(\w+)&#34;\)', info):
        form = {'classCd': class_cd, 'toCd': to_cd, 'kindCd': kind, 'detailClassCd': detail, 'searchKindCd': kind, 'searchDetailClassCd': detail}
        sched = _req('/SK/INF301.do', form)
        for args in re.findall(r'fnEventResult\(([^)]*)\)', html.unescape(sched)):
            use, pcnt, base, rh, rhnm, dist = [x.strip(' "\'') for x in args.split(',')]
            if rhnm != '결승':
                continue
            page = _req('/SK/INF310.do', dict(form, baseClassCd=base, rhCd=rh, rhNm=rhnm, baseClassNm=dist, pcntGbn=pcnt, useGbn=use))
            rows = [_cells(tr) for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', page, re.S)]
            div = next((r[0] for r in rows if len(r) == 1 and r[0].endswith('부')), '')
            podium = [{'rank': int(r[0]), 'name': r[2], 'team': r[3], 'record': _time(r[6])}
                      for r in rows if len(r) >= 7 and r[0].isdigit() and int(r[0]) <= 3]
            if podium:
                events.append({'division': div, 'event': dist.replace('M', 'm'), 'podium': podium})
    return events


# ---------- 레슬링 (/WR, JSON API, 체급별 1위) ----------
def _wr(path, body):
    return _req(f'/WR/api/result/{path}', body, js=True)


def wrestling(class_cd, to_cd):
    body = {'classCd': class_cd, 'toCd': to_cd}
    info = _req('/WR/INF202.do', body)
    style = {'F': '자유형', 'G': '그레코로만형', 'WW': '여자 자유형'}
    events = []
    for kind, detail in re.findall(r"fnEventSchedule\('([^']*)','([^']*)'\)", info):
        b = dict(body, kindCd=kind, detailClassCd=detail)
        names = {d['detailClassCd']: d['detailClassNm'] for d in _wr('detailClassCds.do', b)}
        nm = names.get(detail, '')
        m = re.match(r'(WW|F|G)(\d+)kg', nm)
        if not m:
            continue
        team = {p['korNm']: p.get('teamNm') or '' for p in _wr('tourplayers.do', b)}
        clean = lambda s: re.sub(r'\((승|패)\)', '', s or '').strip()
        final = [s for s in _wr('schedules.do', b) if (s.get('rhNm') or '').strip() == '결승' and s.get('winnerGb') in ('1', '2')]
        if final:  # 토너먼트·노르딕&토너먼트: 결승 승자
            f = final[-1]
            w, l = (f['korNmL'], f['korNmR']) if f['winnerGb'] == '1' else (f['korNmR'], f['korNmL'])
            order = [clean(w), clean(l)]
        else:  # 노르딕(리그전): 조가 하나일 때만 순위표 1·2위
            rank = _wr('league/ranking.do', b)
            if not rank or len({r['groupCd'] for r in rank}) != 1:
                continue
            order = [r['korNm'] for r in sorted(rank, key=lambda r: int(r['rank'] or 99))[:2]]
        events.append({'division': style[m.group(1)], 'event': f'{m.group(2)}kg',
                       'podium': [{'rank': i + 1, 'name': n, 'team': team.get(n, '')} for i, n in enumerate(order) if n]})
    order = {'자유형': 0, '그레코로만형': 1, '여자 자유형': 2}
    return sorted(events, key=lambda e: (order[e['division']], int(e['event'][:-2])))


# ---------- 수영 경영 (/SW, 종목별 결승) ----------
def swimming(class_cd, to_cd):
    info = _req('/SW/INF202.do', {'classCd': class_cd, 'toCd': to_cd})
    events = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', info, re.S):
        a = re.search(r'fnEventSchedule\(&#34;(\w+)&#34;,&#34;(\w+)&#34;\)', tr)
        c = _cells(tr)
        if not a or len(c) < 2:
            continue
        kind, detail = a.groups()
        form = {'classCd': class_cd, 'toCd': to_cd, 'kindCd': kind, 'detailClassCd': detail, 'searchKindCd': kind, 'searchDetailClassCd': detail}
        sched = _req('/SW/INF301.do', form)
        rounds = re.findall(r'fnGameResult\(&#34;(\w+)&#34;\)', sched)
        if not rounds:
            continue
        rh = '9' if '9' in rounds else rounds[-1]  # 결승(없으면 마지막 경기)
        page = _req('/SW/INF306.do', dict(form, rhCd=rh, gubun='T'))
        podium = []
        for row in re.findall(r'<tr>(.*?)</tr>', page, re.S):
            x = [_txt(v) for v in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)]
            if len(x) >= 6 and x[0].isdigit() and int(x[0]) <= 3 and re.search(r'\d\d:\d\d\.\d\d', x[5]):
                podium.append({'rank': int(x[0]), 'name': re.sub(r'\(\d\)$', '', x[3]), 'team': re.sub(r'\([^)]*\)$', '', x[2]),
                               'record': _time(x[5]), 'note': x[6] if len(x) > 6 else ''})
        if podium:
            events.append({'division': c[0], 'event': c[1], 'podium': podium})
    return events


# ---------- 종목별 설정 ----------
def _groups(rows, pattern, group):
    """이름이 pattern에 맞는 대회를 '같은 선발 회차'(group 정규식의 첫 그룹, 예: 2026/27시즌)로 묶는다 — 최근 묶음부터."""
    today = dt.date.today().isoformat()
    hits = sorted((r for r in rows if re.search(pattern, r[2]) and r[4] <= today), key=lambda r: r[4], reverse=True)
    out = {}
    for r in hits:
        m = re.search(group, r[2])
        out.setdefault(m.group(1) if m else r[2], []).append(r)
    return list(out.values())


SPORTS = {
    'wishorttrack': ('SK', '쇼트트랙 국가대표', r'쇼트트랙 국가대표 \d차 선발', r'(\d{4}/\d\d)시즌', shorttrack,
                     '대회별 거리 결승(A) 1~3위다.'),
    'olwrestling': ('WR', '국가대표', r'국가대표 (최종|\d차) ?선발대회', r'(\d{4})년', wrestling,
                    '체급별 1·2위다. 리그전(노르딕) 체급은 순위표, 토너먼트 체급은 결승 승자·패자로 적었다.'),
    'olswimming': ('SW', '경영', r'경영.{0,3}국가대표 선발대회', r'(\d{4})', swimming,
                   '종목별 결승 1~3위다.'),
}


def update():
    out = {'_source': SOURCE, 'updated_at': dt.date.today().isoformat(), 'sports': {}}
    prev = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
    for hub, (code, kw, pattern, group, fn, how) in SPORTS.items():
        trials = []
        try:
            for batch in _groups(competitions(code, kw), pattern, group)[:2]:  # 가장 최근 회차에 결과가 없으면(이제 막 시작) 그 앞 회차
                for class_cd, to_cd, name, place, start, end in batch:
                    events = fn(class_cd, to_cd)
                    print(f'{hub}: {name} ({start}) · {len(events)}개 세부종목', file=sys.stderr)
                    if events:
                        trials.append({'name': name, 'place': place, 'start': start, 'end': end,
                                       'url': f'{BASE}/{code}/INF201.do', 'events': events})
                if trials:
                    break
        except Exception as e:  # 한 종목이 실패해도 나머지는 받는다
            print(f'{hub}: 받기 실패 {e!r}', file=sys.stderr)
            trials = []
        if not trials:
            old = (prev.get('sports') or {}).get(hub)
            print(f'{hub}: 결과가 올라온 선발전 없음 ({"이전 자료 유지" if old else "건너뜀"})', file=sys.stderr)
            if old:  # 시스템 장애 등으로 못 받았을 때 있던 자료를 지우지 않는다
                out['sports'][hub] = old
        else:
            out['sports'][hub] = {'how': how, 'trials': trials}
    DATA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


# ---------- 허브 부록 ----------
E = lambda s: html.escape(str(s), quote=True)


def _who(p):
    return f'{E(p["name"])}' + (f' <span class="small">({E(p["team"])})</span>' if p.get('team') else '')


def _table(events):
    record = any(p.get('record') for e in events for p in e['podium'])
    third = any(len(e['podium']) > 2 for e in events)
    head = '<th>종별</th><th>세부종목</th><th>1위</th><th>2위</th>' + ('<th>3위</th>' if third else '')
    body = ''
    for e in events:
        by = {p['rank']: p for p in e['podium']}
        cell = lambda r: (f'{_who(by[r])}' + (f' {E(by[r]["record"])}' if record and by[r].get('record') else '')
                          + (f' <b>{E(by[r]["note"])}</b>' if by[r].get('note') else '')) if r in by else ''
        body += f'<tr><td>{E(e["division"])}</td><td>{E(e["event"])}</td><td>{cell(1)}</td><td>{cell(2)}</td>' + (f'<td>{cell(3)}</td>' if third else '') + '</tr>'
    return f'<table class="wikitable"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def hub_part(file, data=None):
    """허브 하나의 선발전 부분 (h3부터). 자료가 없으면 ''."""
    if data is None:
        data = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
    d = (data.get('sports') or {}).get(file)
    if not d:
        return ''
    out = ['<h3>국가대표 선발전</h3>',
           f'<p>{SOURCE.split(" (")[0]}(<a href="{E(d["trials"][0]["url"])}">result.sports.or.kr</a>)에 올라온 결과만 옮겼다 '
           f'({E(data.get("updated_at", ""))} 기준). {E(d["how"])} 최종 선발 명단은 연맹 발표로 확인한다.</p>']
    for i, t in enumerate(d['trials']):
        when = t['start'] + ('' if t['end'] == t['start'] else ' ~ ' + t['end'][5:])
        title = f'{E(t["name"])} <span class="small">({E(when)}, {E(t["place"])})</span>'
        if i == 0:
            out += [f'<h4>{title}</h4>', _table(t['events'])]
        else:
            out.append(f'<details><summary>{title}</summary>{_table(t["events"])}</details>')
    return '\n'.join(out)


if __name__ == '__main__':
    update()
