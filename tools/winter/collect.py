"""Collect winter-season schedules and results into data/winter/.

  python -m tools.winter.collect            # quick: live events and events within ±1 day
  python -m tools.winter.collect --full     # whole season calendar + every event's sessions

Outputs (all UTC timestamps; pages convert to KST):
  data/winter/calendar.json        season calendar for every sport
  data/winter/events/<id>.json     sessions, rounds, heats, projections for one event
  data/winter/korea.json           every Korean result found, newest first
  data/winter/status.json          per-source success/failure for the admin page
"""
import argparse, datetime as dt, json, re, sys, traceback
from collections import Counter
from pathlib import Path
from . import isu, fis, bracket, speed, ibu, sliding

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'winter'
KOR = 'KOR'
ISU_SPORTS = ('short-track', 'figure-skating')
FIS_SPORTS = tuple(fis.SECTORS)          # alpine, cross-country, ski-jumping, nordic-combined, freestyle, snowboard
RACE_SPORTS = FIS_SPORTS + ('biathlon',)  # race-list sports: one results table per race
CALENDAR_ONLY = ('bobsleigh', 'skeleton', 'luge')
# main result column per race table, first match wins
MAIN = ('Tot. Time', 'Tot. Points', 'Total Points', 'Time', 'Result', '기록', 'Points')

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
    return {'rank': c.get('final_rank'), 'name': s.get('full_name') or team.get('name') or c.get('started_for_nf_country_name') or '',
            'noc': c.get('started_for_nf_code') or s.get('nationality_code') or '',
            'time': c.get('final_result') or '', 'qual': c.get('qualification_code') or '',
            'status': c.get('result_status') or '', 'record': c.get('record_flag') or '',
            'bib': c.get('bib_number'), 'lane': c.get('starting_position'), 'slug': s.get('slug', '')}

def short_track_results(ev, sessions):
    """Rounds and heats for every distance seen in the schedule; adds projections."""
    out = {}
    for rid in dict.fromkeys(s['event_result_id'] for s in sessions if s.get('event_result_id')):
        title, kind = next((s['title'], s.get('type')) for s in sessions if s['event_result_id'] == rid)
        rounds = sorted(isu.rounds(rid), key=lambda r: r.get('date') or '')
        dist = {'title': title, 'rounds': []}
        for r in rounds:
            heats = []
            if r.get('status') in ('Live', 'Finished'):
                try:
                    fetch = isu.heats_st_team if kind == 'Couples' else isu.heats_st
                    for h in fetch(rid, r['event_result_round_id']):
                        heats.append({'name': h['name'], 'status': h.get('status'), 'official': h.get('result_status'),
                                      'competitors': sorted((competitor(c) for c in h.get('event_result_round_heats_competitors') or []),
                                                            key=lambda c: (c['rank'] is None, c['rank'] or 0))})
                except Exception as exc:
                    heats = [{'name': '수집 실패', 'error': str(exc)[:200], 'competitors': []}]
            dist['rounds'].append({'id': r['event_result_round_id'], 'name': r['name'], 'status': r.get('status'),
                                   'start_utc': r.get('date'), 'rule': r.get('qualification_rule') or '', 'heats': heats})
        out[str(rid)] = dist
    counts = heat_counts(out)
    for dist in out.values():
        add_projections(dist, counts)
    return out

def round_key(name):
    """'Rep. Quarterfinals' / 'Rep Quarterfinals' -> 'rep quarterfinals'; 'Final A' / 'Final' -> 'finals'."""
    k = ' '.join(name.lower().replace('.', '').split())
    return 'finals' if k in ('final', 'final a', 'finals') else k

def heat_counts(event_dists):
    """{(distance title, round key): number of races} from this event and earlier events this season.

    The race count of a round is fixed by the competition format, so a round that has
    already been raced (same distance elsewhere this season, or another distance of the
    same length class here) tells us how many races the projected round will have."""
    seen = {}
    files = [load(f, {}) for f in sorted((OUT / 'events').glob('isu-*.json'))]
    sources = [d.get('results') or {} for d in files if (d.get('event') or {}).get('sport') == 'short-track'] + [event_dists]
    for results in sources:
        for dist in results.values():
            for r in dist.get('rounds', []):
                n = len([h for h in r.get('heats', []) if h.get('competitors')])
                if n and round_key(r['name']) != 'finals':
                    seen.setdefault((dist['title'], round_key(r['name'])), Counter())[n] += 1
    return {k: c.most_common(1)[0][0] for k, c in seen.items()}

