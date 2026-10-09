(async()=>{
const target=document.getElementById('events'),states={scheduled:'예정',in_progress:'진행 중',awaiting_results:'결과 확인 대기',results_confirmed:'결과 확정',wsr_confirmed:'WSR 반영 확인'};
function add(parent,tag,text){const el=document.createElement(tag);el.textContent=text;parent.append(el);return el}
function link(parent,url,label){if(!url)return;const parsed=new URL(url);if(parsed.protocol!=='https:')return;const a=add(parent,'a',label);a.href=url;parent.append(' · ')}
try{const r=await fetch('data/skateboard-events.json');if(!r.ok)throw Error(r.status);const data=await r.json();document.getElementById('updated').textContent='최근 갱신: '+data.updated_at;
function render(){target.replaceChildren();const filtered=data.events.filter(e=>['discipline','gender','status'].every(k=>!document.getElementById(k).value||document.getElementById(k).value===e[k]));if(!filtered.length)add(target,'p','해당 기록이 없습니다.');
filtered.forEach(e=>{const box=add(target,'section','');add(box,'h2',e.name+' · '+(e.gender==='men'?'남자':'여자'));add(box,'p',e.start_date+' ~ '+e.end_date+' | '+e.venue+' | '+states[e.status]);add(box,'p','확인 '+e.checked_at+' · WSR 반영 '+(e.status==='wsr_confirmed'?'확인':'미확인')+' · LA28 포인트 '+(e.la28_points_eligible===null?'검증 대기':e.la28_points_eligible?'인정':'불인정'));link(box,e.official_event_url,'공식 대회');link(box,e.official_results_url,'공식 결과');link(box,e.result_sheet_url,'공식 결과표');link(box,e.wsr_url,'공식 WSR');
const changes=new Map(e.wsr_changes.map(x=>[x.athlete_id,x]));if(e.results_scope==='finalists')add(box,'p','수록 범위: 결승 진출 8명. 경기 점수는 WSR 포인트와 별도입니다.');if(!e.results.length)add(box,'p','공식 최종 결과 미수록');e.results.forEach(x=>{const c=changes.get(x.athlete_id);add(box,'p',x.position+'위 '+x.name+' ('+x.noc+') · 경기 점수 '+(x.event_score??'미확인')+' · WSR 포인트 '+(x.wsr_points??'미확인')+' · 순위 '+(c?c.previous_rank+' → '+c.current_rank+' (변동 '+(c.previous_rank-c.current_rank)+')':'반영 미확인'))});const d=add(box,'details','');add(d,'summary','변경 이력');e.history.forEach(h=>add(d,'p',h.at+' · '+h.note));});}
['discipline','gender','status'].forEach(k=>document.getElementById(k).addEventListener('change',render));render();
}catch(e){add(target,'p','기록을 불러오지 못했습니다. 잠시 후 다시 확인해 주세요.')}
})();
