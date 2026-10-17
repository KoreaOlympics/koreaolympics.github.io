"""Validate imported medal tables and keep non-Olympic weights separate."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
d=json.loads((ROOT/'data/boxing-wikipedia-2025.json').read_text(encoding='utf-8'))
rows=d['medalists']
assert collections.Counter(r['stage'] for r in rows)=={'world':80,'cup1':72,'cup2':80,'final':47}
assert len({(r['stage'],r['weight'],r['athlete'],r['result']) for r in rows})==279
world=[r for r in rows if r['stage']=='world']
assert len({r['weight'] for r in world})==20
for c in {r['weight'] for r in world}:
 assert collections.Counter(r['result'] for r in world if r['weight']==c)=={'금':1,'은':1,'동':2}
assert all(r['athlete'] and r['country'] for r in rows)
assert any(r['athlete']=='Im Ae-ji' and r['weight']=='w54' and r['result']=='동' for r in world)
assert any(r['athlete']=='Bak Chorong' and r['weight']=='w48' and r['result']=='동' for r in rows)
data=json.loads((ROOT/'data/boxing-pathways.json').read_text(encoding='utf-8'))
assert not any(r['athlete']=='박초롱' and r['weight']=='w51' and r['axis']=='2025-cup' for r in data['results'])
assert not data['qualifiers'], '2025 records must not manufacture LA28 qualifiers'
print('PASS: 279 records, 20 world weights, medals, countries, Korean records, original weights, no invented quota')
