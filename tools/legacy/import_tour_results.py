"""Import annual major badminton and table-tennis results from saved Wikipedia HTML."""
import json,re,hashlib,sys
from pathlib import Path
from wiki_tables import Tables,expand,text,clean
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT.parent
EVENTS={"Men's singles":'ms',"Women's singles":'ws',"Men's doubles":'md',"Women's doubles":'wd','Mixed doubles':'xd',"Men's team":'mt',"Women's team":'wt','Mixed team':'xt'}
COUNTRIES={'China','South Korea','North Korea','Japan','Chinese Taipei','France','Denmark','Canada','Thailand','Malaysia','Indonesia','India','Singapore','Hong Kong','Sweden','Germany','Brazil','England','United States','Romania','Austria','Egypt','Iran','Spain','Portugal','Croatia','Australia','Kazakhstan','Slovenia','Nigeria','Poland','China Volksrepublik','Korea Sud','Frankreich','Japan','Brasilien','Deutschland','Schweden','Singapur','Taiwan','Dänemark','Vereinigte Staaten','Hongkong','Rumänien'}
def cell(c):
 segs=c['segments'];countries=[country for s in segs for country in s['countries'] if country and 'medalist' not in country]
 country=countries[0] if countries else next((clean(s['text']) for s in segs if clean(s['text']) in COUNTRIES),'')
 ignored=COUNTRIES|set(countries)
 names=[]
 for s in segs:
  before=len(names)
  for l in s['links']:
   n=clean(l['text'])
   if n and n not in ignored and not l['href'].startswith('#') and n not in ('details','Report','Draw') and not n.startswith('['):names.append(n)
  if len(names)==before:
   n=clean(s['text'])
   for ctry in sorted(ignored,key=len,reverse=True):n=clean(n.replace(ctry,''))
   if n and not n.startswith('Score:') and n not in ('TBD','TBA','—','–'):names.append(n)
 return list(dict.fromkeys(names)),country
def read(title,lang='en'):
 p=RAW/(title+'.html');raw=p.read_text(encoding='utf-8')
 return Tables(raw).tables,dict(url='https://'+lang+'.wikipedia.org/wiki/'+title,sha256=hashlib.sha256(raw.encode()).hexdigest())
def add(out,source,year,comp,category,event,c,outcome):
 names,country=cell(c)
 if not names:return
 r=dict(year=year,competition=comp,category=category,event=event,members=names,country=country,result=outcome,source=source)
 if not any(all(old[k]==r[k] for k in ('year','competition','event','members','result')) for old in out):out.append(r)
def medals(out,sources,title,year,comp,category):
 tables,source=read(title);sources.append(source)
 for t in tables:
  if not t['rows']:continue
  header=' '.join(text(c) for c in t['rows'][0])
  if not header.startswith('Event') or not all(k in header for k in ('Gold','Silver','Bronze')):continue
  for row in expand(t['rows'])[1:]:
   if len(row)!=4:continue
   event=EVENTS.get(text(row[0]).replace('details','').strip())
   if not event:continue
   for c,label in zip(row[1:],['금','은','동']):add(out,source['url'],year,comp,category,event,c,label)
def tours(out,sources,title,year,sport):
 tables,source=read(title);sources.append(source)
 for t in tables:
  if t['section']!='Finals':continue
  counter={}
  for row in expand(t['rows'])[1:]:
   if len(row)!=4 or text(row[2]).startswith('Score:'):continue
   info=text(row[1]);major=('Super 1000' in info or 'World Tour Finals' in info) if sport=='badminton' else 'Grand Smash' in info
   if not major:continue
   links=[l['text'] for s in row[1]['segments'] for l in s['links'] if clean(l['text']) and l['text'] not in ('Draw','Report')]
   comp=clean(links[0]) if links else info.split(' (Draw)')[0].split(' Location:')[0]
   i=counter.get(comp,0);counter[comp]=i+1
   if i>=5:raise ValueError((title,comp,i))
   event=['ms','ws','md','wd','xd'][i]
   category='파이널스' if 'World Tour Finals' in info else 'Super 1000' if sport=='badminton' else '그랜드 스매시'
   add(out,source['url'],year,comp,category,event,row[2],'우승')
   add(out,source['url'],year,comp,category,event,row[3],'준우승')
def worldcup(out,sources):
 tables,source=read('Table_Tennis_World_Cup');sources.append(source)
 for t in tables:
  if t['section']!='Winners' or t['gender'] not in EVENTS or not t['rows']:continue
  head=' '.join(text(c) for c in t['rows'][0])
  if not head.startswith('Year'):continue
  for row in expand(t['rows'])[1:]:
   if len(row)!=5 or text(row[0]) not in ('2025','2026'):continue
   year=int(text(row[0]));event=EVENTS[t['gender']]
   for c,label in zip(row[2:],['금','은','동']):add(out,source['url'],year,'ITTF 월드컵' if event in ('ms','ws') else 'ITTF 혼성단체 월드컵','월드컵',event,c,label)
def german_smashes(out,sources):
 tables,source=read('WTT_Series_2026','de');sources.append(source)
 for t in tables:
  if t['section']!='Turniere':continue
  for row in expand(t['rows']):
   if len(row)!=12 or 'Smash' not in text(row[2]):continue
   comp=text(row[2])
   for event,c in zip(['ms','md','ws','wd','xd'],row[5:10]):add(out,source['url'],2026,comp,'그랜드 스매시',event,c,'우승')
def save(sport,out,sources):
 for i,r in enumerate(out):r['id']=sport+'-'+str(i)
 (ROOT/('data/'+sport+'-tour.json')).write_text(json.dumps(dict(as_of='2026-10-11',sources=sources,results=out,recipients=[]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(sport,len(out),'results',sorted({(r['year'],r['competition']) for r in out}))
def main():
 sports=sys.argv[1:] or ['badminton','tabletennis']
 if 'badminton' in sports:
  out=[];sources=[]
  for year in (2025,2026):
   tours(out,sources,f'{year}_BWF_World_Tour',year,'badminton')
   medals(out,sources,f'{year}_BWF_World_Championships',year,'세계선수권','세계선수권')
  medals(out,sources,'Badminton_at_the_2026_Asian_Games',2026,'아시안게임','아시안게임')
  save('badminton',out,sources)
 if 'tabletennis' in sports:
  out=[];sources=[]
  tours(out,sources,'2025_WTT_Series',2025,'tabletennis')
  medals(out,sources,'2025_World_Table_Tennis_Championships',2025,'세계선수권 · 개인','세계선수권')
  medals(out,sources,'2026_World_Team_Table_Tennis_Championships',2026,'세계선수권 · 남녀 단체','세계선수권')
  medals(out,sources,'Table_tennis_at_the_2026_Asian_Games',2026,'아시안게임','아시안게임')
  worldcup(out,sources);german_smashes(out,sources)
  save('tabletennis',out,sources)
if __name__=='__main__':main()
