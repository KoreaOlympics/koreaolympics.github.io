"""FIS snowboard calendar (fis-ski.com server-rendered HTML)."""
import datetime as dt, html, re
from .net import request

CAL = ('https://www.fis-ski.com/DB/general/calendar-results.html?eventselection=&place=&sectorcode=SB'
       '&seasoncode={code}&categorycode={cat}&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode='
       '&seasonmonth=X-{code}&saveselection=-1&seasonselection=')
EVENT = 'https://www.fis-ski.com/DB/general/event-details.html?sectorcode=SB&eventid={id}&seasoncode={code}'
MONTHS = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}
# Olympic-relevant snowboard: World Cup, World Championships, Olympics
CATEGORIES = ('WC', 'WSC', 'OWG')
DISC = {'BA': '빅에어', 'SS': '슬로프스타일', 'HP': '하프파이프', 'SBX': '스노보드크로스', 'PGS': '평행대회전',
        'PSL': '평행회전', 'SBX-T': '스노보드크로스 혼성 단체'}

def _text(fragment):
    return [html.unescape(x).strip() for x in re.findall(r'>([^<>]+)<', fragment) if x.strip()]

def _dates(label, season_start):
    """'30 Sep-01 Oct' / '12 Dec' / '28 Feb-01 Mar' -> (date, date)."""
    nums = re.findall(r'\d{1,2}|[A-Z][a-z]{2}', label)
    days = [int(x) for x in nums if x.isdigit()]
    months = [MONTHS[x] for x in nums if x in MONTHS]
    if not days or not months: return None, None
    m1 = months[0] if len(months) > 1 or len(days) == 1 else months[-1]
    m2 = months[-1]
    def mk(d, m): return dt.date(season_start + (0 if m >= 7 else 1), m, d)
    return mk(days[0], m1).isoformat(), mk(days[-1], m2).isoformat()

def calendar(season_start):
    code = season_start + 1
    page = request(CAL.format(code=code, cat=''))
    out = []
    for eid, body in re.findall(r'<div class="table-row reset-padding"[^>]*id="(\d+)">(.*?)(?=<div class="table-row reset-padding"|<div class="pagination|\Z)', page, re.S):
        cells = _text(body)
        # cells: D P C C | date | place | cat/event | ... | NSA | ...
        date_label = next((c for c in cells if re.match(r'^\d{1,2}(\s|-|$)', c)), '')
        cancelled = 'Cancelled' in body and 'Not cancelled' not in body
        cat = next((c for c in cells if '•' in c or c in CATEGORIES), '')
        cats = [x.strip() for x in cat.split('•')]
        if not any(c in CATEGORIES for c in cats): continue
        idx = cells.index(date_label) if date_label in cells else 0
        place = cells[idx + 1] if idx + 1 < len(cells) else ''
        nation = next((c for c in cells if re.fullmatch(r'[A-Z]{3}', c) and c not in ('SB',)), '')
        disc_label = cells[cells.index(cat) + 1] if cat in cells and cells.index(cat) + 1 < len(cells) else ''
        start, end = _dates(date_label.replace('\n', ''), season_start)
        if not start: continue
        codes = sorted(set(re.findall(r'\d*x?([A-Z]{2,4}(?:-T)?)', disc_label)) - {'PRT', 'QUA'})
        out.append({'id': f'fis-{eid}', 'sport': 'snowboard', 'name': f"{place} {' / '.join(DISC.get(c, c) for c in codes)}".strip(),
                    'category': cats[0], 'disciplines': codes, 'start': start, 'end': end, 'city': place, 'country': nation,
                    'state': 'Cancelled' if cancelled else '', 'url': EVENT.format(id=eid, code=code), 'raw': disc_label})
    return sorted(out, key=lambda e: e['start'])
