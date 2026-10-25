"""Collect winter-season schedules and results into data/winter/.

  python -m tools.winter.collect            # quick: live events and events within ±1 day
  python -m tools.winter.collect --full     # whole season calendar + every event's sessions

Outputs (all UTC timestamps; pages convert to KST):
  data/winter/calendar.json        season calendar for every sport
  data/winter/events/<id>.json     sessions, rounds, heats, projections for one event
  data/winter/korea.json           every Korean result found, newest first
  data/winter/status.json          per-source success/failure for the admin page
"""
import argparse, datetime as dt, json, sys, traceback
from pathlib import Path
from . import isu, fis, bracket, speed

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'winter'
KOR = 'KOR'
ISU_SPORTS = ('short-track', 'figure-skating')

def now():
    return dt.datetime.now(dt.timezone.utc)

def season_of(day):
    y = day.year if day.month >= 7 else day.year - 1
    return y, f'{y}/{y + 1}'

def load(path, default):
    try: return json.loads(path.read_text())
    except Exception: return default

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + '\n'
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
        return True
    return False

def isu_event(sport, e):
    return {'id': f"isu-{e['event_id']}", 'sport': sport, 'source': 'ISU', 'season': e.get('season'), 'slug': e.get('slug') or slug_from(e),
            'name': e['name'], 'category': e.get('event_sub_type_name', ''),
            'start': e['from_date'][:10], 'end': e['to_date'][:10],
            'start_utc': e['from_date_utc'], 'end_utc': e['to_date_utc'], 'tz': e.get('time_zone'),
            'city': e.get('city', ''), 'country': e.get('country_code', ''), 'state': e.get('state', ''),
            'live': e.get('live_skater', ''),
            'url': isu.SITE.format(sport=sport, slug=e.get('slug') or slug_from(e))}

def slug_from(e):
    # events/list carries the slug inside button URLs (".../eventdetail/<slug>")
    for k in ('button_2_url', 'button_1_url', 'button_3_url'):
        u = e.get(k) or ''
        if '/eventdetail/' in u: return u.rstrip('/').split('/eventdetail/')[1].split('/')[0].split('?')[0]
    return ''

def competitor(c):
    s = c.get('skaters') or {}
    team = c.get('skaters_team') or {}
    return {'rank': c.get('final_rank'), 'name': s.get('full_name') or team.get('name') or '',
            'noc': c.get('started_for_nf_code') or s.get('nationality_code') or '',
            'time': c.get('final_result') or '', 'qual': c.get('qualification_code') or '',
            'status': c.get('result_status') or '', 'record': c.get('record_flag') or '',
            'bib': c.get('bib_number'), 'lane': c.get('starting_position'), 'slug': s.get('slug', '')}

def short_track_results(ev, sessions):
    """Rounds and heats for every distance seen in the schedule; adds projections."""
    out = {}
    for rid in dict.fromkeys(s['event_result_id'] for s in sessions if s.get('event_result_id')):
        title = next(s['title'] for s in sessions if s['event_result_id'] == rid)
        rounds = sorted(isu.rounds(rid), key=lambda r: r.get('date') or '')
        dist = {'title': title, 'rounds': []}
        for r in rounds:
            heats = []
            if r.get('status') in ('Live', 'Finished'):
                try:
                    for h in isu.heats_st(rid, r['event_result_round_id']):
                        heats.append({'name': h['name'], 'status': h.get('status'), 'official': h.get('result_status'),
                                      'competitors': sorted((competitor(c) for c in h.get('event_result_round_heats_competitors') or []),
                                                            key=lambda c: (c['rank'] is None, c['rank'] or 0))})
                except Exception as exc:
                    heats = [{'name': '수집 실패', 'error': str(exc)[:200], 'competitors': []}]
            dist['rounds'].append({'id': r['event_result_round_id'], 'name': r['name'], 'status': r.get('status'),
                                   'start_utc': r.get('date'), 'rule': r.get('qualification_rule') or '', 'heats': heats})
        add_projections(dist)
        out[str(rid)] = dist
    return out

ORDER = ['Preliminaries', 'Heats', 'Rep. Heats', 'Rep. Quarterfinals', 'Quarterfinals', 'Semifinals', 'Final B', 'Final A']

def add_projections(dist):
    """For each finished round, project the round named in its rule if that round has no heats yet."""
    by_name = {r['name'].lower().replace('.', ''): r for r in dist['rounds']}
    for r in dist['rounds']:
        if r['status'] != 'Finished' or not r['heats']: continue
        rule = bracket.parse_rule(r['rule'])
        if not rule: continue
        target = by_name.get(rule['next'].lower().replace('.', ''))
        official = bool(target and any(h['competitors'] for h in target['heats']))
        proj = bracket.project(r['heats'], r['rule'], target['heats'] if official else None,
                               per_race=6 if '1500' in dist['title'] else 4)
        if proj:
            r['projection'] = {'next': rule['next'], 'official_draw_published': official,
                               'qualified': [{k: c[k] for k in ('name', 'noc', 'rank', 'time', 'qual')} for c in proj['qualified']],
                               'races': [[c['name'] + ' (' + c['noc'] + ')' for c in race] for race in proj['races']]}

