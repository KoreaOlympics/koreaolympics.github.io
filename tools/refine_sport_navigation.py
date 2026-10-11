"""Refine wiki navigation while preserving existing qualification/source text."""
from pathlib import Path
import re,json,html
R=Path(__file__).resolve().parents[1];H=lambda s:html.escape(str(s),quote=True)
ORIGIN_FILE=R/'tools/research/navigation-originals.json'
ORIGINS=json.loads(ORIGIN_FILE.read_text(encoding='utf-8')) if ORIGIN_FILE.exists() else {}
def source(name):return ORIGINS.get(name,read(name)) if (R/name).exists() else ORIGINS[name]
def read(name):return (R/name).read_text(encoding='utf-8')
def write(name,t):
 t=re.sub(r'<link rel="stylesheet" href="(?:\./)?css/sports-wiki-refresh.css[^\"]*">','',t)
 t=t.replace('</head>','<link rel="stylesheet" href="./css/sports-wiki-refresh.css?v=20261012"></head>')
 if name.startswith(('olboxing','olbadminton')):
  sport='boxing' if name.startswith('olboxing') else 'badminton';idx='boxing-index' if sport=='boxing' else 'tour-index'
  nav='<nav class="footer-nav"><a href="ol'+sport+'.html#'+idx+'">연도·종목 목차</a><a href="ol'+sport+'.html#pathway">예선 안내</a><a href="index.html">올림픽 예선 목차</a></nav>'
  t=re.sub(r'<nav class="footer-nav".*?</nav>',nav,t,count=1,flags=re.S)
 (R/name).write_text(t,encoding='utf-8',newline='\n')
def main(t):return re.search(r'<main[^>]*>(.*?)</main>',t,re.S)[1]
def setmain(t,b):return re.sub(r'<main[^>]*>.*?</main>',lambda m:'<main id="main">'+b+'</main>',t,count=1,flags=re.S)
def anchor(p,label):return '<a href="'+H(p)+'">'+H(label)+'</a>'
def matrix(sport,weights,axes,title,qualifying):
 b=f'<section class="wiki-matrix-section" id="{"qualifying" if qualifying else "reference"}"><h3>{H(title)}</h3><p class="wiki-caption">{len(weights)}체급 · '+('직접 출전권·예선 랭킹 경로' if qualifying else '경쟁력 참고 · LA28 직접 출전권 없음')+'</p><div class="wiki-matrix-scroll" tabindex="0" role="region" aria-label="'+H(title)+'"><table class="wiki-matrix"><thead><tr><th scope="col">체급</th>'
 for key,label,note in axes:
  year=label.split()[0];name=label[len(year):].strip()
  b+='<th scope="col">'+anchor(f'ol{sport}-{key}.html',year)+'<br>'+anchor(f'ol{sport}-{key}.html',name)+f'<small>{H(note)}</small></th>'
 b+='</tr></thead><tbody>';previous=None
 for code,label in weights:
  group=('남자 자유형' if code.startswith('fs') else '그레코로만형' if code.startswith('gr') else '여자 자유형') if sport=='wrestling' else ('남자' if code.startswith('m') else '여자')
  if group!=previous:
   previous=group;count=sum((c.startswith(code[:2]) if sport=='wrestling' else c[0]==code[0]) for c,_ in weights)
   b+=f'<tr class="wiki-group"><th colspan="{len(axes)+1}">{group} <span>{count}체급</span></th></tr>'
  shortlabel=label.split()[-1]
  b+='<tr><th scope="row">'+anchor(f'ol{sport}-ev-{code}.html',shortlabel)+'</th>'+''.join('<td>'+anchor(f'ol{sport}-{key}.html#'+('weight-' if sport=='boxing' else '')+code,'명단' if 'quota' in key else '보기')+'</td>' for key,_,_ in axes)+'</tr>'
 return b+'</tbody></table></div></section>'
