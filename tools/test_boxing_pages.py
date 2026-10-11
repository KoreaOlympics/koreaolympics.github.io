"""Check the orthogonal views, mobile table structure, and idempotent rebuild."""
import hashlib, re
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from boxing_pages import ROOT, WEIGHTS, AXES, page, render, load_data

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.ids=[]; self.links=[]; self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag in ('a','link') and 'href' in a: self.links.append(a['href'])

files=['olboxing.html','olboxing-events.html']+[f'olboxing-ev-{c}.html' for c,_ in WEIGHTS]+[page(k) for k,_,_,_ in AXES]
docs={f:Document((ROOT/f).read_text(encoding='utf-8')) for f in files}
for f,d in docs.items():
    assert len(d.ids)==len(set(d.ids)),f+' duplicate IDs'
    for href in d.links:
        u=urlsplit(href)
        if u.scheme or u.netloc: continue
        target=ROOT/unquote(u.path) if u.path else ROOT/f
        assert target.exists(),(f,href)
        if u.fragment:
            other=docs.get(target.name) or Document(target.read_text(encoding='utf-8'))
            assert unquote(u.fragment) in other.ids,(f,href)
for k,_,_,_ in AXES:
    for c,_ in WEIGHTS: assert 'weight-'+c in docs[page(k)].ids
for r in load_data()['results']:
    marker='id="meet-'+r['id']+'"'
    def row(f):
        text=(ROOT/f).read_text(encoding='utf-8')
        return re.search('<tr '+marker+'.*?</tr>',text).group()
    if r['weight'] in {c for c,_ in WEIGHTS}:
        assert row(page(r['axis']))==row('olboxing-ev-'+r['weight']+'.html')
    else:
        assert 'weight-'+r['weight'] in docs[page(r['axis'])].ids
        row(page(r['axis']))
before={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
render()
assert before=={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
css=(ROOT/'css/boxing.css').read_text(encoding='utf-8')
assert 'overflow-x:auto' in css and 'white-space:nowrap' in css and 'position:sticky' in css
print(f'PASS: {len(files)} pages, 140 matrix destinations, shared result rows, local anchors, mobile CSS, idempotence')
