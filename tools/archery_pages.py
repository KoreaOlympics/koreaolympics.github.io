"""Archery event × competition views, independent of other sport generators."""
import hashlib,html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVENTS={'rm':'리커브 남자 개인','rw':'리커브 여자 개인','rmt':'리커브 남자 단체','rwt':'리커브 여자 단체','rx':'리커브 혼성','cx':'컴파운드 혼성'}
OTHER={'cm':'컴파운드 남자 개인','cw':'컴파운드 여자 개인','cmt':'컴파운드 남자 단체','cwt':'컴파운드 여자 단체'}
AXES=[('2025-world','2025 세계선수권'),('2025-cup','2025 월드컵'),('2025-final','2025 파이널'),('2026-cup','2026 월드컵'),('2026-ag','2026 아시안게임'),('2026-final','2026 파이널'),('2027-world','2027 세계선수권'),('2027-cup','2027 월드컵'),('2028-quota','2028 출전권 결산')]
FINAL='https://www.worldarchery.sport/news/202196/beginners-guide-nanjing-2025-hyundai-archery-world-cup-final'
NOC={'South Korea':'KOR','United States':'USA','China':'CHN','Chinese Taipei':'TPE','India':'IND','Mexico':'MEX','Spain':'ESP','France':'FRA','Germany':'GER','Great Britain':'GBR','Brazil':'BRA','Japan':'JPN','Italy':'ITA','Türkiye':'TUR','Turkey':'TUR','Denmark':'DEN','Netherlands':'NED'}
KOR={'Kim Woo-jin':'김우진','Kim Je-deok':'김제덕','Lee Woo-seok':'이우석','Lim Si-hyeon':'임시현','Lee Ga-hyun':'이가현','Kang Chae-young':'강채영','An San':'안산','Kim Jongho':'김종호','Kim Jong-ho':'김종호'}
def h(s):return html.escape(str(s),quote=True)
def a(url,label):return '<a href="'+h(url)+'">'+h(label)+'</a>'
def page(k):return 'olarchery-'+k+'.html'
def scroll(s):return '<div class="arch-axis-scroll" tabindex="0" role="region" aria-label="좌우로 넘기는 표">'+s+'</div>'
def table(caption,rows):return scroll('<table class="arch-axis-results"><caption>'+caption+'</caption><thead><tr><th scope="col">대회·경로</th><th scope="col">선수·팀</th></tr></thead><tbody>'+(''.join(rows) or '<tr><td colspan="2">— · 자료 미입력</td></tr>')+'</tbody></table>')
def short(name,country):
 if name in KOR:return KOR[name]
 parts=name.split()
 return parts[0] if country in ('CHN','TPE','China','Chinese Taipei') else parts[-1]
def names(r):
 country=NOC.get(r['country'],r['country'])
 if len(r['members'])==1:return short(r['members'][0],country)+' ('+country+')'
 return country+' · '+' / '.join(short(n,country) for n in r['members'])
def results(data,event,key=None):
 rows=[]
 for r in data['results']:
  if r['event']!=event or (key and r['axis']!=key):continue
  full=r['country']+' · '+' / '.join(r['members'])
  value='<a href="'+h(r['source'])+'" title="'+h(full)+'" aria-label="'+h(full+' · '+r['result'])+'">'+h(names(r)+' · '+r['result'])+'</a>'
  rows.append('<tr id="record-'+r['id']+'"'+(' class="qualified"' if r['result']=='금' else '')+'><th scope="row">'+a(page(r['axis'])+'#event-'+event,r['competition'])+'</th><td>'+value+'</td></tr>')
 return table('대회 통합 결과 · 금 음영은 올림픽 쿼터와 별개',rows)
def paths(data,event,key=None):
 rows=[]
 if key in (None,'2025-cup','2025-final') and event in ('rm','rw','cm','cw'):
  for r in data['results']:
   if r['event']==event and r['axis']=='2025-cup' and r['result']=='금':
    note=' · 최종 출전 철회' if r['members']==['Kim Woo-jin'] else ''
    rows.append('<tr><th scope="row">'+a(FINAL,r['competition']+' → 파이널')+'</th><td>'+h(names(r)+note)+'</td></tr>')
 return table('개인 월드컵 우승에 따른 파이널 참가 경로',rows)+'<p class="small">개인전 우승 경로이며, 단체·혼성 우승을 개인 파이널 진출로 바꾸지 않습니다. LA28 출전권과 별개입니다.</p>' if event in ('rm','rw','cm','cw') else '<p class="small">단체·혼성 월드컵 결과는 개인 파이널 진출 명단이 아닙니다. LA28 배정은 '+a('olarchery.html#pathway','기존 예선 경로')+'에서 확인합니다.</p>'
def roster(event):
 data=json.loads((ROOT/'data/archery-final-roster.json').read_text(encoding='utf-8'))
 return table('2025 난징 파이널 · 공식 최종 명단',['<tr><th scope="row">'+a(FINAL,'2025 파이널')+'</th><td>'+h(KOR.get(n,n))+'</td></tr>' for n in data.get(event,[])])
