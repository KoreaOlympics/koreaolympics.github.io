"""Build boxing's weight × competition views from one source. Run after athletes.py."""
import hashlib, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = [(f'm{x}', f'남자 {x}kg') for x in (55,60,65,70,80,90)] + [('mo90','남자 +90kg')] + [(f'w{x}',f'여자 {x}kg') for x in (51,54,57,60,65,70,75)]
RULE = 'https://worldboxing.org/ioc-approves-olympic-qualification-system-for-boxing-competition-at-la28/'
DOCS = 'https://worldboxing.org/competitions/general-competition-documents/'
AXES = [
 ('2025-wc','2025 세계선수권',False,'리버풀 · World Boxing 세계선수권. LA28 직접 예선이 아닌 참고 성적입니다.'),
 ('2025-cup','2025 월드복싱컵',False,'월드복싱컵 시리즈·파이널의 체급별 참고 성적입니다.'),
 ('2026-cup','2026 월드복싱컵',False,'월드복싱컵 시리즈·파이널의 체급별 참고 성적입니다.'),
 ('2026-asia','2026 아시아선수권',False,'아시아선수권 참고 성적입니다. 2027–28 아시아 올림픽 예선과 별개입니다.'),
 ('2026-ag','2026 아시안게임',False,'아시안게임 참고 성적입니다. LA28 출전권 획득 명단과 구분합니다.'),
 ('2027-wc','2027 세계선수권',True,'LA28 첫 올림픽 예선 · 카자흐스탄. 출전권 획득자는 결과 발표와 공식 배정 확인 후 기록합니다.'),
 ('2027-28-continental','2027–28 대륙 예선',True,'아시아·유럽·아프리카·팬암·오세아니아 예선. 한국의 경로는 아시아 예선이며, 체급별 배정 규정은 체급 문서에 있습니다.'),
 ('2028-wqt1','2028 세계 예선 1',True,'앞선 경로에서 출전권을 확보하지 못한 체급의 세계 예선입니다.'),
 ('2028-wqt2','2028 세계 예선 2',True,'마지막 세계 예선입니다. 개최국 배정 등에 따른 최종 자리는 공식 공지를 따릅니다.'),
 ('2028-quota','2028 출전권 결산',True,'예선별 획득 선수와 최종 출전권을 한 표로 모읍니다. 현재 확정 명단은 입력하지 않았습니다.')]

def e(value): return html.escape(str(value), quote=True)
def page(key): return f'olboxing-{key}.html'
def link(url,label): return f'<a href="{e(url)}">{e(label)}</a>'
def scroll(table): return '<div class="box-scroll" tabindex="0" role="region" aria-label="좌우로 넘기는 표">'+table+'</div>'
def load_data(): return json.loads((ROOT/'data/boxing-pathways.json').read_text(encoding='utf-8'))
NOC={'Kazakhstan':'KAZ','Uzbekistan':'UZB','Brazil':'BRA','India':'IND','England':'ENG','Poland':'POL','China':'CHN','Chinese Taipei':'TPE','South Korea':'KOR','Japan':'JPN','United States':'USA','Australia':'AUS','Ireland':'IRL','Turkey':'TUR','Türkiye':'TUR','France':'FRA','Spain':'ESP','Cuba':'CUB','Mongolia':'MGL','Georgia':'GEO','Bulgaria':'BUL','Italy':'ITA','Hungary':'HUN','Croatia':'CRO','Austria':'AUT','Ukraine':'UKR','Azerbaijan':'AZE','Colombia':'COL','Venezuela':'VEN','Jordan':'JOR','Canada':'CAN','Norway':'NOR','Finland':'FIN','Germany':'GER','Argentina':'ARG','Kyrgyzstan':'KGZ','Guatemala':'GUA','Dominican Republic':'DOM','Philippines':'PHI','Nigeria':'NGR'}
def display_name(r):
 name=r['athlete'];country=r.get('country','');parts=name.split()
 if r.get('family_name') and country!='South Korea':short=r['family_name'].title()
 elif name in ('Xuan Yi Guo','Taguchi Ayaka'):short={'Xuan Yi Guo':'Guo','Taguchi Ayaka':'Taguchi'}[name]
 elif country=='South Korea' or len(parts)==1: short=name
 elif country in ('China','Chinese Taipei'):short=parts[0]
 else:short=parts[-1]
 noc=r.get('noc') or NOC.get(country,country)
 return short+(' ('+noc+')' if noc else '')