def wrestling():
 weights=[(prefix+str(w),label+' '+str(w)+'kg') for prefix,label,ws in [('fs','남자 자유형',[57,65,74,86,97,125]),('gr','그레코로만형',[60,67,77,87,97,130]),('ww','여자 자유형',[50,53,57,62,68,76])] for w in ws]
 q=[('2027-world','2027 세계선수권','직행 · 체급별 4명'),('2027-series','2027 랭킹시리즈','랭킹 · 3개 대회'),('2027-continental','2027 대륙선수권','랭킹 반영'),('2028-ranking','2028 랭킹 결산','랭킹 · 미확보 3명'),('2028-continental','2028 대륙예선','직행 · 권역별 2명'),('2028-world-qualifier','2028 세계예선','직행 · 체급별 1명')]
 other=[('2026-world','2026 세계선수권','다음 시즌 시드 참고'),('2026-ag','2026 아시안게임','국제대회·한국 성적')]
 block='<section id="orthogonal"><h2>18체급 × 연도·대회</h2><p>남자 자유형 6 · 그레코로만형 6 · 여자 자유형 6. 예선 대회를 먼저 확인하고, 체급을 누르면 전체 결과와 선수 정보로 이동합니다.</p>'+matrix('wrestling',weights,q,'올림픽 예선 관련 대회',True)+matrix('wrestling',weights,other,'올림픽 예선과 직접 무관한 대회',False)+'<p class="small">2027 대륙선수권은 랭킹 대회, 2028 대륙예선은 직접 출전권 대회입니다. 날짜순보다 예선 역할을 우선해 배열했습니다.</p></section>'
 t=source('olwrestling.html');t=re.sub(r'<!-- four:start -->.*?<!-- four:end -->','<!-- four:start -->'+block+'<!-- four:end -->',t,count=1,flags=re.S)
 t=re.sub(r'(2027 세계선수권 메달 4 \+ UWW 랭킹 3 \+ 대륙 예선 4개 × 2 8 \+ 세계 예선 1 = 16명)','16명',t)
 t=t.replace('<body>','<body class="wrestling-wiki">');write('olwrestling.html',t)
 for p in R.glob('olwrestling-*.html'):write(p.name,p.read_text(encoding='utf-8').replace('<body>','<body class="wrestling-wiki">'))