def figure_results(ev, sessions):
    out = {}
    event_id = ev['id'].split('-', 1)[1]
    for rid in dict.fromkeys(s['event_result_id'] for s in sessions if s.get('event_result_id')):
        title = next(s['title'] for s in sessions if s['event_result_id'] == rid)
        rows = []
        for c in isu.results_fs(event_id, rid):
            sk = c.get('skaters') or c.get('skaters_team') or {}
            segs = {}
            for r in c.get('event_result_round_competitors') or []:
                rnd = r.get('event_result_round') or {}
                segs[r.get('code') or rnd.get('code') or rnd.get('name', '')] = {
                    'name': rnd.get('name', ''), 'rank': r.get('rank'), 'total': r.get('total_points') or '',
                    'tes': r.get('technical_score') or '', 'pcs': r.get('component_score') or '', 'status': rnd.get('status', '')}
            rows.append({'rank': c.get('final_rank'), 'name': sk.get('full_name') or sk.get('name') or '',
                         'noc': c.get('started_for_nf_code') or sk.get('nationality_code') or '',
                         'points': c.get('final_points') or '', 'status': c.get('participant_status_name') or '', 'segments': segs})
        rows.sort(key=lambda r: (r['rank'] is None, r['rank'] or 0, -float(next((x['total'] for x in r['segments'].values() if x['total']), 0) or 0)))
        order = []
        for r in rows:
            for code, sg in r['segments'].items():
                if code not in order: order.append(code)
        out[str(rid)] = {'title': title, 'segments': order, 'rows': rows}
    return out

def korea_rows_figure(ev, results):
    rows = []
    for cat in results.values():
        for r in cat['rows']:
            if r['noc'] != KOR: continue
            done = [(k, v) for k, v in r['segments'].items() if v['total']]
            last = done[-1] if done else (None, {})
            rows.append({'event_id': ev['id'], 'sport': ev['sport'], 'event': ev['name'], 'distance': cat['title'],
                         'round': last[1].get('name', ''), 'heat': '', 'start_utc': None, 'rank': r['rank'] or last[1].get('rank'),
                         'name': r['name'], 'noc': r['noc'], 'time': r['points'] or last[1].get('total', ''),
                         'qual': '', 'status': '', 'segments': {k: v['total'] for k, v in r['segments'].items()}})
    return rows

def korea_rows(ev, results):
    rows = []
    for dist in results.values():
        for r in dist['rounds']:
            for h in r['heats']:
                for c in h['competitors']:
                    if c['noc'] == KOR:
                        rows.append({'event_id': ev['id'], 'sport': ev['sport'], 'event': ev['name'], 'distance': dist['title'],
                                     'round': r['name'], 'heat': h['name'], 'start_utc': r.get('start_utc'), **c})
    return rows

def merge_previous(sport, season, events):
    """ISU's events/list sometimes drops an event (seen with an in-progress Grand Prix);
    keep anything we saw earlier this season so it never disappears from the calendar."""
    prev = load(OUT / 'calendar.json', {}).get('sports', {}).get(sport, {}).get('events', [])
    prev += [d['event'] for f in sorted((OUT / 'events').glob('isu-*.json'))
             if (d := load(f, {})).get('event', {}).get('sport') == sport]
    seen = {e['id'] for e in events}
    today = now().date().isoformat()
    for e in prev:
        if e['id'] not in seen and e.get('season', season) == season and e['start'] >= f"{season[:4]}-07-01":
            seen.add(e['id'])
            e = dict(e, state='Finished' if e['end'] < today else e.get('state', ''))
            events.append(e)
    return sorted(events, key=lambda e: e['start'])