def races_for(dist_title, target_key, counts, qualified):
    if target_key == 'finals':
        return 1  # the rule's "qualify for Final A": one race
    if (dist_title, target_key) in counts:
        return counts[(dist_title, target_key)]
    long_race = '1500' in dist_title
    similar = [(gender_of(title) == gender_of(dist_title), n) for (title, key), n in counts.items()
               if key == target_key and ('1500' in title) == long_race]  # same round, same length class
    if similar:
        return max(similar)[1]  # prefer the same gender
    if target_key in ('semifinals', 'rep semifinals'):
        return 2
    return max(1, -(-qualified // (6 if long_race else 4)))

def gender_of(title):
    return title.split()[0]

def add_projections(dist, counts):
    """Project each upcoming round from every round that feeds it.

    A round can be fed by several earlier rounds (e.g. the quarterfinals take the heat
    qualifiers plus the repechage-semifinal winners), so qualifiers are pooled per target
    round and the projection is attached to the most recent finished feeder. Official
    heats are used as soon as the ISU publishes them; otherwise the number of races comes
    from races_for(), never from a plain head count."""
    by_key = {round_key(r['name']): r for r in dist['rounds']}
    feeders = {}
    for r in dist['rounds']:
        r.pop('projection', None)
        rule = bracket.parse_rule(r['rule'])
        if rule:
            feeders.setdefault(round_key(rule['next']), []).append((r, rule))
    for key, group in feeders.items():
        done = [(r, rule) for r, rule in group if r['status'] == 'Finished' and r['heats']]
        if not done: continue
        ranked = [c for r, rule in done for c in bracket.qualifiers(r['heats'], rule)]
        if not ranked: continue
        target = by_key.get(key)
        official_heats = [h for h in (target or {}).get('heats', []) if h.get('competitors') and h['name'] != 'Final B']
        official = bool(official_heats)
        n = len(official_heats) if official else races_for(dist['title'], key, counts, len(ranked))
        latest = max(done, key=lambda x: x[0].get('start_utc') or '')[0]
        latest['projection'] = {
            'next': target['name'] if target else done[0][1]['next'], 'official_draw_published': official,
            'pending': [r['name'] for r, _ in group if (r, _) not in done],
            'qualified': [{k: c[k] for k in ('name', 'noc', 'rank', 'time', 'qual')} for c in ranked],
            'races': [[c['name'] + ' (' + c['noc'] + ')' for c in race] for race in bracket.distribute(ranked, n)]}

def figure_results(ev, sessions):
    out = {}
    event_id = ev['id'].split('-', 1)[1]
    for rid in dict.fromkeys(s['event_result_id'] for s in sessions if s.get('event_result_id')):
        title, kind = next((s['title'], s.get('type')) for s in sessions if s['event_result_id'] == rid)
        rows = []
        fetch = isu.results_fs_team if kind == 'Couples' else isu.results_fs
        for c in fetch(event_id, rid):
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
                data['results'] = short_track_results(ev, sessions)
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

def main_result(row):
    cells = row.get('cells') or {}
    return next((cells[k] for k in MAIN if cells.get(k)), '')

def collect_races(sport, ev, list_races, get_results, mode, status, today):
    """FIS / IBU events: race list + one results table per race (data/winter/events/<id>.json)."""
    path = OUT / 'events' / f"{ev['id']}.json"
    active = is_active(ev, today)
    started = ev['start'] <= today.isoformat()
    if ev.get('state') == 'Cancelled' or not (active or (mode == 'full' and started and not path.exists())):
        return
    try:
        prev = load(path, {}).get('results', {})
        races = list_races()
        results = {}
        for r in races:
            key = str(r['id'])
            if r.get('cancelled'):
                continue
            if r.get('has_results') or r.get('live'):
                try:
                    res = get_results(r['id'])
                except Exception as exc:
                    res = prev.get(key) or {'columns': [], 'rows': [], 'error': f'{type(exc).__name__}: {exc}'[:200]}
                if not res.get('rows') and prev.get(key, {}).get('rows'):
                    res = prev[key]  # a transient empty page must not wipe earlier results
            else:
                res = {'columns': [], 'rows': []}
            results[key] = {**res, 'title': res.get('title') or r['name'], 'start_utc': r.get('start_utc') or r.get('date') or None,
                            'gender': r.get('gender', ''), 'live': bool(r.get('live')), 'runs': r.get('runs', []),
                            'status': r.get('status') or ('Finished' if res.get('rows') and not res.get('start_list') else '')}
        sessions = [{'start_utc': x['start_utc'], 'title': x['title'], 'round': ''} for x in results.values() if x['start_utc']]
        korea = [{'event_id': ev['id'], 'sport': sport, 'event': ev['name'], 'distance': x['title'], 'round': '', 'heat': '',
                  'start_utc': x['start_utc'], 'rank': c.get('rank'), 'name': c['name'], 'noc': c['noc'], 'time': main_result(c),
                  'qual': '', 'status': c.get('status', '')}
                 for x in results.values() if not x.get('start_list') for c in x.get('rows', []) if c.get('noc') == KOR]
        save(path, {'event': ev, 'checked_at': now().isoformat(), 'sessions': sessions, 'results': results, 'korea': korea})
        status[f"{sport}:{ev['id']}"] = {'ok': True, 'at': now().isoformat()}
    except Exception as exc:
        status[f"{sport}:{ev['id']}"] = {'ok': False, 'at': now().isoformat(), 'error': f'{type(exc).__name__}: {exc}'[:300]}
        traceback.print_exc()

def podium_race(race):
    """Final classification of a FIS / IBU race (no qualification, training or start list)."""
    if race.get('start_list') or re.search(r'Qualification|Training|Heats|Prologue|\bPR\b', race.get('title', ''), re.I):
        return None
    top = [r for r in race.get('rows', []) if r.get('rank') in (1, 2, 3)]
    return [{'rank': r['rank'], 'name': r['name'], 'noc': r['noc'], 'time': main_result(r)} for r in top] or None

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
            if sport in RACE_SPORTS and (item.get('start_list') or re.search(r'Qualification|Training', item.get('title', ''))):
                continue  # only final classifications go into the season podium tables
            pod = {'short-track': podium_st, 'figure-skating': podium_fs, 'speed-skating': podium_ss}.get(sport, podium_race)(item)
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
    sources = {sp: (lambda sp=sp: fis.calendar(sp, start_year), f'https://www.fis-ski.com/DB/general/calendar-results.html?sectorcode={fis.SECTORS[sp]}')
               for sp in FIS_SPORTS}
    sources['biathlon'] = (lambda: ibu.calendar(start_year), ibu.SITE)
    ibsf = {}
    def ibsf_part(sp):
        if 'all' not in ibsf: ibsf['all'] = sliding.ibsf_calendar()
        return [e for e in ibsf['all'] if e['sport'] == sp]
    sources['bobsleigh'] = (lambda: ibsf_part('bobsleigh'), sliding.IBSF)
    sources['skeleton'] = (lambda: ibsf_part('skeleton'), sliding.IBSF)
    sources['luge'] = (sliding.fil_calendar, sliding.FIL)
    for sp, (fetch, url) in sources.items():
        if mode != 'full' and sp in cal['sports'] and cal['sports'][sp].get('season') == season:
            continue  # calendars of these sources change rarely: refreshed by the twice-daily full run
        try:
            cal['sports'][sp] = {'source': url, 'checked_at': now().isoformat(), 'season': season, 'events': fetch()}
            status[sp] = {'ok': True, 'at': now().isoformat()}
        except Exception as exc:
            failed += 1
            status[sp] = {'ok': False, 'at': now().isoformat(), 'error': f'{type(exc).__name__}: {exc}'[:300]}
            traceback.print_exc()
    today = now().date()
    for sp in RACE_SPORTS:
        for ev in (cal['sports'].get(sp) or {}).get('events', []):
            if sp == 'biathlon':
                collect_races(sp, ev, lambda ev=ev: ibu.races(ev['ibu_id']), ibu.results, mode, status, today)
            else:
                collect_races(sp, ev, lambda ev=ev, sp=sp: fis.races(sp, ev['id'].split('-', 1)[1], start_year),
                              lambda rid, sp=sp: fis.results(sp, rid), mode, status, today)
    cal['season'] = season
    save(OUT / 'calendar.json', cal)
    for sport in (*ISU_SPORTS, 'speed-skating', *RACE_SPORTS):
        if sport in cal['sports']:
            build_season(sport, cal)
    korea = []
    for f in sorted((OUT / 'events').glob('*.json')):
        korea += load(f, {}).get('korea', [])
    korea.sort(key=lambda r: r.get('start_utc') or '', reverse=True)
    save(OUT / 'korea.json', {'season': season, 'rows': korea})
    active = sorted(e['id'] for sp in ('short-track', 'speed-skating', 'figure-skating', *RACE_SPORTS) for e in cal['sports'].get(sp, {}).get('events', [])
                    if e.get('state') != 'Cancelled' and is_active(e, today))
    save(OUT / 'status.json', {'updated_at': now().isoformat(), 'mode': mode, 'active': active, 'sources': status})
    print(f'{mode}: {sum(len(s["events"]) for s in cal["sports"].values())} events, {len(korea)} Korean results, {failed} source failures')
    return 1 if failed >= len(ISU_SPORTS) + 1 + len(sources) else 0

if __name__ == '__main__':
    sys.exit(main())
