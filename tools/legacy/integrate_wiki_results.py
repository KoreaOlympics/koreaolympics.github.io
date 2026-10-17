"""Integrate reviewed podiums into the existing orthogonal wiki documents."""
import html,json,re,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]
DATA=json.loads((R/'data/medal-views.json').read_text(encoding='utf-8'))
H=lambda s:html.escape(str(s),quote=True)
COUNTRIES={'KOR':'한국','CHN':'중국','TPE':'대만','JPN':'일본','USA':'미국','GBR':'영국','FRA':'프랑스','IRI':'이란','UZB':'우즈벡','THA':'태국','INA':'인도네시아','MAS':'말레이시아','DEN':'덴마크','ESP':'스페인','JOR':'요르단','TUN':'튀니지','CRO':'크로아티아','BRA':'브라질','GER':'독일','HKG':'홍콩'}
COUNTRIES.update({'KAZ':'카자흐','KGZ':'키르기스','PRK':'북한','IND':'인도','TJK':'타지크','MGL':'몽골','CAN':'캐나다','RUS':'러시아','AIN':'중립','TUR':'튀르키예'})
TKD_TARGETS={}
for page in R.glob('oltaekwondo-20*.html'):
 for mid in re.findall(r'<section id="meet-([^"]+)"',page.read_text(encoding='utf-8')):TKD_TARGETS[mid]=page.name+'#meet-'+mid
START='<!-- integrated-wiki-results:start -->'
END='<!-- integrated-wiki-results:end -->'

def cell(people):
 if not people:return '<span class="podium-unknown">미수록</span>'
 out=''
 for p in people:
  full=p.get('fullName',p['name']);name=p['name']
  name={'SEONG Yuhyeon':'성유현','KIM Hyanggi':'김향기','HONG Hyo Rim':'홍효림'}.get(name,name)
  if p['country'] in ['CHN','TPE','HKG'] and len(name.split())==1 and not re.search('[가-힣]',name):name=full
  if ' / ' in full and len(full.split(' / '))>2:name=COUNTRIES.get(p['country'],p['country'])+' 팀'
  url=p.get('url','');text=H(name)
  if url:text=f'<a href="{H(url)}" title="{H(full)}">{text}</a>'
  else:text=f'<span title="{H(full)}">{text}</span>'
  out+=f'<span class="podium-person">{text}<span class="podium-country">({H(COUNTRIES.get(p["country"],p["country"]))})</span></span>'
 return out

def table(sport,records,axis):
 d=DATA[sport];meets={m['id']:m for m in d['meets']};body=''
 if axis=='event' and sport=='wrestling':records=sorted(records,key=lambda r:({'fs':0,'gr':1,'ww':2}[r['weight'][:2]],int(r['weight'][2:])))
 if axis=='event' and sport=='judo':records=sorted(records,key=lambda r:(r['weight'][0], 'o' in r['weight'],int(re.sub(r'\D','',r['weight']))))
 for i,r in enumerate(records):
  m=meets[r['meet']];label=m['name'] if axis=='meet' else r['event']
  if axis=='meet' and sport not in ['boxing','golf'] and str(r['date'])[:4] not in label:label=str(r['date'])[:4]+' '+label
  if axis=='meet' and sport=='taekwondo' and r['weight'] not in ['Men -58kg','Men -68kg','Men -80kg','Men +80kg','Women -49kg','Women -57kg','Women -67kg','Women +67kg']:label+=' · '+r['event'].replace('남자 ','').replace('여자 ','')
  raw=r['meet']+'-'+r['weight']
  rid='wiki-result-'+(re.sub(r'[^a-zA-Z0-9_-]','-',raw) if sport=='golf' else hashlib.sha1(raw.encode()).hexdigest()[:12])
  target=TKD_TARGETS.get(r['meet'],r.get('source')) if sport=='taekwondo' and axis=='meet' else r.get('source')
  body+=f'<tr id="{rid}"><th scope="row"><a href="{H(target or m.get("url") or "#sources")}">{H(label)}</a></th>'+''.join('<td>'+cell(r['medals'][rank])+'</td>' for rank in ['gold','silver','bronze'])+'</tr>'
 heads=['대회' if axis=='meet' else '체급·종목','1위','2위','3위'] if sport=='golf' else ['대회' if axis=='meet' else '체급·종목','금 · 우승','은 · 준우승','동 · 4강']
 return '<div class="wiki-podium-scroll" tabindex="0"><table class="podium-table"><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in heads)+'</tr></thead><tbody>'+body+'</tbody></table></div>'

