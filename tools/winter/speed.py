"""Speed skating results from the ISU live results system (api.isuresults.eu)."""
from .net import get_json

API = 'https://api.isuresults.eu'
LIVE = 'https://live.isuresults.eu/events/{id}/schedule'

def events(season_code):
    """season_code: 2027 for 2026/2027. Senior World Cup / championship events only."""
    out, url = [], f'{API}/events/?orderBy=start&isPublished=1&season={season_code}&pageSize=100'
    while url:
        r = get_json(url)
        out += r['results']; url = r.get('next')
    return [e for e in out if 'senior' in e.get('tags', []) and not e.get('isCancelled')]

def event(e):
    t = e.get('track') or {}
    return {'id': f"ssr-{e['isuId']}", 'sport': 'speed-skating', 'source': 'ISU Results', 'isu_id': e['isuId'],
            'name': e['name'], 'category': ', '.join(e.get('tags', [])), 'start': e['start'], 'end': e['end'],
            'tz': t.get('timeZone'), 'city': t.get('city', ''), 'country': t.get('country', ''),
            'state': 'Live' if e.get('isLive') else '', 'url': LIVE.format(id=e['isuId'])}

def schedule(isu_id):
    return get_json(f'{API}/events/{isu_id}/schedule/')

def competitions(isu_id):
    r = get_json(f'{API}/events/{isu_id}/competitions/')
    return r if isinstance(r, list) else r.get('results', [])

def results(isu_id, number):
    return get_json(f'{API}/events/{isu_id}/competitions/{number}/results/')

def row(r):
    comp = r.get('competitor') or {}
    sk = comp.get('skater') or {}
    team = comp.get('team') or {}
    name = f"{sk.get('firstName', '')} {sk.get('lastName', '')}".strip() or team.get('name') or comp.get('identifier', '')
    return {'rank': r.get('rank'), 'name': name, 'noc': sk.get('country') or team.get('country') or '',
            'time': r.get('time') or '', 'behind': r.get('timeBehind') or '', 'lane': r.get('startLane'),
            'pair': r.get('startNumber'), 'medal': r.get('medal'), 'status': r.get('status'),
            'points': r.get('points'), 'official': r.get('isOfficial')}