def results(data,code,key=None):
 rows=[r for r in data['results'] if r['weight']==code and (key is None or r['axis']==key)]
 body=''
 for r in rows:
  name=display_name(r)
  if sum(display_name(x)==name and x['competition']==r['competition'] for x in rows)>1:
   name=r['athlete'].split()[0][:1]+'. '+name
  full=r['athlete']+(' · '+r['country'] if r.get('country') else '')
  athlete='<a href="'+e(r['source'])+'" title="'+e(full)+'" aria-label="'+e(full+' · '+r['result'])+'">'+e(name+' · '+r['result'])+'</a>'
  body+=f'<tr id="meet-{e(r["id"])}"'+(' class="box-gold"' if r['result']=='금' else '')+f'><th scope="row">{link(page(r["axis"])+"#weight-"+code,r["competition"])}</th><td>{athlete}</td></tr>'
 if not body:
  absent=key=='2026-ag' and code not in data.get('competitions',{}).get('2026-ag',{}).get('weights',[code])
  body='<tr><td colspan="2">'+('이번 아시안게임 미개최 체급' if absent else '— · 결과 미입력')+'</td></tr>'
 return scroll('<table class="box-results"><caption>대회 결과 · 국제 입상자와 한국 성적</caption><thead><tr><th scope="col">대회</th><th scope="col">선수 · 결과</th></tr></thead><tbody>'+body+'</tbody></table>')
def qualified(data,code,key=None):
 rows=[r for r in data['qualifiers'] if r['weight']==code and (key is None or key=='2028-quota' or r['axis']==key)]
 body=''.join('<tr class="qualified"><th scope="row">'+link(page(r['axis'])+'#weight-'+code,r['competition'])+'</th><td>'+link(r['source'],r['athlete'])+'</td></tr>' for r in rows)
 if not body: body='<tr><td colspan="2">— · 확인된 출전권 획득자 없음</td></tr>'
 return scroll('<table class="box-results"><caption>LA28 출전권 획득 명단</caption><thead><tr><th scope="col">예선 대회</th><th scope="col">선수</th></tr></thead><tbody>'+body+'</tbody></table>')
def index():
 weights=''.join(link('olboxing-ev-'+c+'.html',n) for c,n in WEIGHTS)
 axes=''.join(link(page(k),n) for k,n,_,_ in AXES)
 heads='<th scope="col">체급</th>'+''.join('<th scope="col">'+link(page(k),n)+'</th>' for k,n,_,_ in AXES)
 rows=''.join('<tr><th scope="row">'+link('olboxing-ev-'+c+'.html',n)+'</th>'+''.join('<td'+(' class="qualifier"' if q else '')+'>'+link(page(k)+'#weight-'+c,'명단' if k=='2028-quota' else '결과·명단' if q else '결과')+'</td>' for k,_,q,_ in AXES)+'</tr>' for c,n in WEIGHTS)
 return '<section class="box-index" id="boxing-index"><h2>체급 × 연도·대회</h2><p>체급 문서는 그 체급의 대회 결과를, 대회 문서는 14체급의 결과를 모읍니다. 노란 칸은 올림픽 예선·출전권 결산 문서입니다. 모바일에서는 표를 좌우로 넘깁니다.</p><p>2025 세선 입상자 80명과 월드컵 1·2차 및 파이널 입상 기록 199건을 수록했습니다. LA28 밖 체급은 해당 대회 문서 하단에 따로 보존합니다. 파이널의 일부 동메달 선수명은 원문 미기재입니다.</p><h3>체급 문서</h3><nav class="box-links" aria-label="14체급">'+weights+'</nav><h3>연도·대회 문서</h3><nav class="box-links" aria-label="연도별 대회">'+axes+'</nav>'+scroll('<table class="box-matrix"><thead><tr>'+heads+'</tr></thead><tbody>'+rows+'</tbody></table>')+'</section>'
def insert(text,block):
 text=re.sub(r'<!-- boxing-orthogonal:start -->.*?<!-- boxing-orthogonal:end -->','',text,flags=re.S)
 wrapped='<!-- boxing-orthogonal:start -->'+block+'<!-- boxing-orthogonal:end -->'
 if block.startswith('<section class="box-index"') and '<section id="overview">' in text:
  return re.sub(r'(<section id="overview">.*?</section>)',lambda m:m.group(1)+wrapped,text,count=1,flags=re.S)
 return text.replace('<main id="main">','<main id="main">'+wrapped,1)
def css(text):
 text=re.sub(r'<link rel="stylesheet" href="\./css/boxing.css[^\"]*">','',text)
 version=hashlib.sha256((ROOT/'css/boxing.css').read_bytes()).hexdigest()[:12]
 return text.replace('</head>',f'<link rel="stylesheet" href="./css/boxing.css?v={version}"></head>')
