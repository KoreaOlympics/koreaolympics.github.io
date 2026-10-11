"""Parse Wikipedia archery result tables. Usage: world.html cup.html"""
import hashlib,json,re,sys
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='https://en.wikipedia.org/wiki/'
class Tables(HTMLParser):
 def __init__(self,text):
  super().__init__();self.tables=[];self.section='';self.gender='';self.event='';self.heading=None;self.depth=0;self.cell=None;self.link=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag in ('h2','h3','h4'):self.heading=[tag,'',d.get('id','')]
  if tag=='table':
   self.depth+=1
   if self.depth==1:self.table={'section':self.section,'gender':self.gender,'event':self.event,'rows':[]}
  if self.depth!=1:return
  if tag=='tr':self.row=[]
  if tag in ('td','th'):
   self.cell={'span':int(d.get('rowspan','1')),'segments':[{'text':'','links':[],'countries':[]}]}
  if self.cell:
   seg=self.cell['segments'][-1]
   if tag=='br':self.cell['segments'].append({'text':'','links':[],'countries':[]})
   if tag=='img' and d.get('alt') and d['alt'] not in ('','No bronze medal awarded'):seg['countries'].append(d['alt'])
   if tag=='a':self.link={'text':'','href':d.get('href','')}
 def handle_data(self,t):
  if self.heading:self.heading[1]+=t
  if self.cell:
   self.cell['segments'][-1]['text']+=t
   if self.link:self.link['text']+=t
 def handle_endtag(self,tag):
  if tag in ('h2','h3','h4') and self.heading:
   level,text,_=self.heading;self.heading=None
   if level=='h2':self.section=text.strip()
   elif level=='h3':self.gender=text.strip()
   else:self.event=text.strip()
  if self.depth==1:
   if tag=='a' and self.cell and self.link:
    self.cell['segments'][-1]['links'].append(self.link);self.link=None
   if tag in ('td','th') and self.cell:self.row.append(self.cell);self.cell=None;self.link=None
   if tag=='tr':self.table['rows'].append(self.row)
   if tag=='table':self.tables.append(self.table)
  if tag=='table':self.depth-=1

def clean(t):return re.sub(r'\s+',' ',t).strip()
def text(cell):return clean(' '.join(s['text'] for s in cell['segments']))
def expand(rows):
 pending={};out=[]
 for row in rows:
  cells={i:c for i,(c,n) in pending.items()};next_pending={i:(c,n-1) for i,(c,n) in pending.items() if n>1};i=0
  for c in row:
   while i in cells:i+=1
   cells[i]=c
   if c['span']>1:next_pending[i]=(c,c['span']-1)
   i+=1
  out.append([cells[i] for i in sorted(cells)]);pending=next_pending
 return out
EVENTS={"Men's individual":'m',"Women's individual":'w',"Men's team":'mt',"Women's team":'wt','Mixed team':'x'}
def parse(path,title):
 raw=Path(path).read_text(encoding='utf-8');rows=[];world='Championships' in title
 for t in Tables(raw).tables:
  if t['gender'] not in ('Recurve','Compound'):continue
  if not t['rows']:continue
  head=' '.join(text(c) for c in t['rows'][0])
  if (world and 'Gold' not in head) or (not world and not head.startswith('Stage')):continue
  for cells in expand(t['rows'])[1:]:
   if world:
    event=text(cells[0]).replace('details','').strip();stage='world';medals=cells[1:]
   else:
    event=t['event'];stage=text(cells[0]).lower();medals=cells[2:]
   if event not in EVENTS or len(medals)!=3:raise ValueError((event,stage,len(medals)))
   code=('r' if t['gender']=='Recurve' else 'c')+EVENTS[event]
   for c,medal in zip(medals,['금','은','동']):
    parts=[s for s in c['segments'] if clean(s['text'])]
    if not parts:continue
    if event.endswith('individual'):
     name=clean(parts[0]['links'][0]['text']) if parts[0]['links'] else clean(parts[0]['text'])
     members=[name]
     country=clean(parts[1]['text']) if world else re.search(r'\(([A-Z]{3})\)',text(c)).group(1)
    else:
     country=clean(parts[0]['text']);members=[clean(s['text']) for s in parts[1:]]
    rows.append(dict(id=('world' if world else 'cup')+'-'+str(len(rows)),event=code,stage=stage,axis='2025-world' if world else '2025-final' if stage=='final' else '2025-cup',competition='2025 광주 세계선수권' if world else '2025 '+{'1':'플로리다','2':'상하이','3':'안탈리아','4':'마드리드','final':'난징 파이널'}[stage]+(' 월드컵' if stage!='final' else ''),country=country,members=members,result=medal,source=BASE+title+'#'+t['gender']))
 return rows,dict(url=BASE+title,sha256=hashlib.sha256(raw.encode()).hexdigest(),count=len(rows))
def main():
 records=[];sources=[]
 for path,title in zip(sys.argv[1:],['2025_World_Archery_Championships','2025_Archery_World_Cup']):
  rows,source=parse(path,title);records+=rows;sources.append(source)
 assert sources[0]['count']==30 and sources[1]['count']==132,sources
 for r in records:
  if r['axis']=='2025-final' and r['event']=='cw':
   r['wikipedia_original']={'members':r['members'],'country':r['country']}
   name,country={'금':('Mariana Bernal','MEX'),'은':('Andrea Becerra','MEX'),'동':('Jyothi Surekha Vennam','IND')}[r['result']]
   r['members']=[name];r['country']=country;r['source']='https://extranet.worldarchery.sport/documents/index.php/?doc=7385';r['correction']='Official result overrides conflicting Wikipedia podium'
 d=dict(as_of='2026-10-11',sources=sources,results=records,qualifiers=[])
 (ROOT/'data/archery-pathways.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('Imported',len(records),'podium records',sources)
if __name__=='__main__':main()
