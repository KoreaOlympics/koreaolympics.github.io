"""One-off source probe run in GitHub Actions: saves raw federation pages so parsers can be written against real markup."""
import re, json, pathlib, traceback, sys
sys.path.insert(0, '.')
from tools.winter.net import request
OUT = pathlib.Path('probe-out'); OUT.mkdir(exist_ok=True)
def get(name, url, **kw):
    try:
        t = request(url, **kw)
    except Exception as e:
        t = f'ERROR {type(e).__name__}: {e}'
    (OUT / name).write_text(t)
    print(name, len(t), url, flush=True)
    return t
CAL = ('https://www.fis-ski.com/DB/general/calendar-results.html?eventselection=&place=&sectorcode={s}&seasoncode={c}'
       '&categorycode={cat}&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-{c}&saveselection=-1&seasonselection=')
for s in ('AL', 'CC', 'JP', 'NK', 'FS', 'SB'):
    for c in ('2026', '2027'):
        t = get(f'fis-cal-{s}-{c}.html', CAL.format(s=s, c=c, cat='WC'))
        ids = re.findall(r'id="(\d{4,6})"', t)
        if ids:
            for j, eid in enumerate([ids[len(ids) // 2]] if c == '2026' else ids[:1]):
                ev = get(f'fis-ev-{s}-{c}.html', f'https://www.fis-ski.com/DB/general/event-details.html?sectorcode={s}&eventid={eid}&seasoncode={c}')
                races = list(dict.fromkeys(re.findall(r'raceid=(\d+)', ev)))
                for i, r in enumerate(races[:3]):
                    get(f'fis-res-{s}-{c}-{i}.html', f'https://www.fis-ski.com/DB/general/results.html?sectorcode={s}&raceid={r}')
get('fis-live-index.html', 'https://live.fis-ski.com/')
B = 'https://www.biathlonresults.com/modules/sportapi/api/'
ev = get('ibu-events-2526.json', B + 'Events?SeasonId=2526&Level=1')
get('ibu-events-2627.json', B + 'Events?SeasonId=2627&Level=1')
try:
    e0 = json.loads(ev)[3]['EventId']
    comp = get('ibu-comp.json', B + f'Competitions?EventId={e0}')
    r0 = json.loads(comp)[0]['RaceId']
    get('ibu-results.json', B + f'Results?RaceId={r0}')
except Exception: traceback.print_exc()
for n, u in [('ibsf-home.html', 'https://www.ibsf.org/en/'), ('ibsf-races.html', 'https://www.ibsf.org/en/races-results'),
             ('ibsf-calendar.html', 'https://www.ibsf.org/en/calendar'),
             ('fil-home.html', 'https://www.fil-luge.org/en'), ('fil-results.html', 'https://www.fil-luge.org/en/results'),
             ('fil-calendar.html', 'https://www.fil-luge.org/en/calendar')]:
    t = get(n, u)
    for js in list(dict.fromkeys(re.findall(r'src="([^"]+\.js[^"]*)"', t)))[:15]:
        if js.startswith('//'): js = 'https:' + js
        elif js.startswith('/'): js = 'https://' + u.split('/')[2] + js
        if js.startswith('http'):
            get(n + '.' + re.sub(r'\W', '_', js)[-60:] + '.js', js)
