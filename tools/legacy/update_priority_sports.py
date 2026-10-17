import re,json,hashlib
from pathlib import Path
from html import escape as E
from wiki_tables import Tables,text
R=Path(__file__).resolve().parents[2]
def a(url,label):return f'<a href="{url}">{E(label)}</a>'
def table(headers,rows):return '<div class="priority-scroll" tabindex="0"><table class="data"><thead><tr>'+''.join('<th>'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
css='.priority-scroll{max-width:100%;overflow-x:auto;margin:1rem 0}.priority-scroll td,.priority-scroll th{white-space:nowrap;padding:.6rem .8rem}.priority-scroll th:first-child{position:sticky;left:0;background:#f3f5f9}.priority-scroll tr:has(td:first-child[data-gold]){background:#fff4bd}.priority-links{display:flex;flex-wrap:wrap;gap:.5rem}.priority-links a{padding:.4rem .6rem;border:1px solid #ccd5df;background:#f7f9fc}.priority-note{padding:.8rem;background:#fff5d5}'
(R/'css/priority-sports.css').write_text(css,encoding='utf-8')
def styled(s):
 s=re.sub(r'<link rel="stylesheet" href="css/priority-sports.css[^\"]*">','',s)
 return s.replace('</head>','<link rel="stylesheet" href="css/priority-sports.css?v='+hashlib.sha256(css.encode()).hexdigest()[:10]+'"></head>')
def inject(path,body):
 s=path.read_text(encoding='utf-8');s=re.sub(r'<!-- priority:start -->.*?<!-- priority:end -->','',s,flags=re.S)
 block='<!-- priority:start -->'+body+'<!-- priority:end -->'
 if '<main id="main">' in s:s=s.replace('<main id="main">','<main id="main">'+block,1)
 else:s=re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+block,s,count=1)
 path.write_text(styled(s),encoding='utf-8',newline='\n')
def newpage(sport,key,title,body):
 s=(R/f'ol{sport}.html').read_text(encoding='utf-8')
 s=re.sub(r'<main\b[^>]*>.*?</main>','<main id="main">'+body+'</main>',s,flags=re.S)
 s=re.sub(r'<title>.*?</title>','<title>'+title+'</title>',s)
 s=re.sub(r'<h1\b[^>]*>.*?</h1>','<h1 class="title">'+title+'</h1>',s,count=1)
 if sport=='lacrosse':
  s=re.sub(r'<a\b([^>]*?)href="#(?:eligibility|men-asia|men-oqt|men-others|men-summary|references)"([^>]*)>',r'<a\1href="ollacrosse.html"\2>',s)
 (R/f'ol{sport}-{key}.html').write_text(styled(s),encoding='utf-8',newline='\n')
def matrix(sport,events,axes):
 return '<section id="priority-matrix"><h2>종목 × 주요 예선 대회</h2>'+table(['종목']+[a(f'ol{sport}-{k}.html',n) for k,n,note,src in axes],[[a(file,name)]+[a(f'ol{sport}-{k}.html#{id}','보기') for k,_,_,_ in axes] for id,name,file in events])+'</section>'
# Official IJF result tables alternate men and women; preserve every listed placing.
raw=(R.parent/'ijf-baku-2026.html').read_text(encoding='utf-8')
result_tables=[t for t in Tables(raw).tables if t['rows'] and len(t['rows'][0])==5 and text(t['rows'][0][1])=='1']
order=['m60','w48','m66','w52','m73','w57','m81','w63','m90','w70','m100','w78','mo100','wo78']
if len(result_tables)==28:
 assert [[text(c) for c in t['rows'][0]] for t in result_tables[:14]]==[[text(c) for c in t['rows'][0]] for t in result_tables[14:]]
 result_tables=result_tables[:14]
assert len(result_tables)==14,len(result_tables)
records=[]
for key,t in zip(order,result_tables):
 for row in t['rows']:
  cells=[text(c) for c in row]
  if len(cells)==5 and cells[1].isdigit():records.append({'event':key,'rank':int(cells[1]),'name':cells[3],'noc':cells[4]})
