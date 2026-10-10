"""Fetch and validate Totallympics public medal tables; retain last good data on error."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
from datetime import datetime,timezone
import json,re,sys,argparse
WORLD='https://totallympics.com/qualification-tracker/los-angeles-2028/world-championships-medal-counts-in-the-road-to-los-angeles-2028/latest-world-championships-medal-count-in-the-road-to-los-angeles-2028-r3084/'
KOREA='https://totallympics.com/qualification-tracker/los-angeles-2028/qualification-by-nation/republic-of-korea/republic-of-korea-world-championships-medal-count-r3094/'
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None;self.links=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='table':self.table=[]
  elif t=='tr' and self.table is not None:self.row=[]
  elif t in ('td','th') and self.row is not None:self.cell=[];self.links=[]
  elif t=='a' and self.cell is not None and a.get('href','').startswith(('https://','/')):self.links.append(a['href'])
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ('td','th') and self.cell is not None:self.row.append({'text':' '.join(''.join(self.cell).split()),'links':self.links});self.cell=None
  elif t=='tr' and self.row is not None:self.table.append(self.row);self.row=None
  elif t=='table' and self.table is not None:self.tables.append(self.table);self.table=None
def parse(s):
 p=Tables();p.feed(s);return p.tables
def fetch(url):
 req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; KoreaOlympicsMedalReader/1.0)','Accept':'text/html'})
 with urlopen(req,timeout=45) as r:return r.read().decode('utf-8-sig')
def build(world,korea):
 tables=parse(world)
 table=next(t for t in tables if [c['text'] for c in t[0]]==['Rank','Nation','Gold','Silver','Bronze','Total'])
 nations=[]
 for row in table[1:]:
  v=[c['text'] for c in row]
  if len(v)!=6 or not all(v[i].isdigit() for i in (2,3,4,5)):continue
  g,s,b,total=map(int,v[2:]);assert g+s+b==total,('invalid nation total',v)
  href=next((urljoin(WORLD,x) for x in row[1]['links'] if 'qualification-by-nation/' in x),WORLD)
  nations.append(dict(rank=v[0],nation=v[1],gold=g,silver=s,bronze=b,total=total,url=href))
 assert len(nations)>=10,'nation table not found'
 kor=next(n for n in nations if n['nation']=='Republic of Korea')
 medals=[];detailtables=[t for t in parse(korea) if [c['text'] for c in t[0]]==['Date','Athletes','Sport & Event','Expire']]
 assert len(detailtables)==3,'Korea medal sections changed'
 for medal,t in zip(('gold','silver','bronze'),detailtables):
  for row in t[1:]:
   if len(row)!=4:continue
   v=[c['text'] for c in row]
   if not v[1]:continue
   url=next((urljoin(KOREA,x) for x in row[2]['links'] if '/qualification-by-sport/' in x),KOREA)
   match=re.search(r'/qualification-by-sport/([^/]+)/',url)
   medals.append(dict(medal=medal,date=v[0],athletes=v[1],event=v[2],expiry=v[3],sport=match[1] if match else '',url=url,expired=v[3].strip().lower()=='expired'))
 assert medals,'Korea detail missing'
 return dict(schema=1,fetchedAt=datetime.now(timezone.utc).isoformat(),sources={'world':WORLD,'korea':KOREA},nations=nations,korea=kor,koreaMedals=medals,activeDetailCounts={m:sum(x['medal']==m and not x['expired'] for x in medals) for m in ('gold','silver','bronze')})
def save(root,data):
 target=root/'data'/'worlds-medals.json';target.parent.mkdir(parents=True,exist_ok=True)
 tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(target)
 page=root/'worlds-medals.html'
 if page.exists():
  s=page.read_text(encoding='utf-8');seed=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
  s,n=re.subn(r'(<script id="medal-seed" type="application/json">).*?(</script>)',lambda m:m[1]+seed+m[2],s,flags=re.S);assert n==1
  page.write_text(s,encoding='utf-8')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--world-file',type=Path);ap.add_argument('--korea-file',type=Path);args=ap.parse_args()
 try:
  world=args.world_file.read_text(encoding='utf-8-sig') if args.world_file else fetch(WORLD)
  korea=args.korea_file.read_text(encoding='utf-8-sig') if args.korea_file else fetch(KOREA)
  data=build(world,korea);save(args.root,data);print(json.dumps({'nations':len(data['nations']),'korea':data['korea'],'detailCounts':data['activeDetailCounts']},ensure_ascii=True))
 except Exception as e:print('Medal update failed; last published data retained: '+str(e),file=sys.stderr);sys.exit(1)
