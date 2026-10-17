"""Render LA28 weight × qualification-event navigation from one event catalogue."""
import hashlib, json, re
from pathlib import Path
from html import escape
ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'https://iwf.sport/wp-content/plugins/download-monitor/download.php?id=2934'
CALENDAR = 'https://iwf.sport/events/calendar-2026/'
WEIGHTS = [('m65','남자 65kg'),('m75','남자 75kg'),('m85','남자 85kg'),('m95','남자 95kg'),('m110','남자 110kg'),('mo110','남자 +110kg'),('w53','여자 53kg'),('w61','여자 61kg'),('w69','여자 69kg'),('w77','여자 77kg'),('w86','여자 86kg'),('wo86','여자 +86kg')]
EVENTS = [
 ('2026-world','2026 세계선수권',1,'10.27–11.08 · 닝보'),
 ('2026-qualifier-1','2026 IWF 예선 I',1,'12.07–12.16 · 도하'),
 ('2027-qualifier-2','2027 IWF 예선 II',1,'세부 일정 확인 대기'),
 ('2027-continental','2027 대륙선수권',1,'한국: 아시아선수권 · 세부 일정 확인 대기'),
 ('2027-qualifier-3','2027 IWF 예선 III',1,'세부 일정 확인 대기'),
 ('2027-world','2027 세계선수권',1,'세부 일정 확인 대기'),
 ('2027-qualifier-4','2027 IWF 예선 IV',2,'세부 일정 확인 대기'),
 ('2028-qualifier-5','2028 IWF 예선 V',2,'세부 일정 확인 대기'),
 ('2028-continental','2028 대륙선수권',2,'한국: 아시아선수권 · 세부 일정 확인 대기'),
 ('2028-world','2028 세계선수권',2,'예선 종료 2028.05.07 이전 · 세부 일정 확인 대기')]
def link(file,label): return f'<a href="{file}">{escape(label)}</a>'
def table(head, rows, matrix=False):
 return '<div class="wl-scroll" tabindex="0" aria-label="표 좌우 스크롤"><table class="data '+('wl-matrix' if matrix else 'wl-table')+'"><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">' if i==0 else '<td>')+v+('</th>' if i==0 else '</td>') for i,v in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'
def rule():
 return '<p>2026.08.01부터 적용된 새 체급 기준. OQR은 <strong>1기 최고 합계 3개 + 2기 최고 합계 2개</strong>를 더합니다. 같은 올림픽 체급에서 각 기간의 유효 합계 수를 채워야 하며, 대회 메달만으로 출전권이 확정되지는 않습니다.</p><p>비올림픽 체급 반영: 남자 60→65kg, 70→75kg · 여자 49→53kg, 57→61kg. 2025년 및 개편 전 체급 기록은 아래 예선 기록에 자동 이월하지 않습니다.</p><p class="small">규정: '+link(SOURCE,'IWF LA28 · 2026.10.02판 (부록 10–12쪽)')+' · '+link(CALENDAR,'IWF 2026 일정')+' · 확인 2026.10.11</p>'
def inject(s,body):
 s=re.sub(r'<!-- weightlifting-orthogonal:start -->.*?<!-- weightlifting-orthogonal:end -->','',s,flags=re.S)
 return s.replace('<main id="main">','<main id="main"><!-- weightlifting-orthogonal:start -->'+body+'<!-- weightlifting-orthogonal:end -->',1)
def style(s):
 s=re.sub(r'<link rel="stylesheet" href="\./css/weightlifting-orthogonal.css[^\"]*">','',s)
 return s.replace('</head>',f'<link rel="stylesheet" href="./css/weightlifting-orthogonal.css?v={HASH}"></head>')