def clean_table(m):
 text=m[0]
 native_judo='선수 · 결과' in text and bool(re.search(r'<td>[123]위 ·',text)) and not re.search(r'<td>[4-9]위 ·',text)
 if not (native_judo or 'data-podium' in text or 'class="wiki-results"' in text or 'class="podium-table"' in text):return text
 ids=re.findall(r'\bid="([^"]+)"',text)
 return ''.join('<span id="'+H(i)+'"></span>' for i in ids)

def integrate(path,sport,records,axis='meet'):
 if not path.exists() or not records:return
 t=path.read_text(encoding='utf-8')
 t=re.sub(re.escape(START)+'.*?'+re.escape(END),'',t,flags=re.S)
 # Replace previous medal-only tables, preserving every anchor used by the matrix.
 t=re.sub(r'<table\b[^>]*>.*?</table>',clean_table,t,flags=re.S)
 if sport=='taekwondo':
  t=re.sub(r'<ul class="tkd-result-names">.*?</ul>','<a class="small" href="#wiki-results">입상자 표 ↓</a>',t,flags=re.S)
  t=re.sub(r'<div class="tkd-result-weight">.*?</div>','',t,flags=re.S)
  t=re.sub(r'(<a class="small" href="#wiki-results">입상자 표 ↓</a>)(?:\s*\1)+',r'\1',t)
 tables=table(sport,records,axis)
 if axis=='event':
  meets={m['id']:m for m in DATA[sport]['meets']}
  tables=''.join('<h3>'+H(meets[mid]['name'])+'</h3>'+table(sport,[r for r in records if r['meet']==mid],axis) for mid in dict.fromkeys(r['meet'] for r in records))
 content=START+'<section id="wiki-results"><h2>대회 결과</h2>'+tables+'<p class="small">동메달·준결승 진출자가 둘이면 같은 칸 안에서 구분합니다. 미수록은 결과를 확인하지 못한 항목입니다.</p></section>'+END
 missing=[]
 for row in records:
  source=row.get('source','').split('#')
  if len(source)==2 and source[0].removeprefix('./')==path.name and f'id="{source[1]}"' not in t and source[1] not in missing:missing.append(source[1])
 content=content.replace('<h2>대회 결과</h2>','<h2>대회 결과</h2>'+''.join('<span id="'+H(i)+'"></span>' for i in missing))
 if sport=='badminton' and re.search(r'<section id="results">.*?</section>',t,re.S):
  t=re.sub(r'<section id="results">.*?</section>',lambda m:'<span id="results"></span>'+content,t,count=1,flags=re.S)
 elif sport=='badminton' and '<span id="results"></span>' in t:
  t=t.replace('<span id="results"></span>','<span id="results"></span>'+content,1)
 else:
  pos=re.search(r'<section\b|<details\b',t[t.index('<main'):])
  at=t.index('<main')+pos.start() if pos else t.index('</main>')
  t=t[:at]+content+t[at:]
 if 'css/podium-tables.css' not in t:t=t.replace('</head>','<link rel="stylesheet" href="css/podium-tables.css?v=20261013-integrated"></head>')
 path.write_text(t,encoding='utf-8',newline='\n')
 changed.append(path.name)

