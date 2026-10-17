"""Single-source rendering for weight, annual tournament and athlete wiki pages."""
from pathlib import Path
import html,json,re
from build_medal_views import CHINESE
import taekwondo_rules as rules
ROOT=Path(__file__).resolve().parents[2]
D=rules.D;E=rules.E;H=rules.H
AXES=[('2025-gp-challenge','2025 GP 챌린지',['gpc1','gpc2','gpc3']),('2026-gp','2026 GP',['gp26a','gp26b','gp26c','gpf26']),('2027-gp','2027 GP·챌린지',['gp27a','gp27b','gp27c','gpc27','gpf27']),('2025-gs-qual','2025 GS 챌린지',['gsc25']),('2026-gs','2026 GS',['gsc26','gscs26']),('2027-gs','2027 GS',['gsc27','gscs27']),('2025-wc','2025 세계선수권',['wc25']),('2027-wc','2027 세계선수권',['wc27']),('2026-ag','2026 아시안게임',['ag26']),('2026-women-open','2026 여자 오픈',['women26']),('2026-continental','2026 대륙선수권',['cu26']),('2028-continental','2028 대륙 예선',[])]
rules.AXES=AXES
AX={eid:key for key,title,ids in AXES for eid in ids}
PEOPLE=json.loads((ROOT/'tools/legacy/research/tkd_judo.json').read_text(encoding='utf-8'))['taekwondo']['events']
SLUGS={'박태준':'park-tae-joon','배준서':'bae-jun-seo','문진호':'mun-jinho','성유현':'seong-yu-hyeon','서건우':'seo-geon-woo','강재권':'kang-jaegwon','강상현':'kang-sanghyun','김향기':'kim-hyanggi','이유민':'lee-yumin','김유진':'kim-yujin','곽민주':'kwak-minju','송다빈':'song-dabin','서은수':'seo-eunsu','장준':'jang-jun','박우혁':'park-woo-hyeok','홍효림':'hong-hyorim'}
rules.KO.update({'KIM Hyanggi':'김향기','AN Hyangsik':'안향식','KWAK Min Ju':'곽민주','MUN Jinho':'문진호','HONG Hyo Rim':'홍효림','HONG Hyo rim':'홍효림','YANG Hui-chan':'양희찬','SEO Yeo-won':'서여원','LEE Ga-eun':'이가은'})
for code,name,en in [('m58','서은수','SEO Eunsu'),('m68','장준','JANG Jun'),('mo80','박우혁','PARK Woo-Hyeok'),('w67','홍효림','HONG Hyo Rim')]:
 if not any(a['name']==name for a in PEOPLE[code]['athletes']):PEOPLE[code]['athletes'].append({'name':name,'name_en':en,'birth':None,'affiliation':None,'results':[],'sources':[]})
TEMPLATE=(ROOT/'oltaekwondo.html').read_text(encoding='utf-8')
REMOVED={'oltaekwondo-men.html':'oltaekwondo.html#classes','oltaekwondo-women.html':'oltaekwondo.html#classes','oltaekwondo-ranking.html':'oltaekwondo.html#rules','oltaekwondo-athletes.html':'oltaekwondo.html#athletes','oltaekwondo-squad.html':'oltaekwondo.html#athletes','oltaekwondo-continental.html':'oltaekwondo-2028-continental.html','oltaekwondo-2026-entries.html':'oltaekwondo.html#entry','oltaekwondo-2028-quota.html':'oltaekwondo.html#rules','oltaekwondo-2026-other.html':'oltaekwondo.html#tournaments','oltaekwondo-results.html':'oltaekwondo.html#timeline'}
def personlink(name):
 name=rules.KO.get(name,name)
 return f'<a href="./oltaekwondo-p-{SLUGS[name]}.html">{H(name)}</a>' if name in SLUGS else H(name)
def athlete(a,compact=False):
 name=rules.KO.get(a['name'],a['name'])
 if name in SLUGS:return personlink(name)+f' <span class="tkd-country">{H(a["country"])}</span>'
 label=CHINESE.get(a['name'],name) if a['country']=='CHN' else rules.SHORT.get(a['name'],name) if compact else name
 return f'<span title="{H(name)}">{H(label)}</span> <span class="tkd-country">{H(a["country"])}</span>'
