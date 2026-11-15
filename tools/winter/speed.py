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
    """number: the competition's scheduleNumber (its `number` field is only the 1st/2nd 500m race index)."""
    return get_json(f'{API}/events/{isu_id}/competitions/{number}/results/')

def row(r):
    """One result line. Individual and mass-start rows carry `competitor`; team pursuit rows carry `team` at the top level."""
    comp = r.get('competitor') or {}
    sk = comp.get('skater') or {}
    team = r.get('team') or comp.get('team') or {}
    name = f"{sk.get('firstName', '')} {sk.get('lastName', '')}".strip() or team.get('name') or comp.get('identifier', '')
    members = [f"{m['member']['skater'].get('firstName', '')} {m['member']['skater'].get('lastName', '')}".strip()
               for m in team.get('members', []) if (m.get('member') or {}).get('skater')
               and (not r.get('activeMembers') or m['member'].get('identifier') in r['activeMembers'])]
    out = {'rank': r.get('rank'), 'name': name, 'noc': sk.get('country') or team.get('country') or '',
           'time': r.get('time') or '', 'behind': r.get('timeBehind') or '', 'lane': r.get('startLane'),
           'pair': r.get('startNumber'), 'medal': r.get('medal'), 'status': r.get('status'),
           'points': r.get('points') if r.get('points') is not None else r.get('sprintPoints'), 'official': r.get('isOfficial')}
    if members:
        out['members'] = members
    return out
