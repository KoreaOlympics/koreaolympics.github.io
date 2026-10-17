"""Shooting event × competition views. Run after shooting_pages.py."""
import hashlib,html,json,re
from pathlib import Path
import shooting_pages as S
ROOT=Path(__file__).resolve().parents[2]
E=S.E
AXES=[('2025-world','2025 세계선수권',False),('2025-wc','2025 월드컵',False),('2025-final','2025 파이널',False),('2026-wc','2026 월드컵',False),('2026-world','2026 도하 세선',True),('2026-28-continental','2026–28 대륙 경로',True),('2027-world','2027 세계선수권',True),('2027-wc','2027 월드컵',True),('2028-quota','2028 출전권 결산',True)]
DESCRIPTIONS={
'2025-world':'카이로 소총·권총 및 아테네 산탄총 세계선수권. 2025 성적은 LA28 쿼터 획득 성적이 아닙니다.',
'2025-wc':'부에노스아이레스·리마·니코시아·뮌헨·로나토·닝보 월드컵의 한국 성적을 종목별로 모았습니다.',
'2025-final':'도하 월드컵 파이널의 최종 출전 성적과 파이널 참가 경로를 구분합니다. 파이널 참가권은 올림픽 출전권과 별개입니다.',
'2026-wc':'2026 월드컵 성적을 추가할 문서입니다. 현재 수록한 성적 표본은 2025 시즌이며 2026 결과는 미입력입니다.',
'2026-world':'2026년 11월 1–14일 도하 세계선수권은 첫 LA28 쿼터 대회입니다. 12개 개인종목에 각각 3장이 배정되며, 국가별·기존 획득자 제한에 따라 차순위로 넘어갈 수 있습니다.',
'2026-28-continental':'대륙선수권·대륙경기 등 공식 지정 대회의 배정을 확인하는 문서입니다. 실제 획득자는 ISSF 공식 배정 확인 후 기록합니다.',
'2027-world':'대구 소총·권총 및 카이로 산탄총 세계선수권의 결과와 LA28 배정을 모을 문서입니다. 현재 결과는 미입력입니다.',
'2027-wc':'2027 월드컵의 개인종목 우승자 또는 적격 차순위 선수에 의한 NOC 쿼터 경로입니다. 우승과 쿼터 획득을 별도로 기록합니다.',
'2028-quota':'공식 대회별 NOC 쿼터와 2028년 5월 1일 올림픽 랭킹 경로를 결산합니다. 국가 쿼터 획득자가 최종 올림픽 대표로 자동 확정되는 것은 아닙니다.'}
def h(x):return html.escape(str(x),quote=True)
def a(url,label):return '<a href="'+h(url)+'">'+h(label)+'</a>'
def page(key):return 'olshooting-'+key+'.html'
def scroll(t):return '<div class="shoot-axis-scroll" tabindex="0" role="region" aria-label="좌우로 넘기는 표">'+t+'</div>'
def group(r):return '2025-'+S.comp(r)['type']
def selected(event,key=None):
 rows=[r for r in S.kor(event) if key is None or group(r)==key]
 best={}
 for r in rows:
  identity=(r['competition'],tuple(r['members']) if r['members'] else r['name'])
  if identity not in best or r['stage']!='Q':best[identity]=r
 return sorted(best.values(),key=lambda r:(S.comp(r)['start'],r['rank'],r['name']))
def result_table(event,key=None):
 rows=''
 for i,r in enumerate(selected(event,key)):
  label=S.comp(r)['name']; stage='결선' if r['stage']!='Q' else '본선'
  outcome={1:'금',2:'은',3:'동'}.get(r['rank']) if S.medal(r) else stage+' '+str(r['rank'])+'위'
  if r['rpo']:outcome+=' · 순위 외'
  rows+='<tr'+(' class="qualified"' if S.medal(r) else '')+' data-record="'+h(str(r['competition'])+'-'+r['name']+'-'+r['stage'])+'"><th scope="row">'+a(page(group(r))+'#event-'+E[event]['code'],label)+'</th><td>'+a(r['url'],S.names(r)+' · '+outcome)+'</td></tr>'
 if not rows:rows='<tr><td colspan="2">— · 결과 미입력</td></tr>'
 return scroll('<table class="shoot-axis-results"><caption>한국 결과 · 대회 통합 표</caption><thead><tr><th scope="col">대회</th><th scope="col">선수·팀 · 결과</th></tr></thead><tbody>'+rows+'</tbody></table>')