CSS='''.wl-scroll{max-width:100%;overflow-x:auto;margin:1rem 0}.wl-table th,.wl-table td,.wl-matrix th,.wl-matrix td{white-space:nowrap;padding:.65rem .8rem;word-break:normal}.wl-matrix{min-width:1250px;border-collapse:collapse}.wl-matrix th:first-child,.wl-matrix td:first-child{position:sticky;left:0;background:#f4f6fa;z-index:1}.wl-links{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}.wl-links a{border:1px solid #ccd5e0;padding:.4rem .6rem;background:#f7f9fc;border-radius:3px}.wl-period{background:#fff4cc;padding:.7rem;border-left:4px solid #d6a600}@media(max-width:600px){.wl-links a{font-size:.9rem}.wl-scroll{font-size:.9rem}.wl-table{min-width:540px}}'''
(ROOT/'css/weightlifting-orthogonal.css').write_text(CSS,encoding='utf-8')
HASH=hashlib.sha256(CSS.encode()).hexdigest()[:12]
catalog={'as_of':'2026-10-11','qualification_source':SOURCE,'weights':WEIGHTS,'events':[{'id':i,'name':n,'period':p,'schedule':d,'results':[]} for i,n,p,d in EVENTS]}
(ROOT/'data/weightlifting-pathways.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
main=ROOT/'olweightlifting.html'
template=main.read_text(encoding='utf-8')
nav='<nav class="wl-links" aria-label="역도 예선 대회">'+''.join(link(f'olweightlifting-{i}.html',n) for i,n,p,d in EVENTS)+'</nav>'
body='<section id="wl-orthogonal"><h2>체급 × 예선 대회</h2>'+rule()+'<h3>체급 문서</h3><nav class="wl-links">'+''.join(link(f'olweightlifting-ev-{i}.html',n) for i,n in WEIGHTS)+'</nav><h3>대회 문서</h3>'+nav+table(['체급']+[link(f'olweightlifting-{i}.html',n) for i,n,p,d in EVENTS],[[link(f'olweightlifting-ev-{w}.html',n)]+[link(f'olweightlifting-{i}.html#{w}','기록') for i,_,_,_ in EVENTS] for w,n in WEIGHTS],True)+'</section>'
# Keep basic explanation before the new index.
clean=re.sub(r'<!-- weightlifting-orthogonal:start -->.*?<!-- weightlifting-orthogonal:end -->','',template,flags=re.S)
clean=re.sub(r'<section id="weight-matrix">.*?</section>','',clean,flags=re.S)
overview=re.search(r'<section id="overview">.*?</section>',clean,re.S)
if overview: clean=clean[:overview.end()]+'<!-- weightlifting-orthogonal:start -->'+body+'<!-- weightlifting-orthogonal:end -->'+clean[overview.end():]
else: clean=inject(clean,body)
main.write_text(style(clean),encoding='utf-8',newline='\n')
for w,n in WEIGHTS:
 path=ROOT/f'olweightlifting-ev-{w}.html'
 body='<section id="wl-results"><h2>'+n+' · 예선 대회 기록</h2>'+rule()+table(['대회','선수 · 합계 / 상태'],[[link(f'olweightlifting-{i}.html#{w}',name),f'{p}기 · 결과 대기'] for i,name,p,d in EVENTS])+'<p>'+link('olweightlifting.html#wl-orthogonal','전체 체급 × 대회')+'</p></section>'
 path.write_text(style(inject(path.read_text(encoding='utf-8'),body)),encoding='utf-8',newline='\n')
for i,n,p,d in EVENTS:
 body='<section id="overview"><h2>'+n+'</h2><p class="wl-period">OQR '+str(p)+'기 · '+d+'</p>'+rule()
 if 'continental' in i: body+='<p>아시아·유럽·팬아메리카·아프리카·오세아니아 중 소속 대륙의 승인 대회 기록을 반영합니다. 2027년은 IWF가 승인한 대륙선수권 또는 대륙 종합대회 1개가 해당됩니다.</p>'
 body+='</section><nav class="wl-links">'+link('olweightlifting.html#wl-orthogonal','전체 체급 × 대회')+link('olweightlifting-oqr.html','OQR 규정')+'</nav>'+''.join('<section id="'+w+'"><h2>'+link(f'olweightlifting-ev-{w}.html',name)+'</h2>'+table(['선수','합계 · 상태'],[['명단 확인 대기','결과 대기']])+'</section>' for w,name in WEIGHTS)
 s=re.sub(r'<main id="main">.*?</main>','<main id="main">'+body+'</main>',template,flags=re.S)
 s=re.sub(r'<title>.*?</title>','<title>'+n+' | 역도 예선</title>',s)
 s=re.sub(r'<h1 class="title">.*?</h1>','<h1 class="title">'+n+'</h1>',s)
 s=re.sub(r'<p class="intro">.*?</p>','<p class="intro">새 체급별 결과와 LA28 예선 반영을 연결하는 대회 문서.</p>',s)
 (ROOT/f'olweightlifting-{i}.html').write_text(style(s),encoding='utf-8',newline='\n')
# Expose the event catalogue on the ranking document too.
path=ROOT/'olweightlifting-oqr.html'
s=path.read_text(encoding='utf-8')
s=inject(s,'<section id="wl-catalog"><h2>공식 예선 10개 대회</h2>'+rule()+nav+'</section>')
path.write_text(style(s),encoding='utf-8',newline='\n')
print('Rendered 12 weight pages, 10 competition pages, main and OQR.')
