"""Parse medalist tables (including rowspan and missing bronze cells) from Wikipedia HTML.
Usage: python tools/import_boxing_wikipedia.py world.html cup.html
"""
import hashlib,json,re,sys
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE='https://en.wikipedia.org/wiki/'
class Tables(HTMLParser):
 def __init__(self,text):
  super().__init__();self.tables=[];self.section='';self.gender='';self.heading=None;self.depth=0;self.cell=None;self.link=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag in ('h2','h3'):self.heading=[tag,'',d.get('id','')]
  if tag=='table':
   self.depth+=1
   if self.depth==1:self.table={'section':self.section,'gender':self.gender,'rows':[]}
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
  if tag in ('h2','h3') and self.heading:
   level,text,_=self.heading;self.heading=None
   if level=='h2':self.section=text.strip()
   elif text.strip() in ('Men','Women'):self.gender=text.strip()
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
def parse(path,title):
 raw=Path(path).read_text(encoding='utf-8');tables=Tables(raw).tables;records=[];missing=[];counts={}
 for table in tables:
  if table['gender'] not in ('Men','Women') or not table['rows']:continue
  if not all(x in ' '.join(text(c) for c in table['rows'][0]) for x in ['Event','Gold','Silver','Bronze']):continue
  section=table['section'];stage='world' if title.endswith('Championships') else {'Stage I':'cup1','Stage II':'cup2','Finals':'final'}[section]
  counts.setdefault(stage,0)
  for row in expand(table['rows'])[1:]:
   if len(row)!=4:raise ValueError(('Unexpected medal columns',section,[text(c) for c in row]))
   weight=text(row[0]).replace('details','').strip();numbers=re.findall(r'\d+',weight)
   if not numbers:continue
   code=('m' if table['gender']=='Men' else 'w')+('o' if '+' in weight else '')+numbers[-1]
   for c,medal in zip(row[1:],['금','은','동']):
    segments=c['segments']
    if stage=='world':
     segments=[dict(s,countries=[clean(segments[i+1]['text'])]) for i,s in enumerate(segments) if i%2==0 and i+1<len(segments)]
    for segment in segments:
     countries=[x.removeprefix('Flag of ') for x in segment['countries'] if x not in ('No bronze medal awarded','None')]
     links=[x for x in segment['links'] if clean(x['text']) and not x['href'].startswith('#') and clean(x['text']) not in countries and 'File:' not in x['href']]
     name=clean(links[0]['text']) if links else clean(segment['text'])
     for country in countries:name=clean(name.replace(country,''))
     if not name or name in ('—','–','-'):
      if stage=='final':missing.append(dict(stage=stage,weight=code,medal=medal))
      continue
     country=countries[0] if countries else ''
     if any(r['stage']==stage and r['weight']==code and r['athlete']==name and r['result']==medal for r in records):continue
     counts[stage]+=1
     records.append(dict(stage=stage,weight=code,original_weight=weight,athlete=name,country=country,result=medal,athlete_url=BASE+links[0]['href'].split('/wiki/')[-1] if links and '/wiki/' in links[0]['href'] else '',source=BASE+title+'#'+('Medalists' if stage=='world' else section.replace(' ','_'))))
 return records,dict(url=BASE+title,sha256=hashlib.sha256(raw.encode()).hexdigest(),counts=counts,missing=missing)
def main():
 allrows=[];sources=[]
 for path,title in zip(sys.argv[1:],['2025_World_Boxing_Championships','2025_World_Boxing_Cup']):
  rows,source=parse(path,title);allrows+=rows;sources.append(source)
 assert sources[0]['counts']=={'world':80},sources[0]
 assert len(sources[1]['counts'])==3,sources[1]
 dataset=dict(as_of='2026-10-11',sources=sources,medalists=allrows)
 (ROOT/'data/boxing-wikipedia-2025.json').write_text(json.dumps(dataset,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 data=json.loads((ROOT/'data/boxing-pathways.json').read_text(encoding='utf-8'))
 data['results']=[r for r in data['results'] if r['axis'] not in ('2025-wc','2025-cup')]
 for i,r in enumerate(allrows):
  row=dict(r,id='wiki2025-'+str(i),axis='2025-wc' if r['stage']=='world' else '2025-cup',competition={'world':'2025 리버풀 세선','cup1':'2025 브라질 월드컵','cup2':'2025 아스타나 월드컵','final':'2025 월드컵 파이널'}[r['stage']],provenance='Wikipedia medalist table')
  if row['athlete']=='Im Ae-ji':row['athlete']='임애지'
  if row['athlete']=='Bak Chorong':row['athlete']='박초롱'
  data['results'].append(row)
 data['scope']='2025 Wikipedia medal tables; existing 2026 Korean athlete records; missing medal cells preserved as unknown'
 (ROOT/'data/boxing-pathways.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('Imported',len(allrows),'medal records; counts:',[s['counts'] for s in sources])
if __name__=='__main__':main()
