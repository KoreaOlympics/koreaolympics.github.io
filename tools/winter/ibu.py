"""IBU biathlon World Cup / World Championships (biathlonresults.com public JSON API)."""
from .net import get_json

API = 'https://www.biathlonresults.com/modules/sportapi/api/'
SITE = 'https://www.biathlonresults.com/'

def season_id(season_start):
    return f'{season_start % 100:02d}{(season_start + 1) % 100:02d}'

def calendar(season_start):
    out = []
    for e in get_json(API + f'Events?SeasonId={season_id(season_start)}&Level=1'):
        champs = 'SWRLCH' in e['EventId']
        out.append({'id': f"ibu-{e['EventId']}", 'sport': 'biathlon', 'source': 'IBU', 'ibu_id': e['EventId'],
                    'name': f"{e['ShortDescription']} {'세계선수권' if champs else '월드컵'}", 'category': 'WCH' if champs else 'WC',
                    'start': (e.get('FirstCompetitionDate') or e['StartDate'])[:10], 'end': e['EndDate'][:10],
                    'city': e['ShortDescription'], 'country': e.get('Nat') or '', 'state': 'Live' if e.get('IsCurrent') else '',
                    'url': SITE})
    return sorted(out, key=lambda e: e['start'])

def races(event_id):
    return [{'id': c['RaceId'], 'name': c.get('ShortDescription') or c['Description'], 'start_utc': c['StartTime'],
             'gender': {'SM': 'M', 'SW': 'W', 'MX': 'A'}.get(c.get('catId'), ''), 'status': c.get('StatusText') or '',
             'live': bool(c.get('IsLive')), 'has_results': c.get('ResultStatus') in ('OFFICIAL', 'UNOFFICIAL') or c.get('StatusId') == 11}
            for c in get_json(API + f'Competitions?EventId={event_id}')]

def results(race_id):
    """Same shape as fis.results(): title, columns, rows (relays: team rows only)."""
    d = get_json(API + f'Results?RaceId={race_id}')
    rows = []
    for r in d.get('Results') or []:
        if r.get('Leg') not in (None, 0, '0'): continue  # relay legs; keep team lines
        rank = r.get('Rank') or ''
        rows.append({'rank': int(rank) if str(rank).isdigit() else None, 'status': r.get('IRM') or '', 'bib': r.get('Bib') or '',
                     'name': r.get('Name') or '', 'noc': r.get('Nat') or '',
                     'cells': {'사격': r.get('Shootings') or '', '기록': r.get('TotalTime') or r.get('Result') or '',
                               '차이': r['Behind'] if str(r.get('Behind') or '').startswith('+') else ('+' + r['Behind']) if r.get('Behind') not in (None, '', '0.0') else ''}})
    comp = d.get('Competition') or {}
    return {'title': comp.get('ShortDescription') or comp.get('Description') or '', 'columns': ['사격', '기록', '차이'],
            'rows': rows, 'start_list': bool(d.get('IsStartList')) and not d.get('IsResult')}
