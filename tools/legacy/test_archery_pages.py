import hashlib,json,re
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from archery_pages import ROOT,render,EVENTS,AXES,page,results
class Doc(HTMLParser):
 def __init__(self,t):
  super().__init__();self.ids=[];self.links=[];self.feed(t)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag in ('a','link','script'):
   u=a.get('href',a.get('src'))
   if u:self.links.append(u)
files=list(ROOT.glob('olarchery*.html'));docs={p.name:Doc(p.read_text(encoding='utf-8')) for p in files}
for p in files:
 d=docs[p.name];assert len(d.ids)==len(set(d.ids)),p
 for href in d.links:
  u=urlsplit(href)
  if u.scheme or u.netloc:continue
  target=ROOT/unquote(u.path) if u.path else p
  if not target.exists() and target.name in ('index.html','la28-korea-squad.html'):continue
  assert target.exists(),(p,href)
  if u.fragment:assert unquote(u.fragment) in (docs.get(target.name) or Doc(target.read_text(encoding='utf-8'))).ids,(p,href)
d=json.loads((ROOT/'data/archery-pathways.json').read_text(encoding='utf-8'))
assert len(d['results'])==162
for c in EVENTS:
 for k,_ in AXES:
  assert 'event-'+c in docs[page(k)].ids
  for row in re.findall(r'<tr id="record-.*?</tr>',results(d,c,k)):
   assert row in (ROOT/page(k)).read_text(encoding='utf-8')
   assert row in (ROOT/('olarchery-ev-'+c+'.html')).read_text(encoding='utf-8')
assert next(r for r in d['results'] if r['event']=='cw' and r['axis']=='2025-final' and r['result']=='금')['members']==['Mariana Bernal']
roster=json.loads((ROOT/'data/archery-final-roster.json').read_text(encoding='utf-8'))
assert sum(map(len,roster.values()))==32
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files};render()
assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
print('PASS: archery 162 podiums, 32 final roster, 54 destinations, anchors, shared rows, correction, idempotence')
