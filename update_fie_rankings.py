"""Fetch all six official senior team rankings; publish only a complete validated snapshot."""
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://fie.org/api/fie/'
# FIE continental zones, including the European federations ISR, TUR, GEO, ARM, AZE.
GROUPS = {
    'Asia-Oceania': 'AFG AUS BAN BRN BRU CAM CHN FIJ HKG INA IND IRI IRQ JOR JPN KAZ KGZ KOR KSA KUW LAO LBN MAC MAS MDV MGL MYA NEP NZL OMA PAK PHI PLE PNG PRK QAT SAM SGP SOL SRI SYR THA TJK TKM TLS TPE UAE UZB VAN VIE YEM',
    'Europe': 'ALB AND ARM AUT AZE BEL BIH BLR BUL CRO CYP CZE DEN ESP EST FIN FRA GBR GEO GER GRE HUN IRL ISL ISR ITA KOS LAT LIE LTU LUX MDA MKD MLT MNE MON NED NOR POL POR ROU RUS SLO SMR SRB SUI SVK SWE TUR UKR',
    'Africa': 'ALG ANG BEN BOT BUR BDI CAF CGO CHA CIV CMR COD COM CPV DJI EGY ERI ETH GAB GAM GEQ GHA GBS GUI KEN LBR LBA LES MAD MAR MAW MLI MOZ MRI MTN NAM NGR NIG RSA RWA SEN SEY SLE SOM SSD STP SUD SWZ TAN TOG TUN UGA ZAM ZIM',
    'America': 'ANT ARG ARU BAH BAR BER BIZ BOL BRA CAN CAY CHI COL CRC CUB DMA DOM ECU ESA GRN GUA GUY HAI HON IVB JAM MEX NCA PAN PAR PER PUR SKN LCA SUR TTO URU USA VIN VEN',
}
ZONES = {code: zone for zone, codes in GROUPS.items() for code in codes.split()}

def fetch(path, query=None):
    url = BASE + path + ('?' + urlencode(query) if query else '')
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'KoreaOlympics-ranking-monitor/1.0', 'Accept': 'application/json'}), timeout=45) as response:
                return json.load(response), url
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

def main():
    seasons, _ = fetch('competitions/seasons')
    season = max(int(x['label']) for x in seasons['items'])
    events = []
    for gender, label in [('M', '남자'), ('F', '여자')]:
        for weapon, name in [('F', '플뢰레'), ('E', '에페'), ('S', '사브르')]:
            rows, page = [], 1
            while True:
                data, source = fetch('fencers/ranking', dict(season=season, weapon=weapon, gender=gender, category='S', type='E', page=page, pageSize=100))
                batch = data['items']
                if not batch:
                    raise ValueError('Empty or truncated ranking')
                rows.extend(batch)
                if len(rows) >= data['totalFound']:
                    break
                page += 1
                if page > 10:
                    raise ValueError('Unexpected pagination')
            teams = []
            for row in rows:
                code = row['countryCode']
                rank, points = int(row['rank']), float(row['points'])
                if code not in ZONES or rank < 1 or points < 0 or not math.isfinite(points):
                    raise ValueError(f'Invalid or unmapped team: {code}')
                teams.append(dict(code=code, country=row['country'], rank=rank, points=points, zone=ZONES[code]))
            if len(teams) < 24 or len({t['code'] for t in teams}) != len(teams) or not any(t['code'] == 'KOR' for t in teams):
                raise ValueError('Incomplete ranking')
            if any(a['rank'] > b['rank'] or a['points'] < b['points'] for a, b in zip(teams, teams[1:])):
                raise ValueError('Invalid ranking order')
            events.append(dict(id=weapon.lower() + gender.lower(), label=label + ' ' + name, source=source, teams=teams))
    snapshot = dict(schemaVersion=1, fetchedAt=datetime.now(timezone.utc).isoformat(), season=season, rankingType='official-senior-team', zoneSource='https://fie.org/fie/structure/federations', events=events)
    directory = ROOT / 'data'
    directory.mkdir(exist_ok=True)
    content = json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n'
    path = directory / 'fie-team-ranking.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(content, encoding='utf-8')
    os.replace(temp, path)
    history = directory / 'fie-team-history'
    history.mkdir(exist_ok=True)
    # One validated snapshot per ISO week.
    now = datetime.now(timezone.utc).isocalendar()
    (history / f'{now.year}-W{now.week:02}.json').write_text(content, encoding='utf-8')
    print(f'Validated {len(events)} team rankings for season {season}')

if __name__ == '__main__':
    main()
