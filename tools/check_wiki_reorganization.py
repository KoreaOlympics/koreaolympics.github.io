from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re
R=Path(__file__).resolve().parents[1]
class Doc(HTMLParser):
 def __init__(self,t):
  super().__init__();self.ids=[];self.links=[];self.sections=[];self.feed(t)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='a' and d.get('href'):self.links.append(d['href'])
  if tag=='section':self.sections.append(d.get('id'))
def validate():
 files=[p for p in R.glob('*.html') if p.name.startswith(('oltaekwondo','olbadminton','olboxing','olwrestling'))]
 docs={p.name:Doc(p.read_text(encoding='utf-8')) for p in files};errors=[]
 for name,d in docs.items():
  duplicates={i for i in d.ids if d.ids.count(i)>1}
  if duplicates:errors.append((name,'duplicate ids',sorted(duplicates)))
  for href in d.links:
   u=urlsplit(href)
   if u.netloc and u.netloc!='koreaolympics.github.io':continue
   if u.scheme and u.scheme not in ['http','https']:continue
   target=unquote(u.path).removeprefix('./').lstrip('/') or name
   if '/' in target or not target.endswith('.html'):continue
   if not (R/target).exists():errors.append((name,'missing file',href));continue
   if u.fragment and target in docs and unquote(u.fragment) not in docs[target].ids:errors.append((name,'missing anchor',href))
 assert len(list(R.glob('oltaekwondo-ev-*.html')))==8
 assert len(list(R.glob('oltaekwondo-p-*.html')))==15
 assert len(list(R.glob('olbadminton-202?-??.html')))==20
 assert docs['oltaekwondo.html'].sections[0]=='classes'
 assert docs['olbadminton.html'].sections[0]=='tour-index'
 for sport in ['wrestling','boxing']:
  d=docs[f'ol{sport}.html'];assert d.sections.index('qualifying')<d.sections.index('reference')
 d=json.loads((R/'data/taekwondo-pathways.json').read_text(encoding='utf-8'));e={x['id']:x for x in d['events']};assert len(e['ag26']['medals'])==32
 assert any(a['name']=='KIM Hyanggi' and a['medal']=='Silver' for a in e['gp26c']['medals'])
 assert len(e['gp26c']['medals'])==25
 for p in R.glob('olbadminton-202?-??.html'):
  s=p.read_text(encoding='utf-8');assert all(h in s for h in ['대회명','우승자','준우승자','비고'])
 print(json.dumps({'pages':len(files),'errors':errors},ensure_ascii=False,indent=2))
 return errors
if __name__=='__main__':raise SystemExit(bool(validate()))
