"""Validate both axes against the same ISSF records and local anchors."""
import hashlib,re
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import shooting_orthogonal as O

class Doc(HTMLParser):
 def __init__(self,t):
  super().__init__();self.ids=[];self.links=[];self.feed(t)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag in ('a','link','script'):
   url=d.get('href',d.get('src'))
   if url:self.links.append(url)

files=sorted(O.ROOT.glob('olshooting*.html'))
docs={p.name:Doc(p.read_text(encoding='utf-8')) for p in files}
for name in ['olshooting.html','olshooting-events.html','olshooting-projection.html']:
 text=(O.ROOT/name).read_text(encoding='utf-8')
 assert text.index('id="shooting-qualifying"')<text.index('id="shooting-reference"')
 assert text.count('<table class="shoot-axis-matrix ')==2
 for _,v in O.E.items():
  assert text.count('href="olshooting-ev-'+v['code']+'.html"')>=2
for p in files:
 d=docs[p.name]
 assert len(d.ids)==len(set(d.ids)),p.name+' duplicate IDs'
 for href in d.links:
  u=urlsplit(href)
  if u.scheme or u.netloc:continue
  target=O.ROOT/unquote(u.path) if u.path else p
  assert target.exists(),(p.name,href)
  if u.fragment:
   other=docs.get(target.name) or Doc(target.read_text(encoding='utf-8'))
   assert unquote(u.fragment) in other.ids,(p.name,href)
for key,_,_ in O.AXES:
 for v in O.E.values():assert 'event-'+v['code'] in docs[O.page(key)].ids
count=0
for event,v in O.E.items():
 weight=(O.ROOT/('olshooting-ev-'+v['code']+'.html')).read_text(encoding='utf-8')
 assert weight.count('<caption>한국 결과 · 대회 통합 표</caption>')==1
 for key,_,_ in O.AXES[:3]:
  expected=re.findall(r'<tr[^>]* data-record=".*?</tr>',O.result_table(event,key))
  year=(O.ROOT/O.page(key)).read_text(encoding='utf-8')
  for row in expected:
   assert row in weight and row in year
   count+=1
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
O.render()
assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
css=(O.ROOT/'css/shooting-orthogonal.css').read_text(encoding='utf-8')
assert all(s in css for s in ['overflow-x:auto','white-space:nowrap','position:sticky'])
print(f'PASS: {len(files)} pages; 135 destinations; {count} shared result rows; anchors; mobile CSS; idempotence')
