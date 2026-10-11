import re,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'index.html';s=p.read_text(encoding='utf-8')
# Remove the two completed/current-event shortcuts, keeping the permanent hubs.
for href in ['issue-judo-worlds-2026.html','issue-lacrosse-sixes-2026.html']:
 s=re.sub(r'<a class="quota-hub hot-card" href="'+re.escape(href)+r'">.*?</a>','',s,flags=re.S)
s=s.replace('HOT ISSUE · 바로가기','현황 · 다가오는 주요 대회')
s=s.replace('진행 중·임박한 예선','다가오는 예선').replace('진행 중·임박한 LA28 예선','다가오는 LA28 예선')
s=s.replace('return a.getFullYear()===yy&&a.getMonth()===mm&&b>=first;','return a.getFullYear()===yy&&a.getMonth()===mm&&a>today;')
start=s.index('  (function(){var box=document.getElementById(\'live-routes\')')
end=s.index('\n',start)
s=s[:start]+"  (function(){var box=document.getElementById('live-routes'),state=document.getElementById('spot-dday');if(!box)return;var today=new Date();today.setHours(0,0,0,0);var items=EV.filter(function(x){return new Date(x.s+'T00:00:00')>today;}).sort(function(a,b){return a.s.localeCompare(b.s);}).slice(0,4);state.textContent=items.length?'다음 예선 '+items[0].s:'일정 확인 대기';box.innerHTML=items.map(function(x){return '<a class=\"live-route\" href=\"'+x.h+'\"><small>예정 · '+x.s+' · '+KIND[x.k]+'</small><b>'+x.ic+' '+x.sp+'</b><span>'+x.t+'</span></a>';}).join('')||'<span>다가오는 등록 일정 확인 대기</span>';})();"+s[end:]
events=[{'start':'2026-10-14','end':'2026-10-18','icon':'🚴','title':'상하이 트랙 세계선수권','role':'트랙 올림픽 랭킹 반영 대회','href':'olcycling-2026-world.html#track'}, {'start':'2026-10-17','end':'2026-10-25','icon':'🤸','title':'로테르담 기계체조 세계선수권','role':'남녀 단체 상위 3개국 직행 경로','href':'olgymnastics-2026-world.html#artistic'}, {'start':'2026-10-27','end':'2026-11-08','icon':'🏋️','title':'닝보 역도 세계선수권','role':'OQR 1기 첫 대회 · 합계 기록 적립','href':'olweightlifting-2026-world.html'}, {'start':'2026-11-01','end':'2026-11-14','icon':'🎯','title':'도하 사격 세계선수권','role':'올림픽 출전권 배정 대회','href':'olshooting-2026-world.html'}, {'start':'2026-12-07','end':'2026-12-16','icon':'🏋️','title':'도하 IWF 예선 I','role':'OQR 1기 · 두 번째 공식 예선 대회','href':'olweightlifting-2026-qualifier-1.html'}]
(R/'data/index-featured-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
css='''<style id="featured-events-style">.featured-events{margin:18px 0}.featured-events h3{font-size:14px;margin:0 0 10px}.event-cards{display:grid;gap:10px}.event-card{display:grid;grid-template-columns:38px minmax(0,1fr);gap:10px;padding:14px;border:1px solid #d6dfeb;border-left:4px solid #3865b0;border-radius:8px;background:linear-gradient(110deg,#eef4ff,#fff);text-decoration:none!important}.event-card .event-icon{font-size:28px}.event-card time{display:block;color:#526580;font-size:12px;font-variant-numeric:tabular-nums;white-space:nowrap}.event-card strong{display:block;color:#18365e;font-size:15px;margin:4px 0;line-height:1.4}.event-card small{display:block;color:#4d5c70;line-height:1.5}.event-card:focus-visible{outline:3px solid #e0ad19}.event-empty{font-size:13px;color:#637188}@media(max-width:760px){.event-card{padding:12px}.event-card strong{font-size:14px}}</style>'''
s=re.sub(r'<style id="featured-events-style">.*?</style>','',s,flags=re.S).replace('</head>',css+'</head>')
s=re.sub(r'<!-- featured-events:start -->.*?<!-- featured-events:end -->','',s,flags=re.S)
block='<!-- featured-events:start --><section class="featured-events" aria-labelledby="featured-title"><h3 id="featured-title">다가오는 주요 대회</h3><nav class="event-cards" id="featured-events" aria-label="다가오는 주요 대회"><span class="event-empty">일정 계산 중…</span></nav></section><!-- featured-events:end -->'
s=s.replace('</nav></div></section><section class="issues-pane"', '</nav>'+block+'</div></section><section class="issues-pane"',1)
script="""<script id="featured-events-script">(function(){var events=EVENT_DATA;function render(){var now=new Date();now.setHours(0,0,0,0);var upcoming=events.filter(function(e){return new Date(e.start+'T00:00:00')>now;}).sort(function(a,b){return a.start.localeCompare(b.start);}).slice(0,4),box=document.getElementById('featured-events');if(!box)return;box.innerHTML=upcoming.map(function(e){return '<a class="event-card" href="'+e.href+'"><span class="event-icon" aria-hidden="true">'+e.icon+'</span><span><time datetime="'+e.start+'">'+e.start+' — '+e.end+'</time><strong>'+e.title+'</strong><small>'+e.role+' →</small></span></a>';}).join('')||'<span class="event-empty">다음 주요 대회 일정 확인 대기 · <a href="#upcoming">전체 일정</a></span>';}render();setInterval(render,60000);document.addEventListener('visibilitychange',function(){if(!document.hidden)render();});})();</script>""".replace('EVENT_DATA',json.dumps(events,ensure_ascii=False))
s=re.sub(r'<script id="featured-events-script">.*?</script>','',s,flags=re.S).replace('</body>',script+'</body>')
# Add IWF Qualifier I to the shared upcoming-event feed once.
if '2026-12-07' not in re.search(r'var EV=(.*?);',s,re.S)[1]:
 m=re.search(r'var EV=(.*?);',s,re.S);feed=json.loads(m[1]);feed.append({'s':'2026-12-07','e':'2026-12-16','ic':'🏋️','sp':'역도','h':'olweightlifting-2026-qualifier-1.html','t':'IWF 예선 I · 도하 — OQR 1기간','k':'rank'});feed.sort(key=lambda x:x['s']);s=s[:m.start(1)]+json.dumps(feed,ensure_ascii=False)+s[m.end(1):]
p.write_text(s,encoding='utf-8',newline='\n')
print('Updated main event cards and future-only schedules')