def collect_isu(sport, season, mode, status):
    events = merge_previous(sport, season, [isu_event(sport, e) for e in isu.events(sport, season)])
    today = now().date()
    for ev in events:
        active = is_active(ev, today)
        path = OUT / 'events' / f"{ev['id']}.json"
        if not (active or (mode == 'full' and not path.exists())) or not ev['slug']:
            continue
        try:
            sessions = [{'start_utc': s['start_time'], 'title': s['event_schedule_title'], 'round': s.get('round_information', ''),
                         'event_result_id': s.get('event_result_id'), 'round_id': s.get('event_result_round_id'),
                         'type': s.get('discipline_type', '')} for s in isu.schedule(ev['slug'])]
            data = {'event': ev, 'checked_at': now().isoformat(), 'sessions': sessions, 'results': {}}
            if sport == 'short-track' and (active or ev['state'] == 'Finished'):
                data['results'] = short_track_results(ev, [s for s in sessions if s['type'] == 'Singles'])
                data['korea'] = korea_rows(ev, data['results'])
            elif sport == 'figure-skating' and (active or ev['state'] == 'Finished'):
                data['results'] = figure_results(ev, sessions)
                last = {}
                for x in sessions:
                    last[str(x['event_result_id'])] = x['start_utc']
                data['korea'] = [dict(r, start_utc=last.get(next((k for k, c in data['results'].items() if c['title'] == r['distance']), ''), ev['start_utc']))
                                 for r in korea_rows_figure(ev, data['results'])]
            else:
                data['korea'] = []
            save(path, data)
            status[f"{sport}:{ev['id']}"] = {'ok': True, 'at': now().isoformat()}
        except Exception as exc:
            status[f"{sport}:{ev['id']}"] = {'ok': False, 'at': now().isoformat(), 'error': f'{type(exc).__name__}: {exc}'[:300]}
            traceback.print_exc()
    return events

def is_active(ev, today):
    start, end = dt.date.fromisoformat(ev['start']), dt.date.fromisoformat(ev['end'])
    return ev['state'] == 'Live' or start - dt.timedelta(days=1) <= today <= end + dt.timedelta(days=1)

def collect_speed(start_year, mode, status):
    events = [speed.event(e) for e in speed.events(start_year + 1)]
    today = now().date()
    for ev in events:
        path = OUT / 'events' / f"{ev['id']}.json"
        finished = dt.date.fromisoformat(ev['end']) < today
        if not (is_active(ev, today) or (mode == 'full' and (not path.exists() or not finished))):
            continue
        try:
            sessions = [{'start_utc': s['start'], 'title': s['title'],
                         'number': next((l['identifier'] for l in s.get('links', []) if l['type'] == 'results'), None)}
                        for s in speed.schedule(ev['isu_id'])]
            races = {}
            for c in speed.competitions(ev['isu_id']):
                if not (c.get('isOfficial') or c.get('isLive')): continue
                rows = [speed.row(r) for r in speed.results(ev['isu_id'], c['number'])]
                races[str(c['number'])] = {'title': c['title'], 'start_utc': c.get('start'), 'live': c.get('isLive'),
                                           'official': c.get('isOfficial'), 'distance': (c.get('distance') or {}).get('name'),
                                           'division': c.get('division'), 'rows': sorted(rows, key=lambda r: (r['rank'] is None, r['rank'] or 0))}
            korea = [{'event_id': ev['id'], 'sport': 'speed-skating', 'event': ev['name'], 'distance': r['title'],
                      'round': r.get('division') and f"Division {r['division']}" or '', 'heat': '', 'start_utc': r['start_utc'], **x}
                     for r in races.values() for x in r['rows'] if x['noc'] == KOR]
            save(path, {'event': ev, 'checked_at': now().isoformat(), 'sessions': sessions, 'results': races, 'korea': korea})
            status[f"speed-skating:{ev['id']}"] = {'ok': True, 'at': now().isoformat()}
        except Exception as exc:
            status[f"speed-skating:{ev['id']}"] = {'ok': False, 'at': now().isoformat(), 'error': f'{type(exc).__name__}: {exc}'[:300]}
            traceback.print_exc()
    return events

def podium_st(dist):
    """Final A (heat named 'Final' or 'Final A') ranks 1-3, once that heat has results."""
    for r in dist['rounds']:
        if 'final' not in r['name'].lower() or r['name'].lower().startswith('rep'):
            continue
        for h in r['heats']:
            if h['name'] in ('Final', 'Final A') or (r['name'] == 'Final A' and h['competitors']):
                done = h.get('status') == 'Finished' or h.get('official') == 'Official'
                top = [c for c in h['competitors'] if c.get('rank') in (1, 2, 3)]
                if done and top:
                    return [{k: c[k] for k in ('rank', 'name', 'noc', 'time')} for c in sorted(top, key=lambda c: c['rank'])]
    return None

def podium_fs(cat):
    rows = cat['rows']
    finished = rows and all(v['status'] == 'Finished' for v in rows[0]['segments'].values())
    top = [r for r in rows if r['rank'] in (1, 2, 3)]
    if finished and top:
        return [{'rank': r['rank'], 'name': r['name'], 'noc': r['noc'], 'time': r['points']} for r in top]
    return None

def podium_ss(race):
    """Division A (or undivided) official race: ranks 1-3."""
    if race.get('division') not in (None, '', 'A') or not race.get('official'):
        return None
    top = [r for r in race['rows'] if r.get('rank') in (1, 2, 3)]
    return [{k: r[k] for k in ('rank', 'name', 'noc', 'time')} for r in top] or None

