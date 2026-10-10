"""Validate medal classification, mixed pairs, scoring and generated links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json
from shooting_pages import update_pages,result_tables
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/shooting-projection.json').read_text(encoding='utf-8'))
R=D['results'];C=D['competitions'];E=D['events']
assert len(E)==15 and len(C)==9
assert set(E)=={'ARM','ARW','R3PM','R3PW','APM','APW','RFPM','SPW','ARMT','APMT','TRM','TRW','SKM','SKW','TRMT'}
def medals(kind):return [r for r in R if r['country']=='KOR' and r['stage'] in ['F','G','B'] and r['rank']<=3 and C[str(r['competition'])]['type']==kind]
for k,expected in [('wc',[1,4,3]),('world',[2,0,1]),('final',[0,1,0])]:assert [sum(r['rank']==n for r in medals(k)) for n in [1,2,3]]==expected
def get(cid,event,name,stage):
    return next(r for r in R if r['competition']==cid and r['event']==event and r['name']==name and r['stage']==stage)
assert get(3275,'ARW','BAN Hyojin','F')['score']=='255.0'
assert get(3275,'SPW','YANG Jiin','F')['score']=='40'
assert get(3275,'SPW','YANG Jiin','Q')['score']=='591 - 29x'
assert get(3275,'APW','OH Yejin','Q')['rank']==12
assert get(3271,'ARW','KWON Eunji','F')['rank']==2
assert get(3271,'SPW','OH Yejin','F')['rank']==2
assert get(3393,'SPW','YANG Jiin','F')['rank']==5
mix=next(r for r in medals('world') if r['event']=='APMT')
assert set(mix['members'])=={'OH Yejin','HONG Suhyeon'}
assert get(3273,'RFPM','LEE Jaekyoon','Q')['rank']==8
assert not any(r['competition']==3273 and r['event']=='RFPM' and r['country']=='KOR' and r['stage']=='F' for r in R)
# Preserve same athlete's two different events on the same meet.
assert result_tables(medals_only=True).count('오예진')==4
class Page(HTMLParser):
    def __init__(self,text):super().__init__();self.ids=[];self.links=[];self.feed(text)
    def handle_starttag(self,t,a):
        a=dict(a)
        if 'id' in a:self.ids.append(a['id'])
        if t in ['a','link'] and 'href' in a:self.links.append(a['href'])
paths=list(ROOT.glob('olshooting*.html'))
parsed={p.name:Page(p.read_text(encoding='utf-8')) for p in paths}
for name,page in parsed.items():
    assert len(page.ids)==len(set(page.ids)),('duplicate ID',name)
    for link in page.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=unquote(u.path).removeprefix('./') or name
        assert (ROOT/target).is_file(),('missing target',name,link)
        if u.fragment and target in parsed:assert unquote(u.fragment) in parsed[target].ids,('missing anchor',name,link)
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
update_pages()
assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'renderer must be idempotent'
print('Passed: 15 Olympic events, 9 meets, medal totals, known scores, mixed names, Q/F distinction, all shooting IDs/links, idempotence.')
