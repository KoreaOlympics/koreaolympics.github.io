(function () {
  'use strict';
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = (url, text) => /^https:\/\//.test(url || '') ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(text)} ↗</a>` : esc(text);
  function table(heads, rows, caption) {
    return `<div class="wi-wrap"><table class="data"><caption>${esc(caption)}</caption><thead><tr>${heads.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
  }
  const row = cells => `<tr>${cells.map(x=>`<td>${x}</td>`).join('')}</tr>`;
  function render(data, key) {
    const s = data.sports[key];
    if (!s) return '<p>이 종목의 자동 수집 자료는 준비 중입니다.</p>';
    const now = new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Seoul'});
    const checked = s.checked_at ? new Date(s.checked_at).toLocaleString('ko-KR',{timeZone:'Asia/Seoul'}) : '성공 이력 없음';
    const stale = !s.checked_at || Date.now()-Date.parse(s.checked_at)>3600000;
    let h = `<p class="note">마지막 수집 성공: ${esc(checked)} KST · ${s.status==='error'?'수집 오류 · 이전 자료 유지':stale?'갱신 지연':'수집 정상'}<br>15분 간격 수집 설정 · 초 단위 중계가 아닙니다. 일정 날짜는 개최지 기준입니다.</p>`;
    if(s.status==='error') h+=`<p class="notice wi">${esc(s.error || '원문을 가져오지 못했습니다.')}</p>`;
    h+=`<p>${esc(s.note || '')}</p><h3>2026–27 연간 일정</h3>`;
    const events = [...(s.events || [])].sort((a,b)=>a.start.localeCompare(b.start));
    h+=table(['기간','대회','개최지','상태'], events.map(e=>row([esc(e.start===e.end?e.start:`${e.start} ~ ${e.end}`),link(e.url,e.name),esc(e.location),esc(e.end<now?'종료':e.start>now?'예정':'진행 기간')])), '공식 발표 일정 · 변경 시 다음 수집에 반영');
    h+='<h3>최근 성적</h3>';
    h+=table(['대회 · 구분','선수 / 팀','순위','기록 · 성적','날짜 · 출처'],(s.results || []).map(r=>row([`${esc(r.event)}<br><small>${esc(r.discipline)}</small>`,`${esc(r.athlete)} <strong>${esc(r.country)}</strong>`,esc(r.rank),`${esc(r.score)}${r.details?'<br><small>'+esc(r.details)+'</small>':''}`,link(r.source,r.date)])), '수집 범위는 위 설명 참조 · 한국 선수는 KOR로 표시');
    if(s.recent?.length) h+='<details><summary>최근 공식 결과 원문</summary><ul>'+s.recent.map(e=>`<li>${link(e.results_url || e.url,e.name)} (${esc(e.start)})</li>`).join('')+'</ul></details>';
    if(key==='figure-skating') h+='<p class="note">SkatingScores는 현재 403 접근 차단으로 자동 수집에 사용하지 않습니다. '+link('https://www.skatingscores.com/','SkatingScores')+' · '+link('https://en.wikipedia.org/wiki/2026%E2%80%9327_figure_skating_season','Wikipedia 시즌 문서')+'</p>';
    return h;
  }
  if(typeof module!=='undefined') {module.exports={render};return;}
  const target=document.querySelector('[data-winter-sport]');
  if(!target)return;
  async function update(){
    try{const r=await fetch('./data/winter-live.json',{cache:'no-store'});if(!r.ok)throw Error(r.status);const d=await r.json();target.innerHTML=render(d,target.dataset.winterSport);}
    catch(e){const note=document.getElementById('winter-fetch-state');if(note)note.textContent='갱신 확인 실패 · 아래는 마지막 저장 자료입니다.';}
  }
  update();setInterval(()=>{if(!document.hidden)update();},60000);
})();
