"""Short track advancement: read the official qualification rule and project the next round.

ISU publishes, per round, a sentence such as
  "The first and second placed skaters from each race and up to a maximum of six
   fastest third place skaters qualify for Heats."
We parse it, rank qualifiers the way the ISU does (place, then time) and, while the
official draw is not yet published, distribute them over the next round's races
serpentine-style. The projection is labelled as such everywhere it is shown.
"""
import math, re

WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
         'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'first': 1, 'second': 2, 'third': 3, 'fourth': 4}

def _num(w):
    return int(w) if w.isdigit() else WORDS.get(w.lower())

def parse_rule(text):
    """-> {'places': n, 'extra': m, 'extra_place': p, 'next': 'Heats'} or None."""
    if not text: return None
    t = ' '.join(text.split())
    m = re.search(r'The ((?:first|second|third|fourth)(?:,? (?:and )?(?:first|second|third|fourth))*) placed', t, re.I)
    if not m: return None
    places = max(_num(w) for w in re.findall(r'first|second|third|fourth', m.group(1), re.I))
    extra, extra_place = 0, places + 1
    e = re.search(r'maximum of (\w+) fastest (\w+) place', t, re.I)
    if e: extra, extra_place = _num(e.group(1)) or 0, _num(e.group(2)) or places + 1
    nxt = re.search(r'qualify for (?:the )?(.+?)\.?$', t, re.I)
    return {'places': places, 'extra': extra, 'extra_place': extra_place, 'next': nxt.group(1) if nxt else ''}

def _time(v):
    try:
        p = [float(x) for x in str(v).split(':')]
        return p[0] * 60 + p[1] if len(p) == 2 else p[0]
    except ValueError:
        return math.inf

def qualifiers(heats, rule):
    """Rank qualifiers from finished heats.

    Once the ISU has stamped codes (Q = by place, q = fastest loser, ADV = advanced by
    referee) those are authoritative; the rule text is only used before that.
    """
    everyone = [c for h in heats for c in h['competitors']]
    if any(c.get('qual') for c in everyone):
        direct = [c for c in everyone if c.get('qual') in ('Q', 'ADV')]
        fastest = [c for c in everyone if c.get('qual') == 'q']
    elif rule:
        direct = [c for c in everyone if c.get('rank') and c['rank'] <= rule['places']]
        fastest = sorted((c for c in everyone if c.get('rank') == rule['extra_place']),
                         key=lambda c: _time(c.get('time')))[:rule['extra']]
    else:
        return []
    direct.sort(key=lambda c: (c.get('rank') or 99, _time(c.get('time'))))
    fastest.sort(key=lambda c: _time(c.get('time')))
    return direct + fastest

def distribute(ranked, races):
    """Serpentine seeding of ranked qualifiers into `races` races."""
    out = [[] for _ in range(max(races, 1))]
    for i, c in enumerate(ranked):
        lap, pos = divmod(i, len(out))
        out[pos if lap % 2 == 0 else len(out) - 1 - pos].append(c)
    return out

def project(heats, rule_text, next_round_heats=None, per_race=4):
    rule = parse_rule(rule_text)
    q = qualifiers(heats, rule)
    if not q: return None
    races = len(next_round_heats) if next_round_heats else math.ceil(len(q) / per_race)
    return {'rule': rule, 'qualified': q, 'races': distribute(q, races)}
