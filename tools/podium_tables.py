"""Shared, lossless presentation of existing medal records; excludes taekwondo."""
from pathlib import Path
from html.parser import HTMLParser
import re,html,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
class Table(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=False);self.rows=[];self.row=None;self.cell=None;self.feed(s)
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row={'attrs':dict(attrs),'cells':[]};self.rows.append(self.row)
  elif tag in ['td','th'] and self.row is not None:self.cell={'tag':tag,'attrs':dict(attrs),'html':''};self.row['cells'].append(self.cell)
  elif self.cell is not None:self.cell['html']+=self.get_starttag_text()
 def handle_endtag(self,tag):
  if tag in ['td','th']:self.cell=None
  elif tag=='tr':self.row=None
  elif self.cell is not None:self.cell['html']+='</'+tag+'>'
 def handle_data(self,s):
  if self.cell is not None:self.cell['html']+=s
 def handle_entityref(self,s):self.handle_data('&'+s+';')
 def handle_charref(self,s):self.handle_data('&#'+s+';')
def plain(s):return html.unescape(re.sub('<[^>]+>','',s)).strip()
def convert(table):
 if 'podium-table' in table or 'data-podium=' in table:return table
 parsed=Table(table)
 if not parsed.rows:return table
 headers=[plain(c['html']) for c in parsed.rows[0]['cells']]
 if len(headers)==4 and any(x in headers for x in ['금','금메달','Gold','1위']):
  return re.sub(r'<table\b([^>]*)>',lambda m:'<table'+m[1]+' data-podium="existing">',table,count=1)
 if len(headers)!=2 or headers[0]!='대회' or '결과' not in headers[1] or not any(x in headers[1] for x in ['선수','팀']):return table
 groups={};other=[]
 for row in parsed.rows[1:]:
  if len(row['cells'])!=2:continue
  label,value=[c['html'] for c in row['cells']];text=plain(value)
  match=re.search(r'\s[·/]\s*(금|은|동|우승|준우승)(?:메달)?\s*$',text)
  if not match:other.append(row);continue
  medal={'금':0,'우승':0,'은':1,'준우승':1,'동':2}[match[1]]
  group=groups.setdefault(label,[[],[],[]])
  value=re.sub(r'\s[·/]\s*(금|은|동|우승|준우승)(?:메달)?\s*(?=</a>|</span>|$)','',value)
  attrs=''.join(' '+k+'="'+html.escape(v,quote=True)+'"' for k,v in row['attrs'].items() if k=='id' or k.startswith('data-'))
  group[medal].append('<span class="podium-person"'+attrs+'>'+value+'</span>')
 if not groups:return table
 body=''.join('<tr><th scope="row">'+label+'</th>'+''.join('<td>'+(''.join(people) if people else '<span class="podium-unknown">미수록</span>')+'</td>' for people in medals)+'</tr>' for label,medals in groups.items())
 result='<table class="podium-table"><caption>대회별 입상 기록 · 수록 자료 기준</caption><thead><tr><th scope="col">대회</th><th scope="col" class="podium-gold">금·우승</th><th scope="col" class="podium-silver">은·준우승</th><th scope="col" class="podium-bronze">동</th></tr></thead><tbody>'+body+'</tbody></table>'
 if other:
  rows=''.join('<tr'+''.join(' '+k+'="'+html.escape(v,quote=True)+'"' for k,v in r['attrs'].items())+'>'+''.join('<'+c['tag']+'>'+c['html']+'</'+c['tag']+'>' for c in r['cells'])+'</tr>' for r in other)
  result+='<details class="podium-other"><summary>기타 순위·한국 성적</summary><table class="data"><thead><tr><th>대회</th><th>선수·팀 · 결과</th></tr></thead><tbody>'+rows+'</tbody></table></details>'
 return result
def update():
 changed=[];counts={}
 version=hashlib.sha256((ROOT/'css/podium-tables.css').read_bytes()).hexdigest()[:12]
 for p in sorted(ROOT.glob('ol*.html')):
  if not p.name.startswith(('olboxing','oljudo','olwrestling','olfencing','olbadminton','oltabletennis','olgolf','olshooting','olarchery','oltennis')):continue
  s=p.read_text(encoding='utf-8');t=re.sub(r'<table\b.*?</table>',lambda m:convert(m[0]),s,flags=re.S)
  if 'podium-table' not in t and 'data-podium="existing"' not in t:continue
  t=re.sub(r'<link rel="stylesheet" href="(?:\./)?css/podium-tables.css[^\"]*">','',t)
  t=t.replace('</head>','<link rel="stylesheet" href="./css/podium-tables.css?v='+version+'"></head>')
  if t!=s:p.write_text(t,encoding='utf-8',newline='\n');changed.append(p.name)
  counts[p.name]=t.count('class="podium-table"')+t.count('data-podium="existing"')
 print(json.dumps({'pages':len(counts),'tables':sum(counts.values()),'changed':len(changed)},ensure_ascii=False))
 return counts
if __name__=='__main__':update()
