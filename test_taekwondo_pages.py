from pathlib import Path
from html.parser import HTMLParser
import hashlib,re
from taekwondo_pages import update_pages,D,AXES,axis_for
R=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):super().__init__();self.ids=[];self.links=[];self.feed(text)
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        x=a.get('href') or a.get('src')
        if x and t in ['a','link','script']:self.links.append(x)
pages={p.name:Page(p.read_text(encoding='utf-8')) for p in R.glob('oltaekwondo*.html')}
for name,page in pages.items():
    assert len(page.ids)==len(set(page.ids)),('duplicate',name)
    for x in page.links:
        if x.startswith('#'):assert x[1:] in page.ids,(name,x)
        elif x.startswith('./'):
            filename,_,anchor=x[2:].partition('#');assert (R/filename).exists(),(name,x)
            if anchor and filename in pages:assert anchor in pages[filename].ids,(name,x)
def cell(text,row):return re.search(r'<tr id="'+re.escape(row)+r'">.*?<td>(.*?)</td></tr>',text,re.S)[1]
comparisons=0
for code,w in D['weights'].items():
    weight=(R/f'oltaekwondo-ev-{code}.html').read_text(encoding='utf-8')
    assert weight.count('tkd-results-table')==1
    assert weight.count('tkd-pathways-table')==1
    for event in D['events']:
        if event.get('gender') and event['gender']!=code[0]:continue
        year=(R/f'oltaekwondo-{axis_for(event["id"])}.html').read_text(encoding='utf-8')
        assert cell(weight,'meet-'+event['id'])==cell(year,'meet-'+event['id']+'-'+code),(code,event['id'])
        comparisons+=1
main=(R/'oltaekwondo.html').read_text(encoding='utf-8')
for key,title,ids in AXES:
    assert f'oltaekwondo-{key}.html' in main
    for code in D['weights']:assert f'oltaekwondo-{key}.html#weight-{code}' in main
hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.glob('oltaekwondo*.html')}
before=hashes();update_pages();assert hashes()==before,'non-idempotent renderer'
print(f'Passed: {len(pages)} pages; all IDs, links; {comparisons} shared event/weight result cells; 8 consolidated result/path tables; matrix links; idempotence.')