rules.athlete=athlete
def refs(e):
 urls={D['sources'][s]['url']:D['sources'][s]['title'] for s in e['sources']}
 if e.get('resultUrl'):urls[e['resultUrl']]='대회 결과'
 for i,u in enumerate(e.get('medalSources',[])):urls[u]=f'공식 {i+1}일차 메달표'
 return ' · '.join(f'<a href="{H(u)}">{H(t)}</a>' for u,t in urls.items())
def dates(e,code=None):
 if code and e.get('dayByWeight'):return e['dayByWeight'][D['weights'][code]['olympic']]
 return e['start']+(' – '+e['end'] if e['start']!=e['end'] else '')
def rows(e,code):
 w=D['weights'][code]
 return [a for a in e['medals'] if a['weight']==w['olympic'] or ((e['id'].startswith('wc') or e['id'] in ['women26','cu26']) and a['weight'] in w['worldWeights'])]
def result(e,code):
 r=rows(e,code)
 if not r:return '<span class="tkd-muted">'+('예정 · 결과 없음' if e['start']>D['asOf'] else '결과 미확인')+'</span>'
 out=''
 for cat in dict.fromkeys(a['weight'] for a in r):
  if cat!=D['weights'][code]['olympic']:out+=f'<div class="tkd-result-weight">{H(cat)}</div>'
  out+='<ul class="tkd-result-names">'
  for a in r:
   if a['weight']!=cat:continue
   m={'Gold':'금','Silver':'은','Bronze':'동'}[a['medal']]
   out+=f'<li class="{"tkd-name-kor" if a["country"]=="KOR" else ""}"><span class="tkd-medal tkd-{a["medal"].lower()}">{m}</span><span>{athlete(a,True)}</span></li>'
  out+='</ul>'
 if e['id']=='gp26c' and code in ['w49','m58']:out+='<small class="tkd-muted">다른 입상자 결과 미확인</small>'
 return out
def weightnav():return rules.weightnav()
def render(path,title,intro,body):
 nav='<nav class="golf-nav" aria-label="태권도 탐색"><a href="./oltaekwondo.html">태권도</a><a href="./oltaekwondo.html#classes">8개 체급</a><a href="./oltaekwondo.html#rules">예선 규정</a><a href="./oltaekwondo.html#competition-routes">대회별 역할</a><a href="./oltaekwondo.html#timeline">대회 일정</a><a href="./oltaekwondo.html#tournaments">대회별·연도별</a><a href="./oltaekwondo.html#athletes">한국 선수</a></nav>'
 t=TEMPLATE
 t=re.sub(r'<title>.*?</title>',f'<title>{H(title)} | 올림픽예선</title>',t,count=1)
 t=re.sub(r'<h1 class="title">.*?</h1>',f'<h1 class="title">{H(title)}</h1>',t,count=1,flags=re.S)
 t=re.sub(r'<p class="intro">.*?</p>',f'<p class="intro">{H(intro)}</p>',t,count=1,flags=re.S)
 t=re.sub(r'<nav class="golf-nav".*?</nav>',nav,t,count=1,flags=re.S)
 t=re.sub(r'<nav class="footer-nav".*?</nav>',nav.replace('golf-nav','footer-nav'),t,count=1,flags=re.S)
 t=re.sub(r'<main id="main">.*?</main>',f'<main id="main">{body}</main>',t,count=1,flags=re.S)
 t=re.sub(r'<nav class="result-pills">.*?</nav>','',t,flags=re.S)
 t=re.sub(r'<script src="js/sports-results.js"></script>','',t)
 t=re.sub(r'<aside\b.*?</aside>','',t,flags=re.S)
 if 'taekwondo.css' not in t:t=t.replace('</head>','<link rel="stylesheet" href="./css/taekwondo.css"></head>')
 if 'taekwondo-pathways.js' not in t:t=t.replace('</head>','<script src="./js/taekwondo-pathways.js" defer></script></head>')
 t=re.sub(r'taekwondo.css(?:\?[^\"]*)?', 'taekwondo.css?v=20261012r3',t)
 t=re.sub(r'(<meta name="description" content=")[^"]*',r'\g<1>'+H(intro),t,count=1)
 t=t.replace('class="columns"','class="columns no-infobox"')
 t=re.sub(r'규정 확인 2026\.10\.04 · 한국 전망 기준 2026\.10\.04','자료 정리 2026.10.13',t)
 for old,new in REMOVED.items():t=t.replace(old,new)
 (ROOT/path).write_text(t,encoding='utf-8',newline='\n')