def recipients(event,key=None):
 data=json.loads((ROOT/'data/shooting-pathways.json').read_text(encoding='utf-8'))
 rows=''
 for r in data['recipients']:
  if r['event']!=event or (key and key!='2028-quota' and r['axis']!=key):continue
  rows+='<tr class="qualified"><th scope="row">'+a(r['source'],r['competition']+' → '+r['target'])+'</th><td>'+h(r['athlete'])+'</td></tr>'
 if not rows:rows='<tr><td colspan="2">— · 확인된 명단 미입력</td></tr>'
 note='혼성은 해당 개인종목 출전자격을 갖춘 남녀의 조합이며, 별도의 혼성 쿼터를 배정하지 않습니다.' if event.endswith('MT') else '파이널 참가권과 LA28 NOC 쿼터를 구분합니다. 노란색은 확인된 참가 경로 명단입니다.'
 return scroll('<table class="shoot-axis-results"><caption>참가권·쿼터 경로 명단</caption><thead><tr><th scope="col">대회 → 다음 경로</th><th scope="col">선수·팀</th></tr></thead><tbody>'+rows+'</tbody></table>')+'<p class="small">'+note+'</p>'
AXIS_NOTES={'2026-world':'첫 쿼터 · 총 36장','2026-28-continental':'ISSF 지정 대회','2027-world':'대구·카이로 · 총 36장','2027-wc':'지정 월드컵 · 총 48장','2028-quota':'랭킹·최종 배정','2025-world':'예선 기간 이전','2025-wc':'예선 기간 이전','2025-final':'파이널 참가·성적','2026-wc':'직접 쿼터 없음 · MQS 참고'}
GROUPS=[('소총',['ARM','ARW','R3PM','R3PW','ARMT']),('권총',['APM','APW','RFPM','SPW','APMT']),('산탄총',['TRM','TRW','SKM','SKW','TRMT'])]
def matrix(qualifying):
 axes=[axis for axis in AXES if axis[2]==qualifying];ident='shooting-qualifying' if qualifying else 'shooting-reference'
 title='올림픽 예선 · 출전권 경로' if qualifying else '비예선 대회 · 성적·MQS 참고'
 caption='12개 개인종목 쿼터 · 혼성 3종목은 개인 출전자격으로 구성' if qualifying else '직접 출전권 배정 없음 · 2026 월드컵의 MQS 인정 여부는 기간·지정 조건 확인'
 out='<section id="'+ident+'" class="shoot-matrix-section"><h3>'+title+'</h3><p class="small">'+caption+'</p>'
 heads='<th scope="col">세부종목</th>'+''.join('<th scope="col">'+a(page(k),n)+'<small>'+h(AXIS_NOTES[k])+'</small></th>' for k,n,_ in axes)
 rows=''
 for group,events in GROUPS:
  rows+='<tr class="shoot-matrix-group"><th colspan="'+str(len(axes)+1)+'" scope="colgroup">'+group+' <span>개인 4 · 혼성 1</span></th></tr>'
  for event in events:
   v=E[event];mixed=event.endswith('MT')
   rows+='<tr><th scope="row">'+a('olshooting-ev-'+v['code']+'.html',v['label'])+'</th>'+''.join('<td>'+a(page(k)+'#event-'+v['code'],'팀 구성' if mixed and qualifying else '명단' if k=='2028-quota' else '결과·쿼터' if qualifying else '결과')+'</td>' for k,_,_ in axes)+'</tr>'
 return out+scroll('<table class="shoot-axis-matrix '+('shoot-qualifying' if qualifying else 'shoot-reference')+'"><thead><tr>'+heads+'</tr></thead><tbody>'+rows+'</tbody></table>')+'</section>'
def index():
 return '<section id="shooting-index" class="shoot-axis-index"><h2>15종목 × 연도·대회</h2><p>소총·권총·산탄총 각 5종목. 출전권 경로를 위에, 직접 쿼터가 없는 참고 대회를 아래에 배치했습니다. 종목명은 전체 성적·선수 정보, 교차 칸은 해당 대회의 종목 기록으로 연결됩니다.</p><nav class="shoot-axis-links" aria-label="예선·비예선 표"><a href="#shooting-qualifying">예선·출전권</a><a href="#shooting-reference">비예선·참고 성적</a><a href="olshooting.html#pathway">예선 규정</a></nav>'+matrix(True)+matrix(False)+'<p class="small">혼성팀은 해당 개인종목 자격을 확보한 남녀로 구성하며 별도 혼성 쿼터는 없습니다. 비예선 표의 메달·파이널 참가권을 올림픽 출전권으로 계산하지 않습니다. 모바일에서는 각 표를 좌우로 넘깁니다.</p></section>'
