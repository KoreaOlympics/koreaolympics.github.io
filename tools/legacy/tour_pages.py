"""Annual orthogonal views for badminton and table tennis. Usage: [sport]."""
import hashlib,html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPORTS={'badminton':{'label':'배드민턴','events':{'ms':'남자 단식','ws':'여자 단식','md':'남자 복식','wd':'여자 복식','xd':'혼합 복식'}},'tabletennis':{'label':'탁구','events':{'ms':'남자 단식','ws':'여자 단식','md':'남자 복식','wd':'여자 복식','xd':'혼합 복식','xt':'혼성 단체'}}}
NOC={'South Korea':'KOR','Korea Sud':'KOR','China':'CHN','China Volksrepublik':'CHN','Chinese Taipei':'TPE','Japan':'JPN','France':'FRA','Frankreich':'FRA','Germany':'GER','Deutschland':'GER','Brazil':'BRA','Brasilien':'BRA','Malaysia':'MAS','Indonesia':'INA','Thailand':'THA','Denmark':'DEN','Canada':'CAN','India':'IND','Singapore':'SGP','Sweden':'SWE','Hong Kong':'HKG','England':'ENG','Iran':'IRI','Portugal':'POR','North Korea':'PRK','Australia':'AUS','Austria':'AUT','Romania':'ROU'}
KOR={'An Se-young':'안세영','Kim Won-ho':'김원호','Seo Seung-jae':'서승재','Baek Ha-na':'백하나','Lee So-hee':'이소희','Kim Hye-jeong':'김혜정','Kong Hee-yong':'공희용','Yoo Tae-bin':'유태빈','Shin Yu-bin':'신유빈','Shin Yubin':'신유빈','Lim Jong-hoon':'임종훈','Lim Jonghoon':'임종훈','Joo Cheonhui':'주천희','Joo Cheon-hee':'주천희','Oh Junsung':'오준성','Oh Jun-sung':'오준성','An Jae-hyun':'안재현','An Jaehyun':'안재현','Jang Woo-jin':'장우진','Kim Na-yeong':'김나영','Cho Dae-seong':'조대성','Lee Sang-su':'이상수'}
LABELS={'Malaysia Open':'말레이시아 오픈','All England Open':'전영 오픈','Indonesia Open':'인도네시아 오픈','China Open':'중국 오픈','BWF World Tour Finals':'월드투어 파이널스','Singapore Smash':'싱가포르 스매시','United States Smash':'미국 스매시','Europe Smash - Sweden':'유럽 스매시','Europe Smash':'유럽 스매시','China Smash':'중국 스매시'}
def h(s):return html.escape(str(s),quote=True)
def a(url,label):return '<a href="'+h(url)+'">'+h(label)+'</a>'
def event_page(sport,event):return 'ol'+sport+('-ev-' if sport=='badminton' else '-')+('team' if event=='xt' else event)+'.html'
def year_page(sport,year):return 'ol'+sport+'-'+str(year)+'.html'
def data(sport):return json.loads((ROOT/('data/'+sport+'-tour.json')).read_text(encoding='utf-8'))
def scroll(s):return '<div class="tour-scroll" tabindex="0" role="region" aria-label="좌우로 넘기는 표">'+s+'</div>'
def short(name,country):
 if name in KOR:return KOR[name]
 if country in ('CHN','TPE','HKG'):return name.split()[0]
 if country=='KOR':return name.split()[0]+' '+''.join(x[:1] for x in name.split()[1:])
 return name.split()[-1]
