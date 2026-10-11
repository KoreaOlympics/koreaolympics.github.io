"""Small HTML table parser with row-span expansion for Wikipedia imports."""
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
   if tag=='img' and not d.get('alt') and self.link and self.link.get('title'):seg['countries'].append(self.link['title'])
   if tag=='a':self.link={'text':'','href':d.get('href',''),'title':d.get('title','')}
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