def build_season(sport, cal):
    """Season summary in the shape of a Wikipedia/Namu season article: schedule, podiums, medal table."""
    events, tally, best = [], {}, {}
    for ev in (cal['sports'].get(sport) or {}).get('events', []):
        d = load(OUT / 'events' / f"{ev['id']}.json", {})
        podiums = []
        for key, item in (d.get('results') or {}).items():
            pod = {'short-track': podium_st, 'figure-skating': podium_fs, 'speed-skating': podium_ss}[sport](item)
            if sport == 'speed-skating' and item.get('division') not in (None, '', 'A'):
                continue
            podiums.append({'title': item['title'], 'podium': pod})
            for p in pod or []:
                t = tally.setdefault(p['noc'], [0, 0, 0]); t[p['rank'] - 1] += 1
            if sport == 'figure-skating':
                for r in item['rows']:
                    try: pts = float(r['points'])
                    except (TypeError, ValueError): continue
                    b = best.setdefault(item['title'], [])
                    b.append({'name': r['name'], 'noc': r['noc'], 'points': pts, 'event': ev['name'], 'event_id': ev['id']})
        events.append({k: ev.get(k) for k in ('id', 'name', 'category', 'start', 'end', 'city', 'country', 'state', 'url')} | {'podiums': podiums})
    medals = sorted(([noc, *m, sum(m)] for noc, m in tally.items()), key=lambda x: (-x[1], -x[2], -x[3], x[0]))
    out = {'sport': sport, 'season': cal.get('season'), 'events': events, 'medals': medals}
    if best:
        out['season_best'] = {k: sorted(v, key=lambda x: -x['points'])[:10] for k, v in best.items()}
    save(OUT / f'season-{sport}.json', out)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--full', action='store_true')
    args = ap.parse_args(argv)
    mode = 'full' if args.full else 'quick'
    start_year, season = season_of(now().date())
    cal = load(OUT / 'calendar.json', {'sports': {}})
    status = load(OUT / 'status.json', {}).get('sources', {})
    failed = 0
    for sport in ISU_SPORTS:
        try:
            cal['sports'][sport] = {'source': f'https://isu-skating.com/en/{sport}/events/', 'checked_at': now().isoformat(),
                                    'events': collect_isu(sport, season, mode, status)}
            status[sport] = {'ok': True, 'at': now().isoformat()}
        except Exception as exc:
            failed += 1
            status[sport] = {'ok': False, 'at': now().isoformat(), 'error': f'{type(exc).__name__}: {exc}'[:300]}
            traceback.print_exc()
    try:
        cal['sports']['speed-skating'] = {'source': 'https://live.isuresults.eu/', 'checked_at': now().isoformat(),
                                          'events': collect_speed(start_year, mode, status)}
        status['speed-skating'] = {'ok': True, 'at': now().isoformat()}
    except Exception as exc:
        failed += 1
        status['speed-skating'] = {'ok': False, 'at': now().isoformat(), 'error': f'{type(exc).__name__}: {exc}'[:300]}
        traceback.print_exc()
    if mode == 'full' or 'snowboard' not in cal['sports']:
        try:
            cal['sports']['snowboard'] = {'source': 'https://www.fis-ski.com/DB/snowboard/calendar-results.html',
                                          'checked_at': now().isoformat(), 'events': fis.calendar(start_year)}
            status['snowboard'] = {'ok': True, 'at': now().isoformat()}
        except Exception as exc:
            failed += 1
            status['snowboard'] = {'ok': False, 'at': now().isoformat(), 'error': f'{type(exc).__name__}: {exc}'[:300]}
            traceback.print_exc()
    cal['season'] = season
    save(OUT / 'calendar.json', cal)
    for sport in (*ISU_SPORTS, 'speed-skating'):
        build_season(sport, cal)
    korea = []
    for f in sorted((OUT / 'events').glob('*.json')):
        korea += load(f, {}).get('korea', [])
    korea.sort(key=lambda r: r.get('start_utc') or '', reverse=True)
    save(OUT / 'korea.json', {'season': season, 'rows': korea})
    today = now().date()
    active = sorted(e['id'] for sp in ('short-track', 'speed-skating', 'figure-skating') for e in cal['sports'].get(sp, {}).get('events', [])
                    if e.get('state') != 'Cancelled' and is_active(e, today))
    save(OUT / 'status.json', {'updated_at': now().isoformat(), 'mode': mode, 'active': active, 'sources': status})
    print(f'{mode}: {sum(len(s["events"]) for s in cal["sports"].values())} events, {len(korea)} Korean results, {failed} source failures')
    return 1 if failed == len(ISU_SPORTS) + 2 else 0

if __name__ == '__main__':
    sys.exit(main())