def result_table(sport,event,year=None):
 rows=[]
 for r in data(sport)['results']:
  if r['event']!=event or (year and r['year']!=year):continue
  country=NOC.get(r['country'],r['country']);members=r['members']
  display=country+' · '+str(len(members))+'명' if len(members)>2 else ' / '.join(short(n,country) for n in members)+(' ('+country+')' if country else '')
  full=' / '.join(members)+(' · '+r['country'] if r['country'] else '')
  value='<a href="'+h(r['source'])+'" title="'+h(full)+'" aria-label="'+h(full+' · '+r['result'])+'">'+h(display+' · '+r['result'])+'</a>'
  competition=str(r['year'])+' '+LABELS.get(r['competition'],r['competition'])
  rows.append('<tr id="result-'+r['id']+'"'+(' class="qualified"' if r['result'] in ('금','우승') else '')+'><th scope="row">'+a(year_page(sport,r['year'])+'#event-'+event,competition)+'</th><td>'+value+'</td></tr>')
 return scroll('<table class="tour-results"><caption>주요 대회 통합 결과</caption><thead><tr><th scope="col">대회</th><th scope="col">선수·팀 · 결과</th></tr></thead><tbody>'+(''.join(rows) or '<tr><td colspan="2">— · 결과 미입력</td></tr>')+'</tbody></table>')
def index(sport):
 events=SPORTS[sport]['events'];heads='<th scope="col">세부종목</th>'+''.join('<th scope="col">'+a(year_page(sport,y),str(y)+'년')+'</th>' for y in range(2025,2029))
 rows=''.join('<tr><th scope="row">'+a(event_page(sport,c),n)+'</th>'+''.join('<td>'+a(year_page(sport,y)+'#event-'+c,'대회 결과')+'</td>' for y in range(2025,2029))+'</tr>' for c,n in events.items())
 return '<section id="tour-index"><h2>세부종목 × 연도</h2><p>연도 문서는 주요 대회의 결과를 종목별로 모으고, 종목 문서는 여러 연도의 결과를 한 표로 연결합니다. 모바일 표는 좌우로 넘깁니다.</p><h3>세부종목</h3><nav class="tour-links">'+''.join(a(event_page(sport,c),n) for c,n in events.items())+'</nav><h3>연도</h3><nav class="tour-links">'+''.join(a(year_page(sport,y),str(y)+'년') for y in range(2025,2029))+'</nav>'+scroll('<table class="tour-matrix"><thead><tr>'+heads+'</tr></thead><tbody>'+rows+'</tbody></table>')+'</section>'
def css(t):
 t=re.sub(r'<link rel="stylesheet" href="\./css/tour-orthogonal.css[^\"]*">','',t)
 v=hashlib.sha256((ROOT/'css/tour-orthogonal.css').read_bytes()).hexdigest()[:12]
 return t.replace('</head>','<link rel="stylesheet" href="./css/tour-orthogonal.css?v='+v+'"></head>')
def insert(t,block,is_main=False):
 t=re.sub(r'<!-- tour-orthogonal:start -->.*?<!-- tour-orthogonal:end -->','',t,flags=re.S)
 block='<!-- tour-orthogonal:start -->'+block+'<!-- tour-orthogonal:end -->'
 m=re.search(r'<section id="overview">.*?</section>',t,flags=re.S) if is_main else None
 if m:return t[:m.end()]+block+t[m.end():]
 return t.replace('<main id="main">','<main id="main">'+block,1)
def write(p,t):p.write_text(t,encoding='utf-8',newline='\n')
def coverage(sport,year):
 results=[r for r in data(sport)['results'] if r['year']==year]
 meetings=sorted({(r['category'],r['competition']) for r in results})
 rows=['<tr><th scope="row">'+h(category)+'</th><td>'+h(LABELS.get(comp,comp))+'</td></tr>' for category,comp in meetings]
 if year==2026:
  rows.append('<tr><th scope="row">'+('파이널스' if sport=='badminton' else '그랜드 스매시')+'</th><td>'+('월드투어 파이널스 · 미래 대회, 결과 없음' if sport=='badminton' else '중국 스매시 · 원문 결과 미입력')+'</td></tr>')
 return scroll('<table class="tour-results"><caption>이 연도의 주요 대회 · 수록 범위</caption><thead><tr><th scope="col">분류</th><th scope="col">대회</th></tr></thead><tbody>'+(''.join(rows) or '<tr><td colspan="2">공식 일정 확정·결과 확인 후 추가</td></tr>')+'</tbody></table>')
