"""Check major tour coverage, pair rosters, annual/event consistency and links."""
import hashlib,re,collections,sys
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import tour_pages as T
class Doc(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.links=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag in ('a','link','script'):
   u=d.get('href',d.get('src'))
   if u:self.links.append(u)
for sport in sys.argv[1:] or T.SPORTS:
 config=T.SPORTS[sport]
 files=list(T.ROOT.glob('ol'+sport+'*.html'));docs={p.name:Doc(p.read_text(encoding='utf-8')) for p in files}
 for p in files:
  d=docs[p.name];assert len(d.ids)==len(set(d.ids)),p
  for href in d.links:
   u=urlsplit(href)
   if u.scheme or u.netloc:continue
   target=T.ROOT/unquote(u.path) if u.path else p
   if not target.exists() and target.name in ('index.html','la28-korea-squad.html'):continue
   assert target.exists(),(p,href)
   if u.fragment:assert unquote(u.fragment) in (docs.get(target.name) or Doc(target.read_text(encoding='utf-8'))).ids,(p,href)
 data=T.data(sport);rows=data['results']
 assert len(rows)==(158 if sport=='badminton' else 130)
 assert not any(r['year']>2026 for r in rows)
 assert len({r['id'] for r in rows})==len(rows)
 for r in rows:
  assert r['members'] and not any('Score:' in n for n in r['members'])
  if r['event'] in ('ms','ws'):assert len(r['members'])==1,r
  if r['event'] in ('md','wd','xd'):assert len(r['members'])==2,r
 for event in config['events']:
  event_text=(T.ROOT/T.event_page(sport,event)).read_text(encoding='utf-8')
  for year in range(2025,2029):
   assert 'event-'+event in docs[T.year_page(sport,year)].ids
   annual=(T.ROOT/T.year_page(sport,year)).read_text(encoding='utf-8')
   for row in re.findall(r'<tr id="result-.*?</tr>',T.result_table(sport,event,year)):
    assert row in annual and row in event_text
 if sport=='badminton':
  for year in (2025,2026):assert len({r['competition'] for r in rows if r['year']==year and r['category']=='Super 1000'})==4
 else:
  assert len({r['competition'] for r in rows if r['year']==2025 and r['category']=='그랜드 스매시'})==4
  assert not any(r['event']=='xt' and '남녀 단체' in r['competition'] for r in rows)
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files};T.render(sport)
 assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
 print('PASS',sport,len(rows),'records; pair rosters; major coverage; annual/event equality; anchors; idempotence')
