'use strict';
// 동계 실시간 센터: data/winter/*.json (tools/winter/collect.py 산출물)을 읽어 그린다.
const DATA = '../data/winter/';
const SPORTS = { 'short-track': '쇼트트랙', 'speed-skating': '스피드스케이팅', 'figure-skating': '피겨스케이팅', 'snowboard': '스노보드' };
const ROUNDS = { 'Preliminaries': '1차 예선', 'Heats': '예선', 'Rep. Heats': '패자부활 예선', 'Rep. Quarterfinals': '패자부활 준준결승',
  'Rep. Semifinals': '패자부활 준결승', 'Quarterfinals': '준준결승', 'Semifinals': '준결승', 'Final A': '결승 A', 'Final B': '결승 B', 'Finals': '결승',
  'Short Program': '쇼트 프로그램', 'Free Skating': '프리 스케이팅', 'Rhythm Dance': '리듬 댄스', 'Free Dance': '프리 댄스' };
const TITLES = [[/^Men /, '남자 '], [/^Women /, '여자 '], [/^Mixed Team Relay/, '혼성 계주'], [/ Relay$/, ' 계주'], [/^Men$/, '남자 싱글'],
  [/^Women$/, '여자 싱글'], [/^Pairs$/, '페어'], [/^Ice Dance$/, '아이스댄스'], [/ m\b/, 'm']];
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const state = { tab: 'now', sport: '', q: '', event: null, cal: null, korea: null, status: null, names: {}, events: {}, columns: [], column: null };

// ---------- time helpers (KST) ----------
const KST = { timeZone: 'Asia/Seoul' };
const kstDate = d => new Date(d).toLocaleDateString('en-CA', KST);
const kstTime = d => new Date(d).toLocaleTimeString('ko-KR', { ...KST, hour: '2-digit', minute: '2-digit', hour12: false });
const kstDay = d => new Date(d).toLocaleDateString('ko-KR', { ...KST, month: 'numeric', day: 'numeric', weekday: 'short' });
const today = () => kstDate(Date.now());
const fmtRange = (a, b) => a === b ? a.slice(5).replace('-', '.') : `${a.slice(5).replace('-', '.')} ~ ${b.slice(5).replace('-', '.')}`;
const ago = d => { const m = Math.round((Date.now() - Date.parse(d)) / 60000); return m < 1 ? '방금' : m < 60 ? `${m}분 전` : m < 1440 ? `${Math.round(m / 60)}시간 전` : `${Math.round(m / 1440)}일 전`; };
const title = t => TITLES.reduce((s, [re, ko]) => s.replace(re, ko), t || '');
const round = r => ROUNDS[r] || r || '';
const name = n => state.names[n] ? `${state.names[n]} <span class="muted small">${esc(n)}</span>` : esc(n);

// ---------- data ----------
async function getJSON(path) {
  const r = await fetch(DATA + path + (path.includes('?') ? '&' : '?') + 't=' + Math.floor(Date.now() / 60000), { cache: 'no-store' });
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}
async function loadAll() {
  const [cal, korea, status, names, colIdx] = await Promise.all([getJSON('calendar.json'), getJSON('korea.json'),
    getJSON('status.json').catch(() => null), getJSON('names-ko.json').catch(() => ({})), getJSON('columns/index.json').catch(() => ({ columns: [] }))]);
  Object.assign(state, { cal, korea, status, names, columns: colIdx.columns || [] });
  $('#season').textContent = cal.season || '';
  $('#updated').textContent = status ? `자료 갱신 ${ago(status.updated_at)} (${kstDay(status.updated_at)} ${kstTime(status.updated_at)})` : '';
}
async function loadEvent(id, force) {
  if (!force && state.events[id]) return state.events[id];
  try { state.events[id] = await getJSON(`events/${id}.json`); } catch { state.events[id] = null; }
  return state.events[id];
}
function allEvents() {
  return Object.entries(state.cal?.sports || {}).flatMap(([sport, s]) => (s.events || []).map(e => ({ ...e, sport })))
    .sort((a, b) => a.start.localeCompare(b.start));
}
function phase(e) {
  const t = today();
  if (e.state === 'Cancelled') return 'cancel';
  if (e.state === 'Live' || (e.start <= t && t <= e.end)) return 'live';
  return e.end < t ? 'done' : 'soon';
}
const BADGE = { live: '<span class="badge live">LIVE</span>', done: '<span class="badge done">종료</span>', soon: '<span class="badge soon">예정</span>', cancel: '<span class="badge">취소</span>' };
function match(e) {
  if (state.sport && e.sport !== state.sport) return false;
  const q = state.q.trim().toLowerCase();
  return !q || [e.name, e.city, e.country, e.category, SPORTS[e.sport]].join(' ').toLowerCase().includes(q);
}