def render(sport):
 config=SPORTS[sport];events=config['events'];p=ROOT/('ol'+sport+'.html')
 write(p,css(insert(p.read_text(encoding='utf-8'),index(sport),True)))
 for c,n in events.items():
  p=ROOT/event_page(sport,c)
  block='<section id="tour-results"><h2>'+n+' · 연도별 주요 대회</h2><p>'+a('ol'+sport+'.html#tour-index','세부종목 × 연도 목차')+' · 우승 음영은 올림픽 출전권을 뜻하지 않습니다.</p>'+result_table(sport,c)+'</section>'
  write(p,css(insert(p.read_text(encoding='utf-8'),block)))
 template=(ROOT/('ol'+sport+'.html')).read_text(encoding='utf-8')
 for year in range(2025,2029):
  extra={c:('남자 단체' if c=='mt' else '여자 단체') for c in ('mt','wt') if any(r['year']==year and r['event']==c for r in data(sport)['results'])}
  description='세계선수권 · 파이널스 · 아시안게임(개최 연도) · Super 1000 네 대회' if sport=='badminton' else '세계선수권 · 월드컵 · 아시안게임(개최 연도) · 그랜드 스매시'
  content='<p>'+h(description)+'</p>'+coverage(sport,year)+'<nav class="tour-links">'+''.join(a('#event-'+c,n) for c,n in events.items())+'</nav><p class="note">위키 원문에서 확인한 기록만 수록합니다. 2027–28 결과는 아직 없습니다. 빈칸은 미출전·무메달을 뜻하지 않습니다. 대회 우승을 올림픽 출전권으로 자동 변환하지 않습니다.</p>'
  if sport=='tabletennis':content+='<p class="small">2026 그랜드 스매시는 원문에 있는 우승자만 수록하며 준우승자는 미입력입니다. 남녀 단체 세계선수권은 LA28 혼성 단체와 다른 종목이므로 아래 별도 보존합니다. 혼성단체 월드컵과 혼합복식도 구분합니다.</p>'
  for c,n in (events|extra).items():
   content+='<section id="event-'+c+'"><h2>'+ (a(event_page(sport,c)+'#tour-results',n) if c in events else h(n+' · 원문 별도 종목'))+'</h2>'+result_table(sport,c,year)+'</section>'
  sources=data(sport)['sources'];content+='<section id="sources"><h2>출처·자료 기준</h2><p>확인 2026.10.11. 위키 표 파싱 자료이며 전체 기록의 공식 결과표 대조는 완료하지 않았습니다. 국가와 전체 이름·복식 및 단체 구성원은 데이터와 링크 설명에 보존합니다.</p><ul>'+''.join('<li>'+a(s['url'],s['url'].split('/wiki/')[-1].replace('_',' '))+'</li>' for s in sources)+'</ul></section>'
  t=re.sub(r'<main id="main">.*?</main>',lambda m:'<main id="main">'+content+'</main>',template,flags=re.S)
  title=config['label']+' · '+str(year)+' 주요 대회'
  t=re.sub(r'<title>.*?</title>','<title>'+title+'</title>',t);t=re.sub(r'<h1 class="title">.*?</h1>','<h1 class="title">'+title+'</h1>',t)
  t=re.sub(r'<p class="intro">.*?</p>','<p class="intro">'+a('ol'+sport+'.html#tour-index','← 세부종목 × 연도 목차')+'</p>',t,count=1)
  t=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+title+' 세부종목별 결과">',t)
  write(ROOT/year_page(sport,year),css(t.replace(' aria-current="page"','')))
if __name__=='__main__':
 for sport in sys.argv[1:] or SPORTS:render(sport)