def write(path,text): path.write_text(text,encoding='utf-8',newline='\n')
def render():
 data=load_data()
 # The main uses the consolidated two-table navigation; removed guide tabs stay removed.
 mainpath=ROOT/'olboxing.html';maintext=mainpath.read_text(encoding='utf-8')
 maintext=re.sub(r'<p id="ag2026-status".*?</p>','',maintext,flags=re.S)
 summary='<p id="ag2026-status" class="wiki-caption">'+link(page('2026-ag'),'2026 아시안게임 · 완료 · 11체급 44명 입상')+' · 한국 장동환·김민성 은메달 · LA28 직접 예선과 구분</p>'
 if data.get('competitions',{}).get('2026-ag'):maintext=maintext.replace('<h3>올림픽 예선과 직접 무관한 대회</h3>','<h3>올림픽 예선과 직접 무관한 대회</h3>'+summary,1)
 write(mainpath,maintext)
 for c,n in WEIGHTS:
  p=ROOT/f'olboxing-ev-{c}.html'
  block='<section class="box-section" id="competition-results"><h2>'+e(n)+' · 대회 결과와 출전권</h2><p>'+link('olboxing.html#boxing-index','체급 × 대회 전체 목차')+' · 성적과 출전권 배정을 별도로 기록합니다.</p>'+results(data,c)+qualified(data,c)+'</section>'
  write(p,css(insert(p.read_text(encoding='utf-8'),block)))
 template=(ROOT/'olboxing.html').read_text(encoding='utf-8')
 template=re.sub(r'href="#(qualifying|reference)"',r'href="olboxing.html#\1"',template)
 for k,n,q,description in AXES:
  sections=''.join('<section class="box-section" id="weight-'+c+'"><h2>'+link('olboxing-ev-'+c+'.html#competition-results',label)+'</h2>'+results(data,c,k)+(qualified(data,c,k) if q else '')+'<p class="box-source">'+link('olboxing-ev-'+c+'.html#rules','체급별 배정 규정')+'</p></section>' for c,label in WEIGHTS)
  extras=sorted({r['weight'] for r in data['results'] if r['axis']==k}-{c for c,_ in WEIGHTS})
  if extras:
   sections+='<section id="other-weights"><h2>LA28 밖 원문 체급</h2><p>다음 성적은 해당 대회의 원문 체급에만 보존합니다.</p></section>'
   for c in extras:sections+='<section id="weight-'+c+'"><h3>'+e(('남자 ' if c.startswith('m') else '여자 ')+c[1:].replace('o','+')+'kg')+'</h3>'+results(data,c,k)+'</section>'
  source_extra=''
  meet_info=''
  if k=='2026-ag' and k in data.get('competitions',{}):
   info=data['competitions'][k]
   meet_info='<section id="meeting"><h2>대회 정보</h2><p>'+e(info['start']+'–'+info['end']+' · '+info['venue']+' · '+info['status'])+'</p><p><b>11체급 · 입상자 44명 · 한국 '+e(info['koreanSummary'])+'</b></p><p>남자 55·60·70·80·90·+90kg, 여자 51·54·60·65·75kg. LA28의 남자 65kg·여자 57kg·70kg은 이번 대회에서 열리지 않았습니다.</p><p>2026 아시안게임은 LA28 직접 예선이 아닙니다. 2027–28 대륙 예선과 구분해 국제 경쟁력 참고 성적으로 확인합니다.</p></section>'
   source_extra='<p>'+link(info['source'],'AINAGOC · 공식 메달리스트')+' · '+link(info['scheduleSource'],'AINAGOC · 체급별 일정')+'</p>'
  if k in ('2025-wc','2025-cup'):
   title='2025_World_Boxing_Championships' if k=='2025-wc' else '2025_World_Boxing_Cup'
   source_extra='<p>'+link('https://en.wikipedia.org/wiki/'+title,'Wikipedia · '+title.replace('_',' '))+' · 입상 표 파싱, 2026.10.11. 선수 성을 축약 표시하며 전체 이름은 링크 설명에 보존합니다.</p>'
  content='<p>'+e(description)+'</p>'+meet_info+'<nav class="box-links" aria-label="이 대회의 체급">'+''.join(link('#weight-'+c,label) for c,label in WEIGHTS)+'</nav><p class="note">2025 세선·월드컵은 기존 입상 표, 2026 아시안게임은 AINAGOC 공식 메달표를 사용합니다. 금메달 음영은 올림픽 출전권을 뜻하지 않습니다. 체급이 다른 성적은 자동 환산하지 않습니다.</p>'+sections+'<section id="sources"><h2>근거·수록 범위</h2>'+source_extra+'<p>'+link(RULE,'World Boxing · LA28 예선 경로')+' · '+link(DOCS,'World Boxing · 공식 대회 문서')+'</p><p>수록 성적의 개별 근거는 선수·결과 링크에 있습니다. 자료 기준 '+e(data['as_of'])+'.</p></section>'
  text=re.sub(r'<title>.*?</title>','<title>'+e(n)+' | 복싱 · 올림픽예선</title>',template)
  text=re.sub(r'<h1 class="title">.*?</h1>','<h1 class="title">복싱 · '+e(n)+'</h1>',text)
  text=re.sub(r'<p class="intro">.*?</p>','<p class="intro">'+link('olboxing.html#boxing-index','← 체급 × 연도·대회 목차')+'</p>',text)
  text=re.sub(r'<main id="main">.*?</main>','<main id="main">'+content+'</main>',text,flags=re.S)
  text=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="복싱 '+e(n)+' 체급별 결과와 출전권 명단">',text)
  write(ROOT/page(k),text)
if __name__=='__main__': render()
