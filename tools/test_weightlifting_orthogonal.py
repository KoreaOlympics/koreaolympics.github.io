import json,re,subprocess,sys,hashlib
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/weightlifting-pathways.json').read_text(encoding='utf-8'))
assert len(data['weights'])==12
assert [e['period'] for e in data['events']].count(1)==6
assert [e['period'] for e in data['events']].count(2)==4
for e in data['events']:
 s=(ROOT/f"olweightlifting-{e['id']}.html").read_text(encoding='utf-8')
 for w,n in data['weights']: assert f'id="{w}"' in s
 assert not e['results']
for p in ROOT.glob('olweightlifting*.html'):
 s=p.read_text(encoding='utf-8')
 for href in re.findall(r'(?:href|src)="([^"]+)"',s):
  u=urlsplit(href)
  if u.scheme or not u.path: continue
  target=ROOT/u.path
  assert target.exists() or u.path in ('index.html','./index.html','la28-korea-squad.html','./la28-korea-squad.html'),(p.name,href)
  if target.exists() and u.fragment and target.suffix=='.html': assert f'id="{u.fragment}"' in target.read_text(encoding='utf-8'),(p.name,href)
paths=list(ROOT.glob('olweightlifting*.html'))
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,str(ROOT/'tools/weightlifting_orthogonal.py')],check=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
print('PASS: 120 intersections, 6+4 events, local links/anchors, idempotent render')