def boxing():
 weights=[(f'm{x}',f'남자 {x}kg') for x in [55,60,65,70,80,90]]+[('mo90','남자 +90kg')]+[(f'w{x}',f'여자 {x}kg') for x in [51,54,57,60,65,70,75]]
 q=[('2027-wc','2027 세계선수권','첫 올림픽 예선'),('2027-28-continental','2027–28 대륙예선','아시아 등 5권역'),('2028-wqt1','2028 세계예선 1','미확보 체급 대상'),('2028-wqt2','2028 세계예선 2','마지막 세계예선'),('2028-quota','2028 출전권 결산','최종 배정 명단')]
 other=[('2025-wc','2025 세계선수권','참고 성적'),('2025-cup','2025 월드복싱컵','시리즈·파이널'),('2026-cup','2026 월드복싱컵','참고 성적'),('2026-asia','2026 아시아선수권','대륙 예선과 별개'),('2026-ag','2026 아시안게임','한국 성적 참고')]
 block='<section class="box-index" id="boxing-index"><h2>14체급 × 연도·대회</h2><p>남자 7체급 · 여자 7체급. 각 체급의 결과·한국 선수 정보와 대회별 전체 기록을 교차 연결합니다.</p>'+matrix('boxing',weights,q,'올림픽 예선 관련 대회',True)+matrix('boxing',weights,other,'올림픽 예선과 직접 무관한 대회',False)+'</section>'
 t=source('olboxing.html');t=re.sub(r'<!-- boxing-orthogonal:start -->.*?<!-- boxing-orthogonal:end -->','',t,flags=re.S);t=t.replace('<main id="main">','<main id="main">'+block,1)
 # Existing main qualification text stays. All tabs use the two matrix axes.
 t=re.sub(r'<nav class="golf-nav".*?</nav>','<nav class="golf-nav"><a href="olboxing.html">예선 안내</a><a href="#qualifying">예선 관련 대회</a><a href="#reference">참고 대회</a></nav>',t,count=1,flags=re.S)
 removed={'olboxing-events.html':'olboxing.html#boxing-index','olboxing-men.html':'olboxing.html#qualifying','olboxing-women.html':'olboxing.html#qualifying','olboxing-athletes.html':'olboxing.html#boxing-index','olboxing-squad.html':'olboxing.html#korea'}
 for c,label in weights:
  p=f'olboxing-ev-{c}.html'
  if p in ORIGINS:(R/p).write_text(ORIGINS[p],encoding='utf-8')
 # Preserve additional tab content in corresponding weight pages, under collapsible details.
 for old,target in removed.items():
  if not (R/old).exists() and old not in ORIGINS:continue
  content=main(source(old));content=re.sub(r'<!-- boxing-orthogonal:start -->.*?<!-- boxing-orthogonal:end -->','',content,flags=re.S)
  content=re.sub(r'<nav class="toc".*?</nav>','',content,flags=re.S)
  content=re.sub(r'id="([^"]+)"',lambda m:'id="legacy-'+old[:-5]+'-'+m[1]+'"',content)
  content=re.sub(r'href="#([^"]+)"',lambda m:'href="#legacy-'+old[:-5]+'-'+m[1]+'"',content)
  if old!='olboxing-events.html':
   for c,label in weights:
    if ('-men' in old and not c.startswith('m')) or ('-women' in old and not c.startswith('w')):continue
    p=f'olboxing-ev-{c}.html';s=read(p);s=s.replace('</main>','<details class="wiki-legacy"><summary>관련 선수·종목 자료</summary>'+content+'</details></main>');write(p,s)
  if (R/old).exists():(R/old).unlink()
 t=t.replace('<body>','<body class="boxing-wiki">');write('olboxing.html',t)
 for p in R.glob('*.html'):
  s=p.read_text(encoding='utf-8');old=s
  for name,target in removed.items():s=re.sub(re.escape(name)+r'(?:#[^"\s<>]*)?',target,s)
  if p.name.startswith('olboxing'):s=s.replace('<body>','<body class="boxing-wiki">');write(p.name,s)
  elif s!=old:p.write_text(s,encoding='utf-8',newline='\n')
LABELS={'Malaysia Open':'말레이시아 오픈','All England Open':'전영 오픈','Indonesia Open':'인도네시아 오픈','China Open':'중국 오픈','BWF World Tour Finals':'투어 파이널스'}
EVENTS={'ms':'남자 단식','ws':'여자 단식','md':'남자 복식','wd':'여자 복식','xd':'혼합 복식'}
KOR={'An Se-young':'안세영','Kim Won-ho':'김원호','Seo Seung-jae':'서승재','Baek Ha-na':'백하나','Lee So-hee':'이소희','Kim Hye-jeong':'김혜정','Kong Hee-yong':'공희용','Kim Ga-eun':'김가은','Jeong Na-eun':'정나은','Kim Ga-ram':'김가람','Lee Yeon-woo':'이연우','Sim Yu-jin':'심유진'}
NOC={'South Korea':'KOR','China':'CHN','Chinese Taipei':'TPE','Japan':'JPN','Denmark':'DEN','France':'FRA','England':'ENG','India':'IND','Indonesia':'INA','Thailand':'THA','Malaysia':'MAS','Singapore':'SGP'}
def bcell(y,c):return f'olbadminton-{y}-{c}.html'
def shortname(name,country):
 if name in KOR:return KOR[name]
 # East Asian names retain the full name for useful identification. Western names use family name.
 if country in ['China','Japan','Chinese Taipei','Hong Kong']:return name
 return name.split()[-1]
def nameview(r):
 if not r:return '<span class="wiki-muted">—</span>'
 country=NOC.get(r.get('country',''),r.get('country',''))
 text=' / '.join(shortname(n,r.get('country','')) for n in r['members']) if len(r['members'])<=2 else country
 full=' / '.join(r['members'])+' · '+r.get('country','')
 return f'<a class="{"wiki-kor" if country=="KOR" else ""}" href="{H(r["source"])}" title="{H(full)}" aria-label="{H(full)}">{H(text)}</a>'