// ---------- views ----------
function eventCard(e) {
  const p = phase(e);
  return `<a class="ev" href="#tab=event&e=${encodeURIComponent(e.id)}"><div class="sport ${e.sport}">${SPORTS[e.sport]} ${BADGE[p]}</div>
    <div class="t">${esc(e.name)}</div><div class="m">${fmtRange(e.start, e.end)} · ${esc(e.city)}${e.country ? ' (' + esc(e.country) + ')' : ''}${e.category ? ' · ' + esc(e.category) : ''}</div>
    ${p === 'live' && e.live ? `<div class="m">진행 중: ${esc(title(e.live))}</div>` : ''}</a>`;
}

async function viewNow() {
  const evs = allEvents().filter(match);
  const live = evs.filter(e => phase(e) === 'live');
  const soon = evs.filter(e => phase(e) === 'soon').slice(0, 8);
  let h = '';
  const kor = (state.korea?.rows || []).filter(r => !state.sport || r.sport === state.sport);
  h += `<div class="stat"><div class="s"><b>${live.length}</b><span>진행 중 대회</span></div><div class="s"><b>${soon.length ? fmtRange(soon[0].start, soon[0].start) : '-'}</b><span>다음 대회 시작</span></div><div class="s"><b>${kor.length}</b><span>수집된 한국 선수 기록</span></div></div>`;
  h += '<h2>진행 중</h2>';
  if (!live.length) h += '<div class="card muted">지금 진행 중인 대회가 없습니다.</div>';
  for (const e of live) {
    const d = await loadEvent(e.id);
    h += `<div class="card">${eventCard(e)}${d ? sessionsTable(d, { windowHours: 30 }) : '<p class="muted small">상세 자료 수집 대기 중</p>'}`;
    const kr = (d?.korea || []).slice().sort((a, b) => (b.start_utc || '').localeCompare(a.start_utc || '')).slice(0, 12);
    if (kr.length) h += `<h3>🇰🇷 한국 선수 최근 기록</h3>${koreaTable(kr, false)}`;
    h += `<p><a href="#tab=event&e=${encodeURIComponent(e.id)}">전체 결과·대진 보기 →</a></p></div>`;
  }
  h += '<h2>다가오는 대회</h2>' + (soon.length ? `<div class="grid">${soon.map(eventCard).join('')}</div>` : '<div class="card muted">예정된 대회가 없습니다.</div>');
  return h;
}

function viewCalendar() {
  const evs = allEvents().filter(match);
  if (!evs.length) return '<div class="empty">조건에 맞는 대회가 없습니다.</div>';
  let h = `<p class="muted small">${evs.length}개 대회 · 날짜는 개최지 기준</p>`, month = '';
  for (const e of evs) {
    const m = e.start.slice(0, 7);
    if (m !== month) { if (month) h += '</div>'; month = m; h += `<div class="month">${m.replace('-', '년 ')}월</div><div class="grid">`; }
    h += eventCard(e);
  }
  return h + '</div>';
}

function koreaTable(rows, withEvent = true) {
  return `<div class="tablewrap"><table><thead><tr>${withEvent ? '<th>대회</th>' : ''}<th>종목</th><th>라운드</th><th>선수</th><th class="num">순위</th><th class="num">기록</th><th>진출</th></tr></thead><tbody>${
    rows.map(r => `<tr class="kor">${withEvent ? `<td><a href="#tab=event&e=${encodeURIComponent(r.event_id)}">${esc(r.event)}</a><br><span class="small muted">${r.start_utc ? kstDay(r.start_utc) : ''}</span></td>` : ''}
      <td>${esc(title(r.distance))}</td><td>${esc(round(r.round))}${r.heat ? ` <span class="muted small">${esc(r.heat.replace('Heat', '조'))}</span>` : ''}</td>
      <td class="name">${name(r.name)}</td><td class="num">${r.rank ?? '-'}</td><td class="num">${esc(r.time)}${r.status ? ` <span class="small">${esc(r.status)}</span>` : ''}</td>
      <td class="q">${esc(r.qual)}</td></tr>`).join('')}</tbody></table></div>`;
}