(R/'data/judo-world-2026.json').write_text(json.dumps({'source':'https://www.ijf.org/competition/3151/results','checked':'2026-10-11','sha256':hashlib.sha256(raw.encode()).hexdigest(),'results':records},ensure_ascii=False,indent=2),encoding='utf-8')
events=[(k,('남자 ' if k[0]=='m' else '여자 ')+('+' if k[1]=='o' else '-')+k.lstrip('mwo')+'kg',f'oljudo-ev-{k}.html') for k in order]
axes=[('2026-world','2026 세계선수권','바쿠 · 개인전 10.04–10.10. 결과는 랭킹 성적이며 메달만으로 LA28 쿼터가 확정되지 않습니다.','https://www.ijf.org/competition/3151/results'),('2027-tour','2027 IJF 투어','그랜드슬램·그랑프리·세계선수권·대륙선수권의 결과를 올림픽 랭킹과 연결합니다. 개별 일정·결과는 발표 후 반영.','https://www.ijf.org/calendar'),('2028-ranking','2028 최종 랭킹','2028.06.12 마감. 국가 상한·대륙 배정·혼성단체 자격을 적용한 최종 명단 확인.','https://www.ijf.org/wrl_olympic')]
for k,n,note,src in axes:
 body='<h2>'+n+'</h2><p>'+note+'</p><p>'+a(src,'공식 근거')+' · 확인 2026.10.11</p><p>공식 상위 8위 결과에서 메달리스트와 한국 선수를 발췌했습니다. 8위 밖 한국 선수의 전체 출전 결과는 별도 확인이 필요합니다.</p>'
 for id,name,file in events:
  rows=[[str(x['rank']),E(x['name'])+' · '+x['noc']] for x in records if x['event']==id and (x['rank']<=3 or x['noc']=='KOR')] if k=='2026-world' else [['확인 대기','대회별 결과·랭킹 발표 후 반영']]
  body+='<section id="'+id+'"><h2>'+a(file,name)+'</h2>'+table(['순위','선수 · 국가'],rows)+'</section>'
 newpage('judo',k,n,body)
inject(R/'oljudo.html',matrix('judo',events,axes)+'<p class="priority-note">바쿠 개인전 결과 업데이트: '+a('oljudo-2026-world.html','체급별 메달·한국 성적')+' · 세계랭킹과 LA28 올림픽 랭킹은 구분해 봅니다.</p>')
for id,name,file in events:
 rows=[[a('oljudo-2026-world.html#'+id,'2026 세계선수권'),str(x['rank'])+'위 · '+E(x['name'])+' · '+x['noc']] for x in records if x['event']==id and (x['rank']<=3 or x['noc']=='KOR')]
 inject(R/file,'<section id="priority-results"><h2>바쿠 세계선수권 결과</h2>'+table(['대회','선수 · 결과'],rows)+'</section>')