def tournaments():
 out='<section id="tournaments"><h2>대회별·연도별 기록</h2><div class="tkd-archive">'
 for family,title in [('gp','GP · 그랑프리'),('gs','GS · 그랜드슬램'),('wc','세계선수권'),('other','아시안게임·기타 대회')]:
  selected=[(key,t) for key,t,ids in AXES if (family in key.split('-') if family!='other' else not any(x in key.split('-') for x in ['gp','gs','wc']))]
  out+='<article><h3>'+title+'</h3><ul>'+''.join(f'<li><a href="./oltaekwondo-{key}.html"><b>{key[:4]}</b> {H(t[5:])}</a></li>' for key,t in selected)+'</ul></article>'
 return out+'</div></section>'
def timeline(code=None):
 out='<section id="timeline"><h2>대회 흐름 · 시간순</h2><p class="small">1기 성적은 초청 경로 기록, 2기 성적은 LA28 랭킹 경쟁 자료입니다. 날짜 미정인 대회는 해당 연도 계획으로 표시합니다.</p><div class="tkd-table-wrap"><table class="tkd-timeline"><thead><tr><th>일정·상태</th><th>대회·경로</th><th>'+('이 체급 결과' if code else '대상·확인 현황')+'</th></tr></thead><tbody>'
 previous=None
 for e in D['events']:
  if code and e.get('gender') and e['gender']!=code[0]:continue
  if e['cycle']!=previous:
   previous=e['cycle'];out+=f'<tr class="tkd-cycle-row"><th colspan="3">{previous}기 · '+('2024.06–2026.05 · 초청 경로 확보' if previous==1 else '2026.06–2028.05 · LA28 랭킹 경쟁')+'</th></tr>'
  key=AX[e['id']];target=f'./oltaekwondo-{key}.html#meet-{e["id"]}'+(f'-{code}' if code else '')
  final=result(e,code) if code else f'{"여자 4 올림픽체급 · 세계체급 8개" if e.get("gender")=="w" else "올림픽 8체급 · 세계체급 16개" if e["id"].startswith("wc") else "올림픽 8체급"}<br><span class="tkd-muted">'+(f'메달 기록 {len(e["medals"])}건' if e['medals'] else '공표 결과 미확인' if e['start']<=D['asOf'] else '예정')+'</span>'
  route='금 → GS · 금·은 → GP 파이널' if e['id'].startswith('gp26') or e['id'].startswith('gp27') else '금 → GS 초청' if e['id'].startswith('gpf') else '결승 → GS 초청' if e['id'].startswith('gsc') and not e['id'].startswith('gscs') else '올림픽 쿼터 · 메리트 판정' if e['id'].startswith('gscs') else '우승 → GS 초청' if e['id'].startswith('wc') else '다음 GP 초청 경로' if e['id'].startswith('gpc') else '랭킹 점수 · 직접 쿼터 없음'
  if e['id']=='cu26':final='세계체급 16개<br><span class="tkd-muted">메달 기록 64건</span>' if not code else final
  out+=f'<tr id="meet-{e["id"]}"><td><time>{H(dates(e,code))}</time><span class="tkd-state">{H(e["status"])}</span></td><th scope="row"><a href="{target}">{H(e["title"])}</a> <span class="tkd-grade">{H(e["grade"])}</span><small>{H(route)}</small></th><td>{final}</td></tr>'
 return out+'</tbody></table></div></section>'