function viewKorea() {
  const q = state.q.trim().toLowerCase();
  const rows = (state.korea?.rows || []).filter(r => (!state.sport || r.sport === state.sport) &&
    (!q || [r.name, state.names[r.name], r.event, r.distance].join(' ').toLowerCase().includes(q)));
  if (!rows.length) return '<div class="empty">수집된 한국 선수 기록이 없습니다.</div>';
  const athletes = [...new Set(rows.map(r => r.name))];
  return `<p class="muted small">기록 ${rows.length}건 · 선수 ${athletes.length}명 · 최신순</p>
    <div class="controls">${athletes.map(a => `<button class="chip" data-athlete="${esc(a)}">${state.names[a] || esc(a)}</button>`).join('')}</div>` + koreaTable(rows);
}

function sessionsTable(d, { windowHours } = {}) {
  let s = (d.sessions || []).slice().sort((a, b) => a.start_utc.localeCompare(b.start_utc));
  const now = Date.now();
  if (windowHours) s = s.filter(x => Math.abs(Date.parse(x.start_utc) - now) < windowHours * 3600e3);
  if (!s.length) return '';
  const nextIdx = s.findIndex(x => Date.parse(x.start_utc) > now);
  return `<div class="tablewrap"><table class="timeline"><tbody>${s.map((x, i) => {
    const cls = i === nextIdx ? 'now' : Date.parse(x.start_utc) < now ? 'past' : '';
    return `<tr class="${cls}"><td class="time">${kstDay(x.start_utc)} <b>${kstTime(x.start_utc)}</b></td><td>${esc(title(x.title))}</td><td>${esc(round(x.round))}</td></tr>`;
  }).join('')}</tbody></table></div>`;
}

function heatTable(h) {
  return `<div class="heat"><div class="hn">${esc(h.name.replace('Heat', '조'))} ${h.official === 'Official' ? '' : `<span class="badge">${esc(h.official || h.status || '')}</span>`}</div>
    <table><tbody>${h.competitors.map(c => `<tr class="${c.noc === 'KOR' ? 'kor' : ''}"><td class="num">${c.rank ?? '-'}</td>
      <td class="name">${name(c.name)} <span class="noc">${esc(c.noc)}</span></td><td class="num">${esc(c.time)}${c.status ? ' ' + esc(c.status) : ''}</td>
      <td class="q">${esc(c.qual)}</td></tr>`).join('')}</tbody></table></div>`;
}

function projection(p) {
  const kor = p.qualified.filter(c => c.noc === 'KOR').map(c => state.names[c.name] || c.name);
  const head = p.official_draw_published ? `${round(p.next)} 진출자 (공식 조 편성 발표됨)` : `${round(p.next)} 예상 대진 <span class="badge proj">예상</span>`;
  return `<div class="proj"><div class="ph">${head}</div>
    <div class="small muted">진출 ${p.qualified.length}명${kor.length ? ` · 한국 ${kor.length}명: ${esc(kor.join(', '))}` : ''}</div>
    ${p.official_draw_published ? '' : `<div class="bracket">${p.races.map((r, i) => `<div class="race"><b>${i + 1}조 (예상)</b><br>${r.map(x => x.includes('(KOR)') ? `<b>${esc(x)}</b>` : esc(x)).join('<br>')}</div>`).join('')}</div>
    <div class="small muted" style="margin-top:4px">순위→기록 순으로 정렬해 지그재그로 배정한 참고용입니다. 실제 조 편성은 ISU 배정표를 따릅니다.</div>`}</div>`;
}

