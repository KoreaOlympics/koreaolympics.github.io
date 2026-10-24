"""ISU (isu-skating.com) collector: calendar, session schedule, rounds, heats.

The public site is a Next.js app backed by https://front-api.isu.org; every call below
is one the site itself makes in the browser.
"""
from .net import get_json

API = 'https://front-api.isu.org'
DISCIPLINES = {'figure-skating': 1, 'short-track': 3, 'speed-skating': 4}
SITE = 'https://isu-skating.com/en/{sport}/events/eventdetail/{slug}/'

def _data(r):
    if r.get('status') != 200: raise ValueError(f"ISU API error: {r.get('message')}")
    return r.get('data') or []

def events(sport, season):
    """All ISU-level events of one discipline in a season ('2026/2027')."""
    out, seen = [], set()
    for state in ('Live', 'On', 'Finished'):
        for page in range(1, 40):
            r = get_json(f'{API}/events/list', data={'discipline_id': DISCIPLINES[sport], 'state': state,
                                                     'page': page, 'pagesize': 50, 'event_level': 'ISU'})
            rows = r.get('data') or []
            for e in rows:
                if e['season'] == season and e['event_id'] not in seen:
                    seen.add(e['event_id']); out.append(e)
            older = rows and all(e['season'] < season for e in rows)
            if r.get('is_next_page') != 'Y' or older: break
    return sorted(out, key=lambda e: e['from_date_utc'])

def schedule(slug):
    r = get_json(f'{API}/events/getschedule/{slug}')
    return (r.get('data') or {}).get('value') or []

def rounds(event_result_id):
    return _data(get_json(f'{API}/events/get-event-result-round', data={'event_result_id': str(event_result_id)}))

def heats_st(event_result_id, round_id):
    """Short track heats with competitors, laps and qualification codes."""
    return _data(get_json(f'{API}/events/get-event-result-round-heats-stk-single',
                          form={'event_result_id': event_result_id, 'event_result_round_id': round_id, 'country_code': ''}))