def peoplecards(code):
 return '<section id="athletes"><h2>한국 선수 · 인물 위키</h2><div class="tkd-grid">'+''.join(f'<article class="tkd-card"><h3>{personlink(a["name"])}</h3><p>{H(a.get("name_en",""))}</p><p>{H(a.get("affiliation") or "대한민국 태권도 선수")}</p><a href="./oltaekwondo-p-{SLUGS[a["name"]]}.html">기본 정보·주요 성적 →</a></article>' for a in PEOPLE[code]['athletes'])+'</div></section>'
def competition_routes():
 rows=[
 ('GP 챌린지','GP 시리즈 참가 경로','상위 3명 → 대응 GP 초청. 국가당 체급별 1명 제한·차순위 재배정 적용.','G2 · 해당 랭킹 주기의 점수'),
 ('GP 시리즈','랭킹 + 파이널·GS 참가 경로','금·은 → GP 파이널 후보, 금 → GS 본선 초청 경로.','G6 · 금 60 / 은 36 / 동 21.6'),
 ('GP 파이널','랭킹 + GS 참가 경로','시리즈 결승 진출자·11월 랭킹으로 선발. 우승 → GS 초청 경로.','G10 · 금 100 / 은 60 / 동 36'),
 ('세계선수권','랭킹 + GS 참가 경로','세계체급 우승자 → GS의 대응 올림픽 체급 초청 경로.','G14 · 금 140 / 은 84 / 동 50.4'),
 ('GS 챌린지','GS 본선 참가 경로','결승 진출자 → 해당 연도 규정에 따른 GS 초청. 국가 중복 제한 적용.','G2 랭킹점수 · 본선 메리트와 별도'),
 ('GS 챔피언스 시리즈','별도 메리트로 올림픽 출전권 판정','2028년 1월 체급별 메리트 1위. 올림픽 랭킹과 중복 시 2위까지 재배정 가능.','메리트 · 금 1000 / 은 600 / 동 360'),
 ('아시안게임·대륙선수권·여자 오픈','올림픽 랭킹 경쟁','대회 메달을 LA28 직접 출전권이나 GP·GS 우승 초청권으로 바꾸어 계산하지 않는다.','G4 · 금 40 / 은 24 / 동 14.4'),
 ('2028 대륙 예선','올림픽 출전권 직접 선발','아시아·유럽·아프리카·팬암 체급별 상위 2명, 오세아니아 상위 1명.','랭킹·GS 확보 수에 따른 참가 제한')]
 return '<section id="competition-routes"><h2>왜 이 대회들을 확인하는가</h2><p><b>대회 성적 → 랭킹 점수 또는 다음 대회 초청 → 올림픽 출전권 판정</b>의 흐름입니다. GP와 세계선수권 우승은 높은 랭킹 점수와 GS 참가 경로를 함께 만듭니다. GS는 별도 메리트 순위, 대륙 예선은 직접 출전권을 다룹니다.</p><div class="tkd-table-wrap"><table class="tkd-route-table"><thead><tr><th>대회</th><th>예선에서의 역할</th><th>성적이 연결되는 곳</th><th>배점·판정</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<th scope="row">'+H(s)+'</th>' if i==0 else '<td>'+H(s)+'</td>' for i,s in enumerate(r))+'</tr>' for r in rows)+'</tbody></table></div><p class="small">초청 후보는 최종 WT 등록·중복 조정과 구분합니다. 세계체급과 올림픽체급의 점수 연결은 선수의 신고 체급·WT 변환 규정을 적용합니다. '+rules.link('gp')+' · '+rules.link('gs')+' · '+rules.link('rank')+'</p></section>'

def eligibility():
 return '<section id="eligibility"><h2>개최국·보편성 및 참가 자격</h2><p>전체 128명은 일반 예선 120명, 개최국 4명(남 2·여 2), 보편성 4명(남 2·여 2)으로 구성됩니다. 미국이 랭킹·GS로 확보한 수만큼 해당 성별 개최국 보장석을 조정하며, 미국은 대륙 예선에 참가하지 않습니다.</p><p>NOC는 랭킹·GS 경로로 남녀 각 최대 4명, 대륙 예선 경로로 남녀 각 최대 2명까지 확보할 수 있습니다. 체급당 출전 선수는 1명입니다.</p><p>기존 참가 자격 안내: 2011.12.31 또는 그 이전 출생, 국기원 단증·WT 글로벌 선수 라이선스, 올림픽 헌장·반도핑 조건을 충족해야 합니다. 경로별 추가 성적 요건과 개최국·보편성 신청 조건은 IOC 예선 문서 C·D조를 함께 확인합니다.</p><p class="small">'+rules.link('ioc')+'</p></section>'