function shortTrack(d) {
  const dists = Object.values(d.results || {});
  if (!dists.length) return '<p class="muted">아직 결과가 없습니다.</p>';
  return dists.map(dist => {
    const hasKor = dist.rounds.some(r => r.heats.some(h => h.competitors.some(c => c.noc === 'KOR')));
    const live = dist.rounds.some(r => r.status === 'Live');
    const last = [...dist.rounds].reverse().find(r => r.heats.length);
    return `<details class="dist" ${live || hasKor ? 'open' : ''}><summary>${esc(title(dist.title))} ${live ? BADGE.live : ''}${hasKor ? ' 🇰🇷' : ''}
      <span class="muted small">${last ? '최근: ' + esc(round(last.name)) : '시작 전'}</span></summary><div class="body">${
      dist.rounds.filter(r => r.heats.length || r.status !== 'Scheduled').reverse().map(r => `<div class="round"><div class="rh"><b>${esc(round(r.name))}</b>
        ${r.status === 'Live' ? BADGE.live : `<span class="badge">${esc(r.status)}</span>`} <span class="small muted">${r.start_utc ? kstDay(r.start_utc) + ' ' + kstTime(r.start_utc) : ''}</span></div>
        ${r.rule ? `<div class="rule">진출 규칙: ${esc(r.rule)}</div>` : ''}
        <div class="heats">${r.heats.map(heatTable).join('')}</div>${r.projection ? projection(r.projection) : ''}</div>`).join('')
      }${dist.rounds.filter(r => r.status === 'Scheduled' && !r.heats.length).length ? `<div class="round small muted">예정 라운드: ${dist.rounds.filter(r => r.status === 'Scheduled' && !r.heats.length).map(r => esc(round(r.name))).join(' → ')}</div>` : ''}</div></details>`;
  }).join('');
}

function speedRaces(d) {
  const races = Object.values(d.results || {});
  if (!races.length) return '<p class="muted">아직 결과가 없습니다.</p>';
  return races.map(r => {
    const hasKor = r.rows.some(x => x.noc === 'KOR');
    return `<details class="dist" ${r.live || hasKor ? 'open' : ''}><summary>${esc(r.title)} ${r.live ? BADGE.live : ''}${hasKor ? ' 🇰🇷' : ''}
      <span class="muted small">${r.start_utc ? kstDay(r.start_utc) + ' ' + kstTime(r.start_utc) : ''}</span></summary><div class="body tablewrap">
      <table><thead><tr><th class="num">순위</th><th>선수</th><th class="num">기록</th><th class="num">차이</th><th>조·레인</th></tr></thead><tbody>${
      r.rows.map(x => `<tr class="${x.noc === 'KOR' ? 'kor' : ''}"><td class="num">${x.rank ?? '-'}</td><td class="name">${name(x.name)} <span class="noc">${esc(x.noc)}</span></td>
        <td class="num">${esc(x.time)}</td><td class="num">${x.behind && x.behind !== '0.000' ? '+' + esc(x.behind) : ''}</td><td class="small muted">${x.pair ?? ''} ${esc(x.lane || '')}</td></tr>`).join('')
      }</tbody></table></div></details>`;
  }).join('');
}

async function viewEvent() {
  const e = allEvents().find(x => x.id === state.event);
  if (!e) return '<div class="empty">대회를 찾을 수 없습니다.</div>';
  const d = await loadEvent(e.id, true);
  let h = `<div class="sport ${e.sport}">${SPORTS[e.sport]} ${BADGE[phase(e)]}</div><h2 style="margin-top:4px">${esc(e.name)}</h2>
    <p class="muted">${fmtRange(e.start, e.end)} · ${esc(e.city)} (${esc(e.country)}) · <a href="${esc(e.url)}" target="_blank" rel="noopener">공식 페이지 ↗</a>${d?.checked_at ? ` · 수집 ${ago(d.checked_at)}` : ''}</p>`;
  if (!d) return h + '<div class="card muted">이 대회의 상세 일정·결과는 아직 수집되지 않았습니다. 대회 하루 전부터 자동 수집합니다.</div>';
  if (d.korea?.length) h += `<h2>🇰🇷 한국 선수</h2>${koreaTable(d.korea.slice().sort((a, b) => (b.start_utc || '').localeCompare(a.start_utc || '')), false)}`;
  if (e.sport === 'short-track') h += '<h2>종목별 결과 · 대진</h2>' + shortTrack(d);
  if (e.sport === 'speed-skating') h += '<h2>경기 결과</h2>' + speedRaces(d);
  if (d.sessions?.length) h += '<h2>경기 일정 (KST)</h2>' + sessionsTable(d);
  return h;
}