def css(t):
 t=re.sub(r'<link rel="stylesheet" href="\./css/shooting-orthogonal.css[^\"]*">','',t)
 version=hashlib.sha256((ROOT/'css/shooting-orthogonal.css').read_bytes()).hexdigest()[:12]
 return t.replace('</head>','<link rel="stylesheet" href="./css/shooting-orthogonal.css?v='+version+'"></head>')
def put(p,t):p.write_text(t,encoding='utf-8',newline='\n')
def render():
 for file in ['olshooting.html','olshooting-events.html','olshooting-projection.html']:
  p=ROOT/file;t=p.read_text(encoding='utf-8')
  t=re.sub(r'<!-- shooting-orthogonal:start -->.*?<!-- shooting-orthogonal:end -->','',t,flags=re.S)
  block='<!-- shooting-orthogonal:start -->'+index()+'<!-- shooting-orthogonal:end -->'
  # Preserve the main's opening explanation and overview before its navigation matrix.
  m=re.search(r'<section id="(?:overview|baseline)">.*?</section>',t,flags=re.S)
  if m:t=t[:m.end()]+block+t[m.end():]
  else:t=t.replace('<main id="main">','<main id="main">'+block,1)
  put(p,css(t))
 for event,v in E.items():
  p=ROOT/('olshooting-ev-'+v['code']+'.html');t=p.read_text(encoding='utf-8')
  block='<section id="season2025"><h2>대회 결과 · 통합</h2><p>'+a('olshooting.html#shooting-index','세부종목 × 대회 전체 목차')+' · 노란 성적은 메달이며 올림픽 쿼터 표시가 아닙니다.</p>'+result_table(event)+recipients(event)+S.rival_section(event)+'</section>'
  if '<section id="season2025">' in t:
   t=re.sub(r'<section id="season2025">.*?</section>',lambda m:block,t,count=1,flags=re.S)
  else:
   t=re.sub(r'(<main[^>]*>)',lambda m:m[1]+block,t,count=1)
  put(p,css(t))
 template=(ROOT/'olshooting-projection.html').read_text(encoding='utf-8')
 for key,title,q in AXES:
  contents='<p>'+h(DESCRIPTIONS[key])+'</p><nav class="shoot-axis-links" aria-label="이 대회의 종목">'+''.join(a('#event-'+v['code'],v['label']) for v in E.values())+'</nav><p class="note">성적 표본은 2025 성인 시즌입니다. 미래 결과를 예측값으로 채우지 않았습니다. 미입력은 미출전·무메달을 뜻하지 않습니다.</p>'
  for event,v in E.items():
   contents+='<section id="event-'+v['code']+'"><h2>'+a('olshooting-ev-'+v['code']+'.html#season2025',v['label'])+'</h2>'+result_table(event,key)+recipients(event,key)+'</section>'
  contents+='<section id="sources"><h2>공식 근거</h2><p>'+a('https://www.issf-sports.org/news/4880','ISSF · LA28 예선 경로')+' · '+a('https://www.issf-sports.org/news/5085','ISSF · 도하 첫 쿼터')+' · '+a('https://www.issf-sports.org/news/4844','ISSF · 2025 파이널 참가 경로')+'</p><p>2025 개별 성적 근거는 결과 링크에서 확인합니다. 확인일 2026.10.11.</p></section>'
  t=re.sub(r'<title>.*?</title>','<title>사격 · '+h(title)+'</title>',template)
  t=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="사격 '+h(title)+' 종목별 결과·참가 경로">',t)
  t=re.sub(r'<h1 class="title">.*?</h1>','<h1 class="title">사격 · '+h(title)+'</h1>',t)
  t=re.sub(r'<p class="intro">.*?</p>','<p class="intro">'+a('olshooting.html#shooting-index','← 세부종목 × 연도·대회 목차')+'</p>',t)
  t=re.sub(r'<main id="main">.*?</main>',lambda m:'<main id="main">'+contents+'</main>',t,flags=re.S)
  t=t.replace(' aria-current="page"','')
  put(ROOT/page(key),css(t))
if __name__=='__main__':render()
