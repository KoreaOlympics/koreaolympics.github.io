import json,re,hashlib
from pathlib import Path
from urllib.parse import urlsplit,unquote
from check_wiki_reorganization import Doc,validate
from integrate_wiki_results import run
R=Path(__file__).resolve().parents[2]
files=[p for p in R.glob('ol*.html') if '<!-- integrated-wiki-results:start -->' in p.read_text(encoding='utf-8')]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
run()
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==before[p.name] for p in files),'Integration must be idempotent'
docs={p.name:Doc(p.read_text(encoding='utf-8')) for p in R.glob('*.html')}
errors=[]
for p in files:
 t=p.read_text(encoding='utf-8');d=docs[p.name]
 assert len(d.ids)==len(set(d.ids)),(p.name,'duplicate anchors')
 section=t.split('<!-- integrated-wiki-results:start -->')[1].split('<!-- integrated-wiki-results:end -->')[0]
 for href in Doc(section).links:
  u=urlsplit(href)
  if u.netloc and u.netloc!='koreaolympics.github.io':continue
  target=unquote(u.path).removeprefix('./').lstrip('/') or p.name
  if target not in docs:errors.append((p.name,href));continue
  if u.fragment and unquote(u.fragment) not in docs[target].ids:errors.append((p.name,href))
assert not errors,errors
assert not list(R.glob('ol*-medals.html'))
assert not any('medal-view-link' in p.read_text(encoding='utf-8') for p in R.glob('ol*.html'))
d=json.loads((R/'data/medal-views.json').read_text(encoding='utf-8'))
assert len(d['wrestling']['records'])==18
assert sum(len(v) for r in d['wrestling']['records'] for v in r['medals'].values())==72
assert not validate()
print('PASS:',len(files),'existing documents; idempotence, unique anchors, result links, preserved qualification structure, 72 wrestling medals')
