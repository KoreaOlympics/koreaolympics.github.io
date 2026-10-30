"""FIS calendar, race lists and results for every FIS Olympic discipline (fis-ski.com server-rendered HTML)."""
import datetime as dt, html, re
from .net import request

CAL = ('https://www.fis-ski.com/DB/general/calendar-results.html?eventselection=&place=&sectorcode={sector}'
       '&seasoncode={code}&categorycode={cat}&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode='
       '&seasonmonth=X-{code}&saveselection=-1&seasonselection=')
EVENT = 'https://www.fis-ski.com/DB/general/event-details.html?sectorcode={sector}&eventid={id}&seasoncode={code}'
RESULTS = 'https://www.fis-ski.com/DB/general/results.html?sectorcode={sector}&raceid={id}'
HTML = {'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en'}
MONTHS = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}
# Olympic-relevant level: World Cup, World Championships, Olympics
CATEGORIES = ('WC', 'WSC', 'OWG')
SECTORS = {'alpine': 'AL', 'cross-country': 'CC', 'ski-jumping': 'JP', 'nordic-combined': 'NK', 'freestyle': 'FS', 'snowboard': 'SB'}
DISC = {
    'AL': {'DH': '활강', 'SG': '슈퍼대회전', 'GS': '대회전', 'SL': '회전', 'AC': '복합', 'TCOM': '팀 복합', 'TC': '팀 복합', 'TP': '팀 평행', 'PAR': '평행', 'TE': '단체'},
    'CC': {'INT': '인터벌', 'SPQ': '스프린트', 'SPF': '', 'MAS': '매스스타트', 'SKT': '스키애슬론', 'PUR': '추적', 'REL': '계주',
           'TSPQ': '팀 스프린트', 'TSP': '', 'HMS': '하프 매스스타트', 'DI': '거리'},
    'JP': {'IND': '개인', 'TE': '단체', 'SUP': '슈퍼팀', 'MT': '혼성 단체'},
    'NK': {'PR': '', 'IC': '컴팩트', 'GU': '군더센', 'MS': '매스스타트', 'TE': '단체', 'TS': '팀 스프린트'},
    'FS': {'BA': '빅에어', 'SS': '슬로프스타일', 'HP': '하프파이프', 'SX': '스키크로스', 'MO': '모굴', 'DM': '듀얼 모굴', 'AE': '에어리얼',
           'AET': '에어리얼 단체', 'SXT': '스키크로스 단체'},
    'SB': {'BA': '빅에어', 'SS': '슬로프스타일', 'HP': '하프파이프', 'SBX': '스노보드크로스', 'PGS': '평행대회전', 'PSL': '평행회전',
           'SBX-T': '스노보드크로스 혼성 단체', 'BXT': '스노보드크로스 혼성 단체', 'PRT': ''},
}

def _text(fragment):
    return [html.unescape(x).strip() for x in re.findall(r'>([^<>]+)<', fragment) if x.strip()]