def run():
 global changed
 changed=[]
 tk=json.loads((R/'data/taekwondo-pathways.json').read_text(encoding='utf-8'))
 fencing={'em':'남자 개인 에페','ew':'여자 개인 에페','emt':'남자 단체 에페','ewt':'여자 단체 에페','fm':'남자 개인 플뢰레','fw':'여자 개인 플뢰레','fmt':'남자 단체 플뢰레','fwt':'여자 단체 플뢰레','sm':'남자 개인 사브르','sw':'여자 개인 사브르','smt':'남자 단체 사브르','swt':'여자 단체 사브르'}
 shooting={'arm':'ARM','arw':'ARW','r3m':'R3PM','r3w':'R3PW','apm':'APM','apw':'APW','rfm':'RFPM','p25w':'SPW','arx':'ARMT','apx':'APMT','trm':'TRM','trw':'TRW','skm':'SKM','skw':'SKW','trx':'TRMT'}
 archery={'rm':'리커브 남자 개인','rw':'리커브 여자 개인','rmt':'리커브 남자 단체','rwt':'리커브 여자 단체','rx':'리커브 혼성 단체','cx':'컴파운드 혼성 단체'}
 for sport,d in DATA.items():
  for p in R.glob('ol'+sport+'-ev-*.html'):
   code=p.stem.split('-ev-')[1];weights=[code]
   if sport=='taekwondo':weights=[tk['weights'][code]['olympic']]+tk['weights'][code]['worldWeights']
   if sport=='fencing':weights=[fencing.get(code,code)]
   if sport=='shooting':weights=[shooting.get(code,code)]
   if sport=='archery':weights=[archery.get(code,code)]
   integrate(p,sport,[r for r in d['records'] if r['weight'] in weights])
  if sport=='badminton':
   for y in [2025,2026]:
    for code in ['ms','ws','md','wd','xd']:integrate(R/f'olbadminton-{y}-{code}.html',sport,[r for r in d['records'] if r['weight']==code and str(r['date']).startswith(str(y))])
  if sport=='golf':
   for gender,name in [('m','men'),('w','women')]:integrate(R/f'olgolf-{name}.html',sport,[r for r in d['records'] if r['weight'].startswith(gender+'-')])
  if sport in ['fencing','archery']:integrate(R/f'ol{sport}-results.html',sport,d['records'],'event')
  for p in R.glob('ol'+sport+'-20*.html'):
   if sport=='badminton' and re.search(r'-20\d\d-[mw][sd]\.html|-20\d\d-xd\.html',p.name):continue
   records=[]
   for r in d['records']:
    if r['source'].split('#')[0].removeprefix('./')==p.name:records.append(r)
   if sport=='taekwondo':
    t=p.read_text(encoding='utf-8');ids=re.findall(r'<section id="meet-([^"]+)"',t)
    records=[r for r in d['records'] if r['meet'] in ids]
   if sport=='judo' and p.name=='oljudo-2026-world.html':records=d['records']
   if sport=='wrestling' and p.name=='olwrestling-2026-ag.html':records=d['records']
   if sport=='archery':
    if p.name=='olarchery-2026-ag.html':records=[r for r in d['records'] if r['meet']=='2026 아시안게임']
    if p.name=='olarchery-2026-cup.html':records=[r for r in d['records'] if r['meet'].startswith('스테이지')]
    if p.name=='olarchery-2026-final.html':records=[r for r in d['records'] if r['meet']=='파이널']
   if sport=='shooting' and '2025' in p.name:
    selected={'olshooting-2025-world.html':['3275','3332'],'olshooting-2025-wc.html':['3268','3274','3271','3273','3269','3272'],'olshooting-2025-final.html':['3393']}.get(p.name,[])
    records=[r for r in d['records'] if r['meet'] in selected]
   # Each tournament has its own table when an annual page covers several meetings.
   integrate(p,sport,records,'event')
 for p in R.glob('ol*.html'):
  t=p.read_text(encoding='utf-8');new=re.sub(r'<a\b[^>]*class="medal-view-link"[^>]*>.*?</a>','',t,flags=re.S)
  if new!=t:p.write_text(new,encoding='utf-8',newline='\n')
 p=R/'olgolf.html';t=p.read_text(encoding='utf-8')
 t=re.sub(r'<!-- major-index:start -->.*?<!-- major-index:end -->','',t,flags=re.S)
 rows=''.join('<tr><th>'+H(label)+'</th>'+''.join('<td><a href="olgolf-'+('men' if code.startswith('m-') else 'women')+'.html#wiki-result-'+str(y)+'-'+code+'-'+code+'">'+str(y)+'</a></td>' for y in [2025,2026])+'</tr>' for code,label in DATA['golf']['weights'].items())
 index='<!-- major-index:start --><section id="major-index"><h2>메이저 · 연도별</h2><div class="wiki-podium-scroll"><table class="data"><thead><tr><th>대회</th><th>2025</th><th>2026</th></tr></thead><tbody>'+rows+'</tbody></table></div></section><!-- major-index:end -->'
 t=re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+index,t,count=1)
 p.write_text(t,encoding='utf-8',newline='\n')
 print('Integrated existing documents:',len(changed))
if __name__=='__main__':run()
