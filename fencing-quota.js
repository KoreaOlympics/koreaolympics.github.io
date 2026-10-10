(function (root) {
  'use strict';
  const zones = ['Africa', 'America', 'Asia-Oceania', 'Europe'];
  const zoneNames = {Africa:'아프리카', America:'아메리카', 'Asia-Oceania':'아시아·오세아니아', Europe:'유럽'};
  const countryNames = {ALG:'알제리',ANG:'앙골라',ARG:'아르헨티나',AUS:'호주',AUT:'오스트리아',AZE:'아제르바이잔',BEL:'벨기에',BEN:'베냉',BLR:'벨라루스',BOL:'볼리비아',BRA:'브라질',BRN:'바레인',BUL:'불가리아',CAM:'캄보디아',CAN:'캐나다',CHI:'칠레',CHN:'중국',CIV:'코트디부아르',COL:'콜롬비아',CRC:'코스타리카',CRO:'크로아티아',CUB:'쿠바',CZE:'체코',DEN:'덴마크',DOM:'도미니카공화국',ECU:'에콰도르',EGY:'이집트',ESA:'엘살바도르',ESP:'스페인',EST:'에스토니아',FIN:'핀란드',FRA:'프랑스',GBR:'영국',GEO:'조지아',GER:'독일',GRE:'그리스',GUA:'과테말라',HKG:'홍콩',HUN:'헝가리',IND:'인도',IRI:'이란',IRL:'아일랜드',ISR:'이스라엘',ITA:'이탈리아',JAM:'자메이카',JOR:'요르단',JPN:'일본',KAZ:'카자흐스탄',KGZ:'키르기스스탄',KOR:'대한민국',KSA:'사우디아라비아',KUW:'쿠웨이트',LBA:'리비아',LUX:'룩셈부르크',MAC:'마카오',MAR:'모로코',MAS:'말레이시아',MDA:'몰도바',MEX:'멕시코',MRI:'모리셔스',NED:'네덜란드',NEP:'네팔',NGR:'나이지리아',NIG:'니제르',NOR:'노르웨이',NZL:'뉴질랜드',PAN:'파나마',PAR:'파라과이',PER:'페루',PHI:'필리핀',POL:'폴란드',POR:'포르투갈',PUR:'푸에르토리코',QAT:'카타르',ROU:'루마니아',RSA:'남아프리카공화국',RUS:'러시아',SEN:'세네갈',SGP:'싱가포르',SRI:'스리랑카',SUI:'스위스',SWE:'스웨덴',THA:'태국',TKM:'투르크메니스탄',TPE:'대만',TUN:'튀니지',TUR:'튀르키예',UAE:'아랍에미리트',UKR:'우크라이나',URU:'우루과이',USA:'미국',UZB:'우즈베키스탄',VEN:'베네수엘라',VIE:'베트남'};
  function qualify(teams) {
    if (teams.length < 24 || new Set(teams.map(t => t.code)).size !== teams.length || teams.some(t => !zones.includes(t.zone) || !Number.isFinite(t.points) || !Number.isInteger(t.rank) || t.rank < 1)) throw Error('불완전한 랭킹');
    const ordered = [...teams].sort((a,b) => a.rank-b.rank);
    const selected = ordered.filter(t => t.rank <= 4).map(t => ({...t, route:'세계 상위 4팀'}));
    if (selected.length !== 4 || ordered.some(t => t.rank === selected[3].rank && !selected.some(s => s.code === t.code))) return {unresolved:true, selected:[]};
    let missing = 0;
    for (const zone of zones) {
      const candidates = ordered.filter(t => t.rank >= 5 && t.rank <= 24 && t.zone === zone);
      if (!candidates.length) { missing++; continue; }
      if (candidates.filter(t => t.rank === candidates[0].rank).length > 1) return {unresolved:true, selected:[]};
      selected.push({...candidates[0], route:zoneNames[zone]+' 존 몫'});
    }
    while (missing--) {
      const candidates = ordered.filter(t => !selected.some(s => s.code === t.code));
      if (!candidates.length || candidates.filter(t => t.rank === candidates[0].rank).length > 1) return {unresolved:true, selected:[]};
      selected.push({...candidates[0], route:'빈 존 차순위 배정'});
    }
    return {unresolved:false, selected};
  }
  if (typeof module !== 'undefined') module.exports = {qualify};
  root.FencingQuota = {qualify};
  if (typeof document === 'undefined') return;
  const status = document.getElementById('quota-status');
  if (!status) return;
  const cards = document.getElementById('quota-events');
  let busy = false, lastFetched;
  function el(tag, text, cls) { const e = document.createElement(tag); if(text !== undefined) e.textContent = text; if(cls) e.className=cls; return e; }
  async function refresh() {
    if (busy) return;
    busy = true;
    const button = document.getElementById('quota-refresh');
    button.disabled = true;
    try {
      const response = await fetch('./data/fie-team-ranking.json?t='+Date.now(), {cache:'no-store'});
      if(!response.ok) throw Error('HTTP '+response.status);
      const data = await response.json();
      if(data.schemaVersion !== 1 || data.rankingType !== 'official-senior-team' || data.events.length !== 6 || new Set(data.events.map(e=>e.id)).size!==6 || !['fm','em','sm','ff','ef','sf'].every(id=>data.events.some(e=>e.id===id)) || !Number.isFinite(Date.parse(data.fetchedAt))) throw Error('자료 검증 실패');
      const results = data.events.map(e => ({...e, result:qualify(e.teams)}));
      const count = results.filter(e=>e.result.selected.some(t=>t.code==='KOR')).length;
      const unresolved = results.some(e=>e.result.unresolved);
      const fragment = document.createDocumentFragment();
      for(const event of results) {
        const card = el('section',undefined,'quota-card');
        card.append(el('h2',event.label+' 단체'));
        const korea = event.teams.find(t=>t.code==='KOR');
        const selected = event.result.selected.find(t=>t.code==='KOR');
        card.append(el('p',event.result.unresolved?'동순위 경계 · FIE 순위 확정 필요':selected?'한국 · 가상 쿼터권 · 3명':'한국 · 현재 가상 쿼터권 밖',selected?'quota-positive':'quota-result'));
        card.append(el('p',korea?`한국 ${korea.rank}위 · ${korea.points.toFixed(3)}점${selected?' · '+selected.route:''}`:'한국 랭킹 없음'));
        const rivals = event.teams.filter(t=>t.zone==='Asia-Oceania' && t.rank>=5 && t.rank<=24);
        card.append(el('p','아시아·오세아니아 존 선두: '+(rivals.length?`${rivals[0].code} ${rivals[0].rank}위 · ${rivals[0].points.toFixed(3)}점`:'5–24위 해당 팀 없음'),'small'));
        if(korea && rivals.length && rivals[0].code!=='KOR') {const gap=korea.points-rivals[0].points;card.append(el('p',`존 선두 대비 한국 ${Math.abs(gap).toFixed(3)}점 ${gap>=0?'앞섬':'뒤짐'} (순위는 FIE 공식 동률 규정 적용)`,'small'));}
        const detail=el('details'); detail.append(el('summary','국가별 랭킹 TOP 10'));
        if(event.result.unresolved) detail.append(el('p','동순위 경계로 쿼터 판정 보류'));
        detail.append(el('p','노란색 음영: 현재 순위 기준 가상 쿼터 배정 팀 · 굵은 글씨: 한국','small'));
        const wrap=el('div',undefined,'quota-table-wrap'), table=el('table',undefined,'data');
        table.append(el('caption',event.label+' · 단체 랭킹 TOP 10'));
        const head=el('thead'), tr=el('tr'); for(const title of ['순위','국가명']) {const th=el('th',title);th.scope='col';tr.append(th);} head.append(tr);table.append(head);
        const body=el('tbody');
        for(const team of event.teams.slice(0,10)) {const assigned=event.result.selected.find(t=>t.code===team.code);const row=el('tr',undefined,(assigned?'quota-qualified ':'')+(team.code==='KOR'?'quota-korea':''));const name=countryNames[team.code]||team.country;if(assigned)row.setAttribute('aria-label',`${team.rank}위 ${name} · 가상 배정`);row.append(el('td',String(team.rank)));const country=el('td',name);country.title=team.country+' ('+team.code+')';row.append(country);body.append(row);}table.append(body);wrap.append(table);detail.append(wrap);
        const link=el('a','FIE 전체 단체 랭킹 ↗');link.href=`https://fie.org/athletes?season=${data.season}&weapon=${event.id[0].toUpperCase()}&gender=${event.id[1].toUpperCase()}&category=S&type=E`;detail.append(link);card.append(detail);fragment.append(card);
      }
      cards.replaceChildren(fragment);
      lastFetched=data.fetchedAt;
      const old=Date.now()-Date.parse(data.fetchedAt)>7*86400000;
      status.textContent=`${data.season-1}/${data.season} 시즌 · FIE 수집 ${new Date(data.fetchedAt).toLocaleString('ko-KR',{timeZone:'Asia/Seoul'})} (한국시간)${old?' · 주의: 7일 이상 지난 자료':''}`;
      document.getElementById('quota-total').textContent=unresolved?`${count}종목 판정 · 일부 동순위 보류`:`가상 단체 쿼터 ${count}종목 · 선수 ${count*3}명`;
    } catch(error) { status.textContent='최신 자료를 불러오지 못했습니다. '+(lastFetched?'아래는 이전에 불러온 자료입니다.':'계산 결과를 표시할 수 없습니다.')+' 새로고침하거나 FIE 공식 랭킹을 확인하세요.'; }
    finally {busy=false;button.disabled=false;}
  }
  document.getElementById('quota-refresh').addEventListener('click',refresh);
  refresh();setInterval(refresh,60000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden) refresh();});
})(typeof globalThis !== 'undefined' ? globalThis : this);
