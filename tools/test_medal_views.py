import json,hashlib,subprocess
from pathlib import Path
from podium_tables import ROOT,Table
from check_wiki_reorganization import Doc
from urllib.parse import urlsplit,unquote
d=json.loads((ROOT/'data/medal-views.json').read_text(encoding='utf-8'))
assert len(d['golf']['records'])==18 and len(d['golf']['weights'])==9
assert len(d['judo']['weights'])==14 and len(d['wrestling']['weights'])==18
for sport,s in d.items():
 assert (ROOT/('ol'+sport+'-medals.html')).exists()
 assert len({(r['meet'],r['weight']) for r in s['records']})==len(s['records'])
 for r in s['records']:
  assert r['weight'] in s['weights'] and any(m['id']==r['meet'] for m in s['meets'])
  assert all(isinstance(r['medals'][k],list) for k in ['gold','silver','bronze'])
asian=[r for r in d['taekwondo']['records'] if r['meet']=='cu26']
assert len(asian)==16 and sum(len(p) for r in asian for p in r['medals'].values())==64
assert any(p['name']=='천위판' for r in asian for p in r['medals']['bronze'])
cache={}
def docfile(p):
 if p not in cache:cache[p]=Doc(p.read_text(encoding='utf-8'))
 return cache[p]
changed=set(subprocess.check_output(['git','-C',str(ROOT),'-c','core.autocrlf=false','diff','--name-only'],text=True).splitlines())
changed.update('ol'+s+'-medals.html' for s in d)
for p in ROOT.glob('ol*.html'):
 if p.name not in changed:continue
 if not p.name.startswith(tuple('ol'+s for s in d)):continue
 doc=docfile(p)
 assert len(doc.ids)==len(set(doc.ids)),(p.name,'duplicate ids')
 for link in doc.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  target=ROOT/unquote(u.path) if u.path else p
  assert target.exists(),(p.name,link)
  if u.fragment:
   assert unquote(u.fragment) in docfile(target).ids,(p.name,link)
print('PASS: 10 sport views; Asian Championships 64 medals; 9 majors per season; changed-page local links')