def bresults(records,y,c):
 groups={}
 for r in records:
  if r['year']==y and r['event']==c:groups.setdefault(r['competition'],[]).append(r)
 rows=''
 for comp,rs in groups.items():
  gold=next((r for r in rs if r['result'] in ['우승','금']),None);silver=next((r for r in rs if r['result'] in ['준우승','은']),None)
  kor=[r for r in rs if r.get('country')=='South Korea'];notes=[]
  for r in kor:
   note='한국 '+({'우승':'우승','금':'우승','준우승':'준우승','은':'준우승','동':'동'}.get(r['result'],r['result']))
   if note not in notes:notes.append(note)
  alltext='; '.join(' / '.join(r['members'])+' · '+r['result'] for r in rs)
  rows+=f'<tr title="{H(alltext)}"><th scope="row">{H(LABELS.get(comp,comp))}</th><td>{nameview(gold)}</td><td>{nameview(silver)}</td><td>{H(' · '.join(notes) or '—')}</td></tr>'
 return '<div class="wiki-results-scroll" tabindex="0"><table class="wiki-results"><thead><tr><th scope="col">대회명</th><th scope="col">우승자</th><th scope="col">준우승자</th><th scope="col">비고</th></tr></thead><tbody>'+(rows or '<tr><td colspan="4">공표 결과 없음 · 일정 확정·결과 확인 후 추가</td></tr>')+'</tbody></table></div>'
