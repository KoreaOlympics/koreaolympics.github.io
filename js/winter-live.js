(function () {
  'use strict';
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = (url, text) => /^https:\/\//.test(url || '') ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(text)} ↗</a>` : esc(text);
  function table(heads, rows, caption) {
    return `<div class="wi-wrap" tabindex="0" role="region" aria-label="${esc(caption)}"><table class="data"><caption>${esc(caption)}</caption><thead><tr>${heads.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.join(''):`<tr><td colspan="${heads.length}">표시할 자료가 없습니다. 공식 원문을 확인해 주세요.</td></tr>`}</tbody></table></div>`;
  }
  const row = cells => `<tr>${cells.map(x=>`<td>${x}</td>`).join('')}</tr>`;
  function render(data, key, options = {}) {
    const s = data.sports[key];
    if (!s) return '<p>이 종목의 자동 수집 자료는 준비 중입니다.</p>';
    const now = options.today || new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Seoul'});
    const checked = s.checked_at ? new Date(s.checked_at).toLocaleString('ko-KR',{timeZone:'Asia/Seoul'}) : '성공 이력 없음';
    const stale = !s.checked_at || Date.now()-Date.parse(s.checked_at)>3600000;
    let h = `<p class="note">마지막 수집 성공: ${esc(checked)} KST · ${s.status==='error'?'수집 오류 · 이전 자료 유지':stale?'갱신 지연':'수집 정상'}<br>15분 간격 수집 설정(실행이 지연될 수 있음). 수집 시각은 경기 결과 확정 시각과 다릅니다. 일정은 개최지 날짜이며 상태는 한국 날짜 기준 참고 표시입니다.</p>`;
    if(s.status==='error') h+=`<p class="notice wi">${esc(s.error || '원문을 가져오지 못했습니다.')}</p>`;
    h+=`<p>${esc(s.note || '')}</p><p>${link(s.source,'공식 일정 / 자료 제공처')} ${s.result_index?' · '+link(s.result_index,'공식 결과 목록'):''}</p><h3>${esc(data.season || '2026/2027')} 연간 일정</h3>`;
    const seasonStart = Number((data.season || '2026/2027').split('/')[0]);
    const allEvents = [...(s.events || [])].filter(e=>e.end>=`${seasonStart}-07-01` && e.start<`${seasonStart+1}-07-01`).sort((a,b)=>a.start.localeCompare(b.start));
    const months = [...new Set(allEvents.flatMap(e=>[e.start.slice(0,7),e.end.slice(0,7)]))].sort();
    const selected = (v,x) => v===x?' selected':'';
    h+=`<div class="wi-filters"><label>월 <select data-wi-filter="month"><option value="">전체 월</option>${months.map(m=>`<option${selected(options.month,m)} value="${esc(m)}">${esc(m)}</option>`).join('')}</select></label><label>일정 <select data-wi-filter="upcoming"><option value="">전체 일정</option><option value="yes"${selected(options.upcoming,'yes')}>오늘 이후 · 진행 기간</option></select></label></div>`;
    const events = allEvents.filter(e=>(!options.month || (e.start.slice(0,7)<=options.month && e.end.slice(0,7)>=options.month)) && (!options.upcoming || e.end>=now));
    h+=`<p class="note" role="status">일정 ${events.length}건 / 시즌 전체 ${allEvents.length}건</p>`;
    h+=table(['기간','대회','개최지','상태'], events.map(e=>row([esc(e.start===e.end?e.start:`${e.start} ~ ${e.end}`),link(e.url,e.name),esc(e.location),esc(e.end<now?'종료':e.start>now?'예정':'진행 기간')])), '공식 발표 일정 · 변경 시 다음 수집에 반영');
    h+=`<h3>${key==='short-track'?'2026 세계선수권 우승 기록':key==='speed-skating'?'시즌 최고기록 순위':key==='curling'?'최근 대회 라운드로빈 승패':'최근 수집 대회 성적'}</h3>`;
    h+=`<div class="wi-filters"><label>선수 / 팀 <select data-wi-filter="country"><option value="">전체 수집 성적</option><option value="KOR"${selected(options.country,'KOR')}>한국 (KOR)</option></select></label></div>`;
    const results=(s.results || []).filter(r=>!options.country || r.country===options.country);
    h+=`<p class="note" role="status">성적 ${results.length}건 · 한국 성적이 없으면 해당 수집 범위에 포함되지 않은 것이며 미출전을 뜻하지 않습니다.</p>`;
    h+=table(['대회 · 구분','선수 / 팀','순위','기록 · 성적','기준 날짜 · 출처'],results.map(r=>row([`${esc(r.event)}<br><small>${esc(r.discipline)}</small>`,`${esc(r.athlete)} <strong${r.country==='KOR'?' class="wi-kor"':''}>${esc(r.country)}</strong>`,esc(r.rank),`${esc(r.score)}${r.details?'<br><small>'+esc(r.details)+'</small>':''}`,link(r.source,r.date)])), '수집 범위는 위 설명 참조 · 날짜의 의미는 종목별 설명 참조');
    if(s.recent?.length) h+='<details><summary>최근 공식 결과 원문</summary><ul>'+s.recent.map(e=>`<li>${link(e.results_url || e.url,e.name)} (${esc(e.start)})</li>`).join('')+'</ul></details>';
    if(key==='figure-skating') h+='<p class="note">SkatingScores는 현재 403 접근 차단으로 자동 수집에 사용하지 않습니다. '+link('https://www.skatingscores.com/','SkatingScores')+' · '+link('https://en.wikipedia.org/wiki/2026%E2%80%9327_figure_skating_season','Wikipedia 시즌 문서')+'</p>';
    return h;
  }
  if(typeof module!=='undefined') {module.exports={render};return;}
  const target=document.querySelector('[data-winter-sport]');
  if(!target)return;
  let data, busy=false;
  const options={};
  target.addEventListener('change',event=>{
    const name=event.target.dataset.wiFilter;
    if(!name || !data)return;
    options[name]=event.target.value;
    target.innerHTML=render(data,target.dataset.winterSport,options);
    target.querySelector(`[data-wi-filter="${name}"]`)?.focus();
  });
  async function update(){
    if(busy)return;
    busy=true;
    try{const r=await fetch('./data/winter-live.json',{cache:'no-store',signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error(r.status);const d=await r.json();if(!d.sports?.[target.dataset.winterSport])throw Error('Missing sport');data=d;const focused=target.contains(document.activeElement)?document.activeElement.dataset.wiFilter:null;target.innerHTML=render(data,target.dataset.winterSport,options);if(focused)target.querySelector(`[data-wi-filter="${focused}"]`)?.focus();const note=document.getElementById('winter-fetch-state');if(note)note.textContent='';}
    catch(e){const note=document.getElementById('winter-fetch-state');if(note)note.textContent='갱신 확인 실패 · 아래는 마지막 저장 자료입니다.';}
    finally{busy=false;}
  }
  update();setInterval(()=>{if(!document.hidden)update();},60000);
})();