def ruleblocks(compact=True):
 content=rules.quota().replace('id="rules"','id="quota"')+competition_routes()+rules.cycles()+rules.entry()+rules.points()+rules.grand_slam()+eligibility()
 if compact:content='<p>랭킹 5명·GS 메리트 1명·대륙 예선 9명 경로를 확인합니다. <a href="./oltaekwondo.html#rules">전체 예선 규정과 대회별 역할 →</a></p><details class="tkd-meet"><summary>체급에 적용되는 예선 규정 전체</summary>'+content+'</details>'
 return '<section id="rules"><h2>LA28 예선 규정</h2>'+content+'</section>'

def event_context(e):
 eid=e['id']
 if eid.startswith('gpc'):text='GP 챌린지는 다음 GP 시리즈에 들어가기 위한 대회입니다. 상위 3명 초청 경로에 국가당 체급별 1명 제한·중복 재배정을 적용합니다.'
 elif eid.startswith('gpf'):text='GP 파이널은 G10 랭킹점수 대회입니다. 우승은 GS 본선 초청 경로에도 연결되며, 특히 2027 파이널은 2028년 1월 올림픽 랭킹 판정에 앞선 핵심 대회입니다.'
 elif eid.startswith('gp'):text='GP 시리즈는 G6 랭킹점수 대회입니다. 금·은메달은 GP 파이널 진출 경로, 금메달은 GS 본선 초청 경로에도 연결됩니다. 이 대회 메달만으로 올림픽 출전권이 확정되지는 않습니다.'
 elif eid.startswith('gscs'):text='GS 본선은 일반 올림픽 랭킹과 별도로 메리트 점수를 쌓는 대회입니다. 2028년 1월 체급별 메리트 순위로 올림픽 출전권을 판정하므로, 초청권 확보 뒤 본선 성적·감점·랭킹 중복을 함께 확인합니다.'
 elif eid.startswith('gsc'):text='GS 챌린지는 GS 본선 참가 경로입니다. 결승 진출자의 초청에는 연도별 규정과 국가 중복 조정이 적용됩니다. 챌린지 G2 랭킹점수를 GS 본선 메리트에 합산하지 않습니다.'
 elif eid.startswith('wc'):text='세계선수권은 G14 랭킹점수 대회이며, 세계체급 우승자는 해당 올림픽 체급의 GS 본선 초청 경로에도 연결됩니다. 랭킹점수 변환과 GS의 체급 통합은 각각의 규정을 적용합니다.'
 else:text='G4 성적을 통한 올림픽 랭킹 경쟁 자료입니다. 직접 올림픽 출전권을 주는 2028 대륙 예선과 구분하며, 이 대회 우승을 GP·세계선수권의 GS 초청 경로로 대체하지 않습니다.'
 cycle='1기 성적은 2026년 7월 랭킹에서 초기화되지만, 성적으로 확보한 다음 대회 초청 경로는 별도로 확인합니다.' if e['cycle']==1 else '2기 성적은 2026년 6월부터 적립하며, 일반 올림픽 랭킹 또는 GS 메리트의 각 배점·감점 규정을 적용합니다.'
 return '<div class="tkd-callout"><b>이 대회와 LA28 예선의 관계</b><p>'+text+'</p><p>'+cycle+'</p><a href="./oltaekwondo.html#competition-routes">대회별 역할·전체 예선 규정 →</a></div>'