def badminton():
 d=json.loads((R/'data/badminton-tour.json').read_text(encoding='utf-8'));records=d['results'];template=source('olbadminton.html')
 history=json.loads((R/'data/sports-results-2026.json').read_text(encoding='utf-8'))['badminton']
 rankings=json.loads((R/'data/badminton-rankings.json').read_text(encoding='utf-8'))['events']
 historical=[]
 for meet in history:
  if meet['year']>=2025:continue
  for label,podium in meet['podiums'].items():
   code=next((c for c,n in EVENTS.items() if n.replace('혼합','혼성')==label),None)
   if not code:continue
   for place,people in podium.items():
    for person in people:
     historical.append({'year':meet['year'],'event':code,'competition':meet['competition'],'result':{'1':'우승','2':'준우승','3':'동'}[place],'country':next((n for n,a in NOC.items() if a==person['noc']),person['noc']),'members':person['names'],'source':meet.get('source','https://bwfbadminton.com/')})
 sourceevents={c:source(f'olbadminton-ev-{c}.html') for c in EVENTS}
 oldtabs={name:source('olbadminton-'+name+'.html') for name in ['singles','doubles','ranking','athletes','squad'] if (R/('olbadminton-'+name+'.html')).exists() or 'olbadminton-'+name+'.html' in ORIGINS}
 matrix='<section id="tour-index"><h2>세부종목 × 연도</h2><p class="wiki-caption">5종목 · 4개 연도 · 20개 상세 페이지</p><div class="wiki-matrix-scroll" tabindex="0"><table class="wiki-matrix badminton-matrix"><thead><tr><th scope="col">세부종목</th>'+''.join('<th scope="col">'+anchor(f'olbadminton-{y}.html',str(y))+'</th>' for y in range(2025,2029))+'</tr></thead><tbody>'
 for c,n in EVENTS.items():matrix+='<tr><th scope="row">'+anchor('olbadminton-ev-'+c+'.html',n)+'</th>'+''.join('<td>'+anchor(bcell(y,c),'결과·정보')+'</td>' for y in range(2025,2029))+'</tr>'
 matrix+='</tbody></table></div></section>'
 maint=template;maint=re.sub(r'<!-- tour-orthogonal:start -->.*?<!-- tour-orthogonal:end -->','',maint,flags=re.S);maint=maint.replace('<main id="main">','<main id="main">'+matrix,1)
 maint=re.sub(r'<nav class="result-pills">.*?</nav>','',maint,flags=re.S);maint=maint.replace('<script src="js/sports-results.js"></script>','')
 maint=re.sub(r'<nav class="golf-nav".*?</nav>','<nav class="golf-nav"><a href="olbadminton.html#tour-index">20개 연도·종목</a><a href="olbadminton.html#pathway">예선 안내</a><a href="olbadminton.html#timeline">예선 일정</a></nav>',maint,count=1,flags=re.S)
 def basepage(title,intro,body):
  t=setmain(maint,body);t=re.sub(r'<title>.*?</title>',f'<title>{H(title)} | 올림픽예선</title>',t,count=1);t=re.sub(r'<h1 class="title">.*?</h1>',f'<h1 class="title">{H(title)}</h1>',t,count=1,flags=re.S);t=re.sub(r'<p class="intro">.*?</p>',f'<p class="intro">{H(intro)}</p>',t,count=1,flags=re.S)
  t=re.sub(r'<nav class="result-pills">.*?</nav>','',t,flags=re.S);t=re.sub(r'<script src="js/sports-results.js"></script>','',t)
  return t.replace('<body>','<body class="badminton-wiki">')
 for y in range(2025,2029):
  for c,n in EVENTS.items():
   body='<nav class="wiki-year-nav">'+''.join(anchor(bcell(yr,c),str(yr)) for yr in range(2025,2029))+'</nav><section id="results"><h2>주요 대회 결과</h2>'+bresults(records,y,c)+'</section><p class="small">—는 수록 자료의 추가 정보 없음. 동메달·전체 선수명은 각 행 설명과 원문에서 확인할 수 있습니다. 우승은 올림픽 출전권을 뜻하지 않습니다.</p>'
   if y in [2027,2028]:body+='<section id="qualification"><h2>LA28 예선에서의 위치</h2><p>올림픽 랭킹 적립 2027.05.03–2028.04.30 · 2028.05.02 랭킹으로 선발. '+('단식 16위 이내 국가당 최대 2명, 그 외 최대 1명.' if c in ['ms','ws'] else '복식 8위 이내 국가당 최대 2조, 그 외 최대 1조.')+'</p>'+anchor('olbadminton.html#pathway','전체 예선 규정')+'</section>'
   info=main(sourceevents[c]);info=re.sub(r'<!-- tour-orthogonal:start -->.*?<!-- tour-orthogonal:end -->','',info,flags=re.S);info=re.sub(r'<nav class="toc".*?</nav>','',info,flags=re.S)
   info=re.sub(r'id="([^"]+)"',lambda m:'id="profile-'+m[1]+'"',info);info=re.sub(r'href="#([^"]+)"',lambda m:'href="#profile-'+m[1]+'"',info)
   body+='<details class="wiki-legacy"><summary>종목·한국 선수 정보 · 자료 기준 2026.10</summary>'+info+'</details>'
   for name,t in oldtabs.items():
    if (name=='singles' and c not in ['ms','ws']) or (name=='doubles' and c in ['ms','ws']) or (name=='ranking' and y<2027) or (name in ['athletes','squad'] and y!=2026):continue
    content=main(t);content=re.sub(r'<!-- tour-orthogonal:start -->.*?<!-- tour-orthogonal:end -->','',content,flags=re.S);content=re.sub(r'<nav class="toc".*?</nav>','',content,flags=re.S);content=re.sub(r'id="([^"]+)"',lambda m:'id="legacy-'+name+'-'+m[1]+'"',content);content=re.sub(r'href="#([^"]+)"',lambda m:'href="#legacy-'+name+'-'+m[1]+'"',content)
    if name=='ranking':
     rank=rankings[c]
     rankbody='<section id="legacy-ranking-world-top20"><h2>'+H(n)+' · 세계랭킹 TOP 20</h2><p class="small">'+H(rank['date'])+' 기준 · '+anchor(rank['source'],'랭킹 원문')+' · 올림픽 출전권 확정 명단이 아닙니다.</p><div class="wiki-results-scroll"><table class="data"><thead><tr><th>순위</th><th>선수·조</th><th>NOC</th></tr></thead><tbody>'+''.join('<tr><td>'+str(r['rank'])+'</td><td>'+H(' / '.join(r['names']))+'</td><td>'+H(r['noc'])+'</td></tr>' for r in rank['rows'])+'</tbody></table></div></section>'
     content=re.sub(r'<section id="legacy-ranking-world-top20".*?</section>',lambda m:rankbody,content,count=1,flags=re.S)
     content=re.sub(r'<script.*?</script>','',content,flags=re.S)
    body+='<details class="wiki-legacy"><summary>'+{'singles':'단식 참고 자료','doubles':'복식 참고 자료','ranking':'올림픽 랭킹 규정','athletes':'한국 선수 자료','squad':'선수단 구성 참고'}[name]+'</summary>'+content+'</details>'
   # Non-Olympic team results are preserved outside the five-event Olympic result table.
   if y==2025:
    body+='<details class="wiki-legacy"><summary>이전 기록 · 2023–2024</summary>'+''.join('<h3>'+str(yr)+'</h3>'+bresults(historical,yr,c) for yr in [2023,2024])+'</details>'
   if y==2026 and c in ['ms','ws']:
    team='mt' if c=='ms' else 'wt';body+='<details class="wiki-legacy"><summary>아시안게임 단체전 · 별도 참고</summary>'+bresults(records,y,team)+'</details>'
   body+='<section id="sources"><h2>결과 출처</h2><ul>'+''.join('<li>'+anchor(s['url'],s['url'].split('/wiki/')[-1].replace('_',' '))+'</li>' for s in d['sources'])+'</ul><p class="small">기존 위키 표 파싱 자료 기준 2026.10.11. 공표되지 않은 미래 결과는 비워 둡니다.</p></section>'
   write(bcell(y,c),basepage(f'배드민턴 · {y} {n}',f'{y}년 {n} · 대회 결과·한국 선수·예선 정보',body))
  body='<nav class="wiki-year-nav">'+''.join(anchor(bcell(y,c),n) for c,n in EVENTS.items())+'</nav>'
  for c,n in EVENTS.items():body+=f'<section id="event-{c}"><h2>'+anchor(bcell(y,c),n)+'</h2>'+bresults(records,y,c)+'</section>'
  for c,n in [('mt','남자 단체'),('wt','여자 단체')]:
   if any(r['year']==y and r['event']==c for r in records):body+='<details class="wiki-legacy"><summary>'+n+' · 별도 참고</summary>'+bresults(records,y,c)+'</details>'
  write(f'olbadminton-{y}.html',basepage(f'배드민턴 · {y}년',f'{y}년 · 5종목 기록',body))
 for c,n in EVENTS.items():
  body='<section id="tour-results"><h2>'+H(n)+' · 4개 연도</h2><nav class="wiki-year-nav">'+''.join(anchor(bcell(y,c),str(y)) for y in range(2025,2029))+'</nav></section>'
  for y in range(2025,2029):body+=f'<section id="year-{y}"><h2>'+anchor(bcell(y,c),str(y))+'</h2>'+bresults(records,y,c)+'</section>'
  write(f'olbadminton-ev-{c}.html',basepage('배드민턴 · '+n,'연도별 결과와 종목 정보',body))
 removed={f'olbadminton-{name}.html':'olbadminton.html#'+('pathway' if name=='ranking' else 'tour-index') for name in oldtabs}
 removed['olbadminton-results.html']='olbadminton.html#tour-index'
 write('olbadminton.html',maint.replace('<body>','<body class="badminton-wiki">'))
 for old in removed:
  if (R/old).exists():(R/old).unlink()
 for p in R.glob('*.html'):
  s=p.read_text(encoding='utf-8');old=s
  for name,target in removed.items():s=re.sub(re.escape(name)+r'(?:#[^"\s<>]*)?',target,s)
  if s!=old:p.write_text(s,encoding='utf-8',newline='\n')
if __name__=='__main__':
 wrestling();boxing();badminton();print('Refined wrestling, boxing and badminton; created 20 badminton cells')