def _clean(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()

def _dates(label, season_start):
    """'30 Sep-01 Oct' / '12 Dec' / '28 Feb-01 Mar' / '24-25 Oct 2026' -> (date, date)."""
    nums = re.findall(r'\b\d{1,2}\b|[A-Z][a-z]{2}', re.sub(r'\b\d{4}\b', '', label))
    days = [int(x) for x in nums if x.isdigit()]
    months = [MONTHS[x] for x in nums if x in MONTHS]
    if not days or not months: return None, None
    m1 = months[0] if len(months) > 1 or len(days) == 1 else months[-1]
    m2 = months[-1]
    def mk(d, m): return dt.date(season_start + (0 if m >= 7 else 1), m, d)
    return mk(days[0], m1).isoformat(), mk(days[-1], m2).isoformat()

def calendar(sport, season_start):
    sector = SECTORS[sport]
    code = season_start + 1
    out, seen = [], set()
    for cat in ('WC', 'WSC', 'OWG'):
        page = request(CAL.format(sector=sector, code=code, cat=cat), headers=HTML)
        for eid, body in re.findall(r'<div class="table-row reset-padding"[^>]*id="(\d+)">(.*?)(?=<div class="table-row reset-padding"|<div class="pagination|\Z)', page, re.S):
            if eid in seen: continue
            cells = _text(body)
            # cells: D P C C | date | place | cat • cat | disciplines | place | place | NSA | sector | ...
            date_label = next((c for c in cells if re.match(r'^\d{1,2}(\s|-|$)', c)), '')
            cancelled = 'Cancelled' in body and 'Not cancelled' not in body
            cat_cell = next((c for c in cells if '•' in c or c in CATEGORIES), '')
            cats = [x.strip() for x in cat_cell.split('•')]
            if not any(c in CATEGORIES for c in cats): continue
            idx = cells.index(date_label) if date_label in cells else 0
            place = cells[idx + 1] if idx + 1 < len(cells) else ''
            nation = next((c for c in cells if re.fullmatch(r'[A-Z]{3}', c) and c != sector), '')
            disc_label = cells[cells.index(cat_cell) + 1] if cat_cell in cells and cells.index(cat_cell) + 1 < len(cells) else ''
            start, end = _dates(date_label, season_start)
            if not start: continue
            seen.add(eid)
            codes = list(dict.fromkeys(re.findall(r'(?:\d+x)?([A-Z]{2,4}(?:-T)?)\b', disc_label)))
            names = [DISC[sector].get(c, c) for c in codes if c != 'QUA']
            out.append({'id': f'fis-{eid}', 'sport': sport, 'source': 'FIS', 'name': f"{place} {' / '.join(n for n in dict.fromkeys(names) if n)}".strip(),
                        'category': cats[0], 'disciplines': codes, 'start': start, 'end': end, 'city': place, 'country': nation,
                        'state': 'Cancelled' if cancelled else '', 'url': EVENT.format(sector=sector, id=eid, code=code), 'raw': disc_label})
    return sorted(out, key=lambda e: e['start'])

def races(sport, event_id, season_start):
    """Every race (codex) of one FIS event: id, start time, name, gender, whether results exist."""
    sector = SECTORS[sport]
    page = request(EVENT.format(sector=sector, id=event_id, code=season_start + 1), headers=HTML)
    body = page[page.find('id="eventdetailscontent"'):]
    out = []
    for row in re.split(r'<div class="table-row reset-padding', body)[1:]:
        rid = re.search(r'raceid=(\d+)', row)
        if not rid: continue
        iso = re.search(r'data-iso-date="([^"]+)"', row)
        codex = re.search(r'codex\(\'(\d+)\'\)', row)
        name = re.search(r'<div class="clip">(.*?)</div>', row, re.S)
        flags = {title: bool(sel) for sel, title in re.findall(r'class="status__item( status__item_selected)?"\s+title="([^"]+)"', row)}
        gender = re.search(r'<div class="gender__item[^"]*">\s*([A-Z])\s*</div>', row)
        runs = [_clean(x) for x in re.findall(r'<div class="g-lg-5 g-md-9 justify-left hidden-sm-down">(.*?)</div>', row, re.S)]
        start = None
        day = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', row)
        if iso:
            d = dt.datetime.fromisoformat(iso.group(1))
            start = d.astimezone(dt.timezone.utc).isoformat().replace('+00:00', 'Z') if d.tzinfo else iso.group(1)
        live = re.search(r'href="(https://live\.fis-ski\.com/[^"]+)"', row)
        out.append({'id': rid.group(1), 'codex': codex.group(1) if codex else '', 'start_utc': start, 'date': day.group(1) if day else '',
                    'name': _clean(name.group(1)) if name else '', 'gender': gender.group(1) if gender else '',
                    'has_results': flags.get('Data available', False), 'cancelled': flags.get('Cancelled', False),
                    'live_url': live.group(1) if live else '', 'runs': [r for r in runs if r]})
    return out

LEAF = re.compile(r'<div class="([^"]*)"[^>]*>((?:(?!<div|</div>).)*)</div>', re.S)
SKIP = ('constructor-name', 'split-row', 'g-row', 'container')

def _leaves(fragment, header=False):
    fragment = re.sub(r'<!--.*?-->', '', fragment, flags=re.S)
    fragment = re.sub(r'<span class="hidden-md-up[^"]*">.*?</span>', '', fragment, flags=re.S)  # mobile-only duplicates
    out = []
    for cls, inner in LEAF.findall(fragment):
        if any(s in cls.split() for s in SKIP): continue
        if header and 'hidden-lg' in cls.split(): continue  # mobile-only header
        out.append((cls, _clean(inner)))
    return out

FIXED = {'Rank': 'rank', 'Order': 'order', 'Bib': 'bib', 'FIS code': 'code', 'Athlete': 'name', 'Year': 'year', 'Nation': 'noc'}

def results(sport, race_id):
    """{'title', 'date', 'columns', 'rows'} — columns are the result columns after the athlete/nation block."""
    page = request(RESULTS.format(sector=SECTORS[sport], id=race_id), headers=HTML)
    kind = re.search(r'class="event-header__kind">(.*?)</', page, re.S)
    out = {'title': _clean(kind.group(1)) if kind else '', 'columns': [], 'rows': []}
    i = page.find('id="events-info-results"')
    if i < 0: return out
    head = page.rfind('class="thead', 0, i)
    labels = [t for _, t in _leaves(page[head:i], header=True)]
    if not labels or labels[0] not in ('Rank', 'Order'): return out  # documents only (no data yet)
    fixed = [FIXED.get(l) for l in labels]
    n_fixed = next((k for k, f in enumerate(fixed) if f is None), len(fixed))
    rest = labels[n_fixed:]
    group = []
    if 'Round' in rest:  # ski jumping: Round / Distance / Points / Round Rank repeat per round
        a = rest.index('Round'); b = next((k for k in range(a + 1, len(rest)) if rest[k].startswith('Round')), a + 3)
        group = rest[a:b + 1]
    tail = page[i:]
    end = tail.find('<div class="table__footer') if '<div class="table__footer' in tail else len(tail)
    section = ''
    for m in re.finditer(r'<a class="table-row".*?</a>|class="thead thead_slave">.*?<div class="g-xs-24 bold">([^<]*)</div>', tail[:end], re.S):
        if m.group(1) is not None:  # 'Did not qualify', 'Did not finish 1st run', ...
            section = _clean(m.group(1)); continue
        row = m.group(0)
        cells = _leaves(row)
        vals = [t for _, t in cells]
        if len(vals) < n_fixed: continue
        r = {f: vals[k] for k, f in enumerate(fixed[:n_fixed]) if f}
        extra = vals[n_fixed:]
        if group:
            a = rest.index(group[0])
            n_rounds = max(1, (len(extra) - (len(rest) - len(group))) // len(group))
            cols = rest[:a] + [f'{k + 1}R {g}' if g != 'Round' else f'{k + 1}R' for k in range(n_rounds) for g in group] + rest[a + len(group):]
        else:
            cols = rest
        r['cells'] = dict(zip(cols, extra))
        for c in cols:
            if c not in out['columns'] and not re.fullmatch(r'\d+R', c): out['columns'].append(c)
        raw = r.get('rank', '')
        r['rank'] = int(raw) if raw.isdigit() else None
        r['status'] = '' if raw.isdigit() else raw or section  # DNF / DSQ / DNS, or the section the row sits in
        out['rows'].append(r)
    out['start_list'] = labels[0] == 'Order'
    return out