def eventpage(key,title,ids):
 body=weightnav()+'<nav class="tkd-axis-links" aria-label="대회 목록">'+''.join(f'<a href="#meet-{i}">{H(E[i]["title"])}</a>' for i in ids)+'</nav>'
 for eid in ids:
  e=E[eid];body+=f'<section id="meet-{eid}" class="tkd-tournament"><h2>{H(e["title"])}</h2><p><time>{H(dates(e))}</time> <span class="tkd-grade">{H(e["grade"])}</span> · {H(e["status"])}</p><p>{H(e["route"])}</p>'+event_context(e)
  if e.get('resultNote'):body+=f'<p class="tkd-callout">{H(e["resultNote"])}</p>'
  if eid=='ag26':body+='<p>겨루기 10.02–10.03 · 품새 10.01 · 버추얼 10.02 · 도요하시 종합체육관. 한국 겨루기 금 1·동 4. 태권도 전체(품새 포함)는 금 3·동 4.</p>'
  body+='<div class="tkd-grid">'
  for c,w in D['weights'].items():
   if e.get('gender') and e['gender']!=c[0]:continue
   body+=f'<article id="meet-{eid}-{c}" class="tkd-card"><span id="weight-{c}-{eid}"></span><h3><a href="./oltaekwondo-ev-{c}.html#meet-{eid}">{H(w["label"])}</a></h3>'+result(e,c)
   names=e.get('participants',{}).get(w['olympic'],[])
   if names:body+=f'<details><summary>참가 선수 {len(names)}명</summary>'+rules.recipient_names(names)+'</details>'
   body+='</article>'
  body+='</div><p class="small">'+refs(e)+'</p></section>'
 if key=='2028-continental':body+='<section id="continental"><h2>2028 대륙 예선</h2><p>2028년 2–4월 예정 · 세부 개최지·날짜 미확인. 아시아·유럽·아프리카·팬아메리카는 체급별 상위 2명, 오세아니아는 체급별 상위 1명 경로입니다.</p>'+rules.quota().replace('id="rules"','id="quota"')+'</section>'
 for c,w in D['weights'].items():body+=f'<p id="weight-{c}"><a href="./oltaekwondo-ev-{c}.html">{H(w["label"])} 전체 시간순 기록 →</a></p>'
 render(f'oltaekwondo-{key}.html','태권도 · '+title,'연도별 대회 기록 · 일정·체급별 입상자·참가 명단 · 2026.10.13 기준',body)
def personpage(code,a):
 name=a['name'];body=f'<p class="tkd-breadcrumb"><a href="./oltaekwondo.html">태권도</a> / <a href="./oltaekwondo-ev-{code}.html">{H(D["weights"][code]["label"])}</a> / {H(name)}</p><section id="profile"><h2>기본 정보</h2><dl class="tkd-facts"><dt>이름</dt><dd>{H(name)} · {H(a.get("name_en",""))}</dd><dt>국적·종목</dt><dd>대한민국 · 태권도 겨루기</dd><dt>연결 체급</dt><dd><a href="./oltaekwondo-ev-{code}.html">{H(D["weights"][code]["label"])}</a></dd>'
 if a.get('birth'):body+='<dt>생년월일</dt><dd>'+H(a['birth'])+'</dd>'
 if a.get('affiliation'):body+='<dt>소속</dt><dd>'+H(a['affiliation'])+' <small>(기존 자료 기준 2026.10.05 · 소속 변경 가능)</small></dd>'
 body+='</dl><p>올림픽 체급별 주요 한국 선수 참고 문서입니다. LA28 대표 선발·출전 확정 명단은 별도입니다.</p></section><section id="results"><h2>최근 대회 기록</h2><table class="tkd-recipients"><thead><tr><th>대회·일정</th><th>체급·성적</th></tr></thead><tbody>'
 refsmap={s['url']:s['title'] for s in a.get('sources',[])}
 for e in sorted(D['events'],key=lambda e:e['start'],reverse=True):
  matches=[x for x in e['medals'] if rules.KO.get(x['name'],x['name'])==name and x['country']=='KOR']
  for x in matches:
   resultcode=next((c for c,w in D['weights'].items() if x['weight']==w['olympic']),code)
   body+=f'<tr><th><a href="./oltaekwondo-{AX[e["id"]]}.html#meet-{e["id"]}-{resultcode}">{H(e["title"])}</a><span class="tkd-date">{H(dates(e,resultcode))}</span></th><td>{H(x["weight"])} · <b>'+{'Gold':'금메달','Silver':'은메달','Bronze':'동메달'}[x['medal']]+'</b></td></tr>'
   for s in e['sources']:refsmap[D['sources'][s]['url']]=D['sources'][s]['title']
   if e.get('resultUrl'):refsmap[e['resultUrl']]=e['title']+' 결과'
 body+='</tbody></table></section>'
 if a.get('results'):
  body+='<section id="history"><h2>기존 주요 성적</h2><ul>'+''.join(f'<li>{H(r["year"])} · {H(r["comp"])} · {H(r["event"])} · <b>{H(r["result"])}</b></li>' for r in a['results'])+'</ul><p class="small">기존 선수 자료(2026.10.05)에서 보존한 기록. 최근 GP·아시안게임 기록은 위 표를 함께 확인합니다.</p></section>'
 body+='<section id="sources"><h2>자료 출처</h2><ul>'+''.join(f'<li><a href="{H(u)}">{H(t)}</a></li>' for u,t in refsmap.items())+'</ul></section>'+peoplecards(code).replace('id="athletes"','id="related"')
 render(f'oltaekwondo-p-{SLUGS[name]}.html',name+' (태권도)','대한민국 태권도 선수 · '+D['weights'][code]['label']+' · 기본 정보와 주요 대회 성적',body)