# Lacrosse: verified final standings and world-championship recipients.
src='https://worldlacrosse.sport/2026-asia-pacific-sixes-lacrosse-championships-conclude-after-six-days/'
standings={'men':['호주','일본','필리핀','중국','대만','홍콩','뉴질랜드','한국','인도','싱가포르','사우디아라비아'],'women':['일본','호주','한국','필리핀','뉴질랜드','대만','중국','홍콩','인도','싱가포르']}
body='<section id="apslc-results"><h2>2026 아시아·태평양 식스 최종 결과</h2><p class="priority-note">한국 여자 3위 · 2027 세계선수권 진출. 남자 8위 · 이 대회 상위 5팀 진출 경로에서는 탈락. LA28 본선 확보와는 별개입니다.</p>'+table(['부문','세계선수권 진출국'],[[g,' · '.join(v[:5])] for g,v in [('남자',standings['men']),('여자',standings['women'])]])
for gender,values in standings.items():body+='<section id="'+gender+'"><h3>'+('남자' if gender=='men' else '여자')+'</h3>'+table(['순위','국가'],[[str(i),v] for i,v in enumerate(values,1)])+'</section>'
body+='<p>한국 여자 동메달 결정전: 필리핀에 16–11 승. '+a(src,'World Lacrosse 공식 최종 결과')+' · 확인 2026.10.11</p></section>'
newpage('lacrosse','2026-asia','2026 라크로스 식스 아시아·태평양',body)
for file in ['ollacrosse.html','ollacrosse-men.html','ollacrosse-women.html']:inject(R/file,body)
# Gymnastics: discipline/event pages intersect qualification meets.
ge=[('artistic','기계체조','olgymnastics-artistic.html'),('rhythmic','리듬체조','olgymnastics-rhythmic.html'),('trampoline','트램펄린','olgymnastics-trampoline.html')]
ga=[('2026-world','2026 세계선수권','기계체조: 로테르담 10.17–25 · 남녀 단체 상위 3개국 경로. 리듬체조와 트램펄린은 각각의 공식 결과·규정을 확인합니다.','https://www.gymnastics.sport/site/events/detail.php?id=17247&type=sport'),('2027-world','2027 세계선수권','기계체조 단체·개인종합·종목별, 리듬체조 개인·단체, 트램펄린 개인 경로를 디시플린별로 구분.','https://www.gymnastics.sport/site/rules/'),('2027-28-cup','2027–2028 월드컵','기계체조 종목별·리듬체조·트램펄린은 서로 다른 랭킹 및 대회 반영 규정을 적용.','https://www.gymnastics.sport/site/rules/')]
ce=[(k,n,f'olcycling-{k}.html') for k,n in [('track','트랙'),('road','도로'),('mtb','MTB'),('bmxr','BMX 레이싱'),('bmxf','BMX 프리스타일')]]
ca=[('2026-world','2026 세계선수권','트랙: 상하이 10.14–18. 도로·MTB·BMX는 별도 대회 및 예선 기간을 적용합니다.','https://www.uci.org/competition-hub/2026-tissot-uci-track-world-championships/39Is0rqaU5PS9XcOIiiqBN'),('2027-season','2027 주요 대회·랭킹','세계선수권·월드컵 및 국가 랭킹을 디시플린별로 확인. 국가별 쿼터와 개인 결과는 별도 표로 관리.','https://www.uci.org/'),('2028-quota','2028 쿼터 결산','국가별 랭킹 상한 및 디시플린별 직접 예선 경로를 적용해 확보국을 확인.','https://www.uci.org/inside-uci/constitutions-regulations/regulations')]
for sport,ev,ax in [('gymnastics',ge,ga),('cycling',ce,ca)]:
 inject(R/f'ol{sport}.html',matrix(sport,ev,ax))
 for key,title,note,source in ax:
  b='<h2>'+title+'</h2><p>'+note+'</p><p>'+a(source,'공식 대회·규정')+' · 확인 2026.10.11</p>'
  for id,name,file in ev:
   state='결과·참가 명단 확인 대기'
   if key=='2026-world' and id=='track':state='10.14–18 · 상하이 · 개최 전'
   if key=='2026-world' and id=='artistic':state='10.17–25 · 로테르담 · 개최 전'
   b+='<section id="'+id+'"><h2>'+a(file,name)+'</h2>'+table(['대회·경로','상태'],[[title,state]])+'</section>'
  newpage(sport,key,title,b)
 for id,name,file in ev:inject(R/file,'<section id="priority-events"><h2>주요 예선 대회 문서</h2>'+table(['대회','세부종목'],[[a(f'ol{sport}-{key}.html#{id}',title),name] for key,title,note,src in ax])+'</section>')
# Replace old PDF references only where the latest wording has been reviewed.
for p in R.glob('olweightlifting*.html'):
 s=p.read_text(encoding='utf-8').replace('https://stillmed.olympics.com/media/Documents/Olympic-Games/LA28/WLF-LA28-Qualification-System.pdf','https://iwf.sport/wp-content/plugins/download-monitor/download.php?id=2934')
 s=s.replace('PDF, 2026.05.12','PDF, 2026.10.02').replace('Version as of 12 May 2026','Version as of 2 October 2026')
 p.write_text(s,encoding='utf-8',newline='\n')
note='<section id="latest-rule"><h2>2026.10.02판 규정 보완</h2><p>최신판은 여성 비올림픽 체급을 49kg으로 정정하고 Best Lifter 미사용 쿼터 재배정을 본문에 포함했습니다. Best Lifter 국가는 자동 추가 선수를 얻는 것이 아니라, 해당 성별 선수들이 일반 예선 경로로 자격을 얻고 국가 상한에 도달했을 때 최대 4명까지 허용됩니다.</p><p>참가 자격은 현행 올림픽 헌장·IOC 여성 카테고리 정책·반도핑 규정 준수를 요구합니다. 예선 참가 선수 정보와 소재지 정보는 해당 대회 최소 3개월 전에 제출해야 합니다.</p><p>'+a('https://iwf.sport/wp-content/plugins/download-monitor/download.php?id=2934','IWF 최신 규정 · C 및 F, 부록')+' · 규정 보완 확인 2026.10.11. 기존 한국 전망 날짜는 별도입니다.</p></section>'
for p in R.glob('olweightlifting*.html'):inject(p,note)
print('Updated priority sports; IJF records:',len(records))
