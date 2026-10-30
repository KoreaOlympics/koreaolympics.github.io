"""Sliding calendars: IBSF bobsleigh & skeleton, FIL luge (results are PDFs / scripted pages: calendar only for now)."""
import datetime as dt, html, re
from .net import request

HTML = {'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en'}
IBSF = 'https://www.ibsf.org/en/races-and-results'
FIL = 'https://www.fil-luge.org/en/results'
MONTHS = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}
IBSF_LEVEL = {'WC': ('WC', '월드컵'), 'WCH': ('WCH', '세계선수권')}

def _d(day, mon, year):
    return dt.date(int(year), MONTHS[mon[:3]], int(day)).isoformat()

def ibsf_calendar():
    """'11. Nov 2026 - 16. Nov 2026, WC Bobsleigh & Skeleton Altenberg' options of the event filter (current season)."""
    page = request(IBSF, headers=HTML)
    sel = re.search(r'name="tx_fmresults_list\[event_id\]">(.*?)</select>', page, re.S)
    out = []
    for eid, label in re.findall(r'<option[^>]*value="(\d+)"[^>]*>(.*?)</option>', sel.group(1) if sel else '', re.S):
        label = html.unescape(re.sub(r'\s+', ' ', label)).strip()
        m = re.match(r'(\d+)\. (\w+) (\d{4}) - (\d+)\. (\w+) (\d{4}), (\S+) (.*)$', label)
        if not m: continue
        prefix, rest = m.group(7), m.group(8)
        if prefix == 'World' and rest.startswith('Championships '):  # 'World Championships Lillehammer': both sports
            prefix, rest = 'WCH', 'Bobsleigh & Skeleton ' + rest.split(' ', 1)[1]
        if prefix not in IBSF_LEVEL: continue
        level, ko = IBSF_LEVEL[prefix]
        kinds = [k for k, word in (('bobsleigh', 'Bobsleigh'), ('skeleton', 'Skeleton')) if word in rest and 'Para' not in rest]
        city = re.sub(r'^(Bobsleigh & Skeleton|Bobsleigh|Skeleton) ', '', rest)
        for sport in kinds:
            out.append({'id': f'ibsf-{eid}-{sport[:3]}', 'sport': sport, 'source': 'IBSF', 'name': f'{city} {ko}', 'category': level,
                        'start': _d(*m.group(1, 2, 3)), 'end': _d(*m.group(4, 5, 6)), 'city': city, 'country': '', 'state': '',
                        'url': IBSF})
    return sorted(out, key=lambda e: e['start'])

def fil_calendar():
    """Senior luge (artificial track) World Cups and Championships from the FIL results index."""
    page = request(FIL, headers=HTML)
    out = []
    for block in re.findall(r'<div class="col-xs-12 events"><h2>(.*?)</h2>(.*?)(?=<div class="col-xs-12 events"><h2>|\Z)', page, re.S):
        section, body = block
        if section not in ('World Cups', 'Championships', 'Olympic Games', 'Relay competitions', 'Mixed Event', 'Sprint World Cup'): continue
        for href, d1, d2, title, track in re.findall(r'<a href="([^"]+)" class="event-link"><div[^>]*>(\d\d\.\d\d\.\d{4}) - (\d\d\.\d\d\.\d{4})</div>'
                                                     r'<div[^>]*event-title">(.*?)</div>.*?<div class="col-xs-12 col-sm-2">(.*?)</div>', body, re.S):
            title = html.unescape(title).strip()
            if track.strip() != 'Luge Artificial Track' or re.search(r'Junior|Youth|Asian|America Pacific|Juniors', title): continue
            name, _, place = title.partition(' | ')
            pm = re.match(r'(.*?) \((\w{3})\)', place)
            iso = lambda s: '-'.join(reversed(s.split('.')))
            ko = '세계선수권' if 'World Championships' in name else '유럽선수권' if 'European Championships' in name else \
                 '팀 계주 월드컵' if 'Relay' in name else '월드컵'
            city = pm.group(1) if pm else place
            out.append({'id': 'fil-' + href.rstrip('/').split('/')[-1], 'sport': 'luge', 'source': 'FIL', 'name': f'{city} {ko}',
                        'category': section, 'start': iso(d1), 'end': iso(d2), 'city': city, 'country': pm.group(2) if pm else '',
                        'state': '', 'url': 'https://www.fil-luge.org' + href})
    return sorted({e['id']: e for e in out}.values(), key=lambda e: e['start'])