async function viewColumns() {
  const cols = state.columns.filter(c => !state.sport || c.sport === state.sport);
  if (!cols.length) return '<div class="empty">아직 작성된 칼럼이 없습니다. 한국 선수 결과가 들어오면 AI가 자동으로 정리합니다.</div>';
  const id = state.column || cols[0].id;
  let body = '';
  try {
    const c = await getJSON(`columns/${id}.json`);
    body = `<article class="card column"><div class="sport ${c.sport}">${SPORTS[c.sport] || ''} · ${esc(c.event)} · ${esc(c.day)}</div>
      <h2 style="margin:6px 0">${esc(c.title)}</h2><p class="muted">${esc(c.summary)}</p>
      ${c.body.split(/\n\s*\n/).map(p => `<p>${esc(p)}</p>`).join('')}
      <p class="small muted">🤖 수집된 공식 기록을 바탕으로 AI(Claude)가 자동 작성한 글입니다 · ${kstDay(c.generated_at)} ${kstTime(c.generated_at)} 작성 · 기록은 <a href="#tab=event&e=${encodeURIComponent(c.event_id)}">대회 상세</a>에서 확인하세요.</p></article>`;
  } catch { body = '<div class="card muted">칼럼을 불러오지 못했습니다.</div>'; }
  return body + '<h3>전체 칼럼</h3>' + cols.map(c => `<a class="ev" style="margin-bottom:8px" href="#tab=columns&c=${encodeURIComponent(c.id)}"><div class="sport ${c.sport}">${SPORTS[c.sport] || ''} · ${esc(c.day)}</div><div class="t">${esc(c.title)}</div><div class="m">${esc(c.summary)}</div></a>`).join('');
}

function viewStatus() {
  const s = state.status;
  if (!s) return '<div class="empty">상태 정보가 없습니다.</div>';
  const rows = Object.entries(s.sources).sort();
  const bad = rows.filter(([, v]) => !v.ok);
  return `<p>마지막 실행: ${kstDay(s.updated_at)} ${kstTime(s.updated_at)} (${ago(s.updated_at)}) · 모드 ${esc(s.mode)} · 실패 ${bad.length}건</p>
    <div class="tablewrap"><table><thead><tr><th>수집 대상</th><th>상태</th><th>시각</th><th>오류</th></tr></thead><tbody>${rows.map(([k, v]) =>
      `<tr><td>${esc(k)}</td><td class="${v.ok ? 'status-ok' : 'status-bad'}">${v.ok ? '정상' : '실패'}</td><td class="small">${ago(v.at)}</td><td class="small muted">${esc(v.error || '')}</td></tr>`).join('')}</tbody></table></div>`;
}

// ---------- routing ----------
function readHash() {
  const p = new URLSearchParams(location.hash.slice(1));
  state.tab = p.get('tab') || 'now'; state.event = p.get('e'); state.column = p.get('c'); state.sport = p.get('sport') || '';
}
function writeHash() {
  const p = new URLSearchParams();
  if (state.tab !== 'now') p.set('tab', state.tab);
  if (state.tab === 'event' && state.event) p.set('e', state.event);
  if (state.tab === 'columns' && state.column) p.set('c', state.column);
  if (state.sport) p.set('sport', state.sport);
  history.replaceState(null, '', p.toString() ? '#' + p : location.pathname);
}
let rendering = 0;
async function render() {
  const n = ++rendering;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('on', t.dataset.tab === state.tab));
  document.querySelectorAll('[data-sport]').forEach(c => c.classList.toggle('on', c.dataset.sport === state.sport));
  $('#eventTab').hidden = !state.event;
  const html = await ({ now: viewNow, calendar: viewCalendar, korea: viewKorea, event: viewEvent, columns: viewColumns, status: viewStatus }[state.tab] || viewNow)();
  if (n !== rendering) return;
  const open = [...document.querySelectorAll('details.dist')].map(d => d.open);
  $('#view').innerHTML = html;
  if (state.keepOpen) document.querySelectorAll('details.dist').forEach((d, i) => { if (i < open.length) d.open = open[i]; });
  state.keepOpen = false;
}
document.addEventListener('click', e => {
  const t = e.target.closest('[data-tab]'); if (t) { state.tab = t.dataset.tab; writeHash(); render(); return; }
  const s = e.target.closest('[data-sport]'); if (s) { state.sport = s.dataset.sport; writeHash(); render(); return; }
  const a = e.target.closest('[data-athlete]'); if (a) { $('#q').value = state.q = a.dataset.athlete; render(); }
});
$('#q').addEventListener('input', e => { state.q = e.target.value; render(); });
window.addEventListener('hashchange', () => { readHash(); render(); });

(async function main() {
  readHash();
  try { await loadAll(); } catch (err) { $('#view').innerHTML = `<div class="empty">자료를 불러오지 못했습니다: ${esc(err.message)}</div>`; return; }
  render();
  setInterval(async () => {
    if (document.hidden) return;
    try { await loadAll(); state.events = {}; state.keepOpen = true; render(); } catch { /* keep last view */ }
  }, 60000);
})();