def index():
 heads='<th scope="col">세부종목</th>'+''.join('<th scope="col">'+a(page(k),n)+'</th>' for k,n in AXES)
 rows=''.join('<tr><th scope="row">'+a('olarchery-ev-'+c+'.html',n)+'</th>'+''.join('<td>'+a(page(k)+'#event-'+c,'결과·명단')+'</td>' for k,_ in AXES)+'</tr>' for c,n in EVENTS.items())
 return '<section id="archery-index"><h2>세부종목 × 연도·대회</h2><p>2025 세계선수권 30개·월드컵 및 파이널 132개 입상 기록을 수록했습니다. 모바일은 표 안에서 좌우로 넘깁니다.</p><h3>올림픽 6종목</h3><nav class="arch-axis-links">'+''.join(a('olarchery-ev-'+c+'.html',n) for c,n in EVENTS.items())+'</nav><h3>연도·대회</h3><nav class="arch-axis-links">'+''.join(a(page(k),n) for k,n in AXES)+'</nav>'+scroll('<table class="arch-axis-matrix"><thead><tr>'+heads+'</tr></thead><tbody>'+rows+'</tbody></table>')+'</section>'
def css(t):
 t=re.sub(r'<link rel="stylesheet" href="\./css/archery-orthogonal.css[^\"]*">','',t)
 v=hashlib.sha256((ROOT/'css/archery-orthogonal.css').read_bytes()).hexdigest()[:12]
 return t.replace('</head>','<link rel="stylesheet" href="./css/archery-orthogonal.css?v='+v+'"></head>')
def write(p,t):p.write_text(t,encoding='utf-8',newline='\n')
def insert(t,block):
 t=re.sub(r'<!-- archery-orthogonal:start -->.*?<!-- archery-orthogonal:end -->','',t,flags=re.S)
 block='<!-- archery-orthogonal:start -->'+block+'<!-- archery-orthogonal:end -->'
 m=re.search(r'<section id="overview">.*?</section>',t,flags=re.S) if 'id="archery-index"' in block else None
 if m:return t[:m.end()]+block+t[m.end():]
 return t.replace('<main id="main">','<main id="main">'+block,1)
def render():
 d=json.loads((ROOT/'data/archery-pathways.json').read_text(encoding='utf-8'))
 p=ROOT/'olarchery.html';write(p,css(insert(p.read_text(encoding='utf-8'),index())))
 for c,n in EVENTS.items():
  p=ROOT/('olarchery-ev-'+c+'.html');block='<section id="competition-results"><h2>대회 결과·참가 경로</h2><p>'+a('olarchery.html#archery-index','세부종목 × 대회 목차')+'</p>'+results(d,c)+paths(d,c)+(roster(c) if c in ('rm','rw') else '')+'</section>'
  write(p,css(insert(p.read_text(encoding='utf-8'),block)))
 template=(ROOT/'olarchery.html').read_text(encoding='utf-8')
 for key,title in AXES:
  extra=OTHER if key in ('2025-world','2025-cup','2025-final') else {}
  contents='<p>'+a('olarchery.html#archery-index','← 세부종목 × 대회 목차')+'</p><nav class="arch-axis-links">'+''.join(a('#event-'+c,n) for c,n in EVENTS.items())+'</nav><p class="note">2025 위키 입상 표를 파싱했습니다. 컴파운드 여자 파이널은 위키와 달라 공식 결과로 정정했습니다. 미래 결과는 미입력이며 현재 페이지의 빈칸은 무메달을 뜻하지 않습니다.</p>'
  if key=='2026-ag':contents+='<p>'+a('olarchery-asia.html','기존 아시안게임 결과·쿼터 분석')+'</p>'
  for c,n in (EVENTS|extra).items():
   contents+='<section id="event-'+c+'"><h2>'+ (a('olarchery-ev-'+c+'.html#competition-results',n) if c in EVENTS else h(n+' · LA28 밖 종목'))+'</h2>'+results(d,c,key)+paths(d,c,key)+(roster(c) if key=='2025-final' and c in ('rm','rw','cm','cw') else '')+'</section>'
  contents+='<section id="sources"><h2>출처·수록 범위</h2><p>'+a('https://en.wikipedia.org/wiki/2025_Archery_World_Cup','Wikipedia · 2025 월드컵')+' · '+a('https://en.wikipedia.org/wiki/2025_World_Archery_Championships','Wikipedia · 2025 세계선수권')+' · '+a(FINAL,'World Archery · 공식 최종 명단')+'</p><p>원문 팀 구성원은 데이터와 링크 설명에 보존합니다. 전체 결과의 공식 대조는 아직 완료하지 않았습니다. 확인일 2026.10.11.</p></section>'
  t=re.sub(r'<main id="main">.*?</main>',lambda m:'<main id="main">'+contents+'</main>',template,flags=re.S)
  t=re.sub(r'<title>.*?</title>','<title>양궁 · '+title+'</title>',t)
  t=re.sub(r'<h1 class="title">.*?</h1>','<h1 class="title">양궁 · '+title+'</h1>',t)
  t=re.sub(r'<p class="intro">.*?</p>','<p class="intro">세부종목별 결과와 참가 경로</p>',t,count=1)
  t=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="양궁 '+title+' 종목별 결과·참가 경로">',t)
  write(ROOT/page(key),css(t.replace(' aria-current="page"','')))
if __name__=='__main__':render()