def update_pages():
 for c,w in D['weights'].items():
  body=weightnav()+peoplecards(c)+'<div class="tkd-callout"><b>이 체급의 예선 흐름</b><p>GP·세계선수권 성적은 올림픽 랭킹 점수와 GP 파이널·GS 초청 경로를 만듭니다. GS 본선은 별도 메리트, 2028 대륙 예선은 직접 출전권을 다룹니다. 아래 기록의 초청 경로와 올림픽 출전권 판정을 구분해서 확인합니다.</p><a href="./oltaekwondo.html#rules">예선 규정·대회별 역할 전체 →</a></div>'+timeline(c)+rules.recipients(c)+ruleblocks()+tournaments()
  render(f'oltaekwondo-ev-{c}.html','태권도 · '+w['label'],'1기 → 2기 · 시간순 대회 결과와 GP·GS 초청 경로 · 2026.10.13 기준',body)
 for key,title,ids in AXES:eventpage(key,title,ids)
 for code,p in PEOPLE.items():
  for a in p['athletes']:personpage(code,a)
 body='<section id="classes"><h2>8개 올림픽 체급</h2><p>남자 4체급 · 여자 4체급 · 체급별 대회 흐름과 한국 선수</p>'+weightnav()+'</section>'+ruleblocks(False)+timeline()+'<section id="athletes"><h2>한국 선수 · 체급별 인물 위키</h2><div class="tkd-table-wrap"><table class="tkd-timeline"><thead><tr><th>체급</th><th>선수 위키</th></tr></thead><tbody>'+''.join(f'<tr><th><a href="./oltaekwondo-ev-{c}.html">{H(w["label"])}</a></th><td>'+ ' · '.join(personlink(a['name']) for a in PEOPLE[c]['athletes'])+'</td></tr>' for c,w in D['weights'].items())+'</tbody></table></div></section>'+rules.sources()+tournaments()
 render('oltaekwondo.html','태권도 (Taekwondo)','LA28 · 남녀 8체급 · 시간순 대회 결과·초청 경로·한국 선수 위키 · 2026.10.13 기준',body)
 for old in REMOVED:
  p=ROOT/old
  if p.exists():p.unlink()
 for p in ROOT.glob('*.html'):
  if p.name.startswith('oltaekwondo'):continue
  t=p.read_text(encoding='utf-8');original=t
  for old,new in REMOVED.items():
   t=re.sub(r'(?<=/)' +re.escape(old)+r'(?:#[^"\s<>]*)?',new,t)
  if t!=original:p.write_text(t,encoding='utf-8',newline='\n')
 print('Rendered 8 weights, 12 annual tournament pages, '+str(sum(len(p['athletes']) for p in PEOPLE.values()))+' athlete wikis and main hub')
if __name__=='__main__':update_pages()
