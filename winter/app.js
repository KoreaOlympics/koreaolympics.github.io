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

function heatTable(h, q = '') {
  return `<div class="heat"><div class="hn">${esc(h.name.replace('Heat', '조'))} ${h.official === 'Official' ? '' : `<span class="badge">${esc(h.official || h.status || '')}</span>`}</div>
    <table><tbody>${h.competitors.map(c => `<tr class="${c.noc === 'KOR' ? 'kor' : ''}${q && [c.name, state.names[c.name], c.noc].join(' ').toLowerCase().includes(q) ? ' hit' : ''}"><td class="num">${c.rank ?? '-'}</td>
      <td class="name">${name(c.name)} <span class="noc">${esc(c.noc)}</span></td><td class="num">${esc(c.time)}${c.status ? ' ' + esc(c.status) : ''}</td>
      <td class="q">${esc(c.qual)}</td></tr>`).join('')}</tbody></table></div>`;
}

function projection(p) {
  const kor = p.qualified.filter(c => c.noc === 'KOR').map(c => state.names[c.name] || c.name);
  const head = p.official_draw_published ? `${round(p.next)} 진출자 (공식 조 편성 발표됨)` : `${round(p.next)} 예상 대진 <span class="badge proj">예상</span>`;
  return `<div class="proj"><div class="ph">${head}</div>
    <div class="small muted">진출 ${p.qualified.length}명${kor.length ? ` · 한국 ${kor.length}명: ${esc(kor.join(', '))}` : ''}</div>
    ${p.pending?.length ? `<div class="small" style="color:var(--proj)">${esc(p.pending.map(round).join(', '))} 결과가 아직 반영되지 않아 진출자 일부만 배정했습니다.</div>` : ''}
    ${p.official_draw_published ? '' : `<div class="bracket">${p.races.map((r, i) => `<div class="race"><b>${i + 1}조 (예상)</b><br>${r.map(x => x.includes('(KOR)') ? `<b>${esc(x)}</b>` : esc(x)).join('<br>')}</div>`).join('')}</div>
    <div class="small muted" style="margin-top:4px">조 수는 이 라운드가 이번 시즌 실제로 열린 조 수(없으면 규정상 조 수)를 따르고, 선수는 순위→기록 순 지그재그로 배정한 참고용입니다. 실제 조 편성은 ISU 배정표를 따릅니다.</div>`}</div>`;
}

// ---------- event detail ----------
// URL: #tab=event&e=<id>&v=summary|results|schedule&d=<event_result_id>&r=<round id>
const GENDERS = [['Women', '여자'], ['Men', '남자'], ['Mixed', '혼성']];
const gender = t => /^Women|Women\b|Ladies/.test(t) ? 'Women' : /^Men|\bMen\b/.test(t) ? 'Men' : 'Mixed';
const distKey = t => (/relay/i.test(t) ? 1e5 : 0) + (parseInt((t.match(/(\d+)\s*m\b/) || [])[1], 10) || 9e4);
const byDist = (a, b) => distKey(a.title) - distKey(b.title);
const gIdx = t => ['Women', 'Men', 'Mixed'].indexOf(gender(t));
const byGenderDist = (a, b) => gIdx(a.title) - gIdx(b.title) || byDist(a, b);
const ST_ROWS = ['Women 500 m', 'Women 1000 m', 'Women 1500 m', 'Women 3000 m Relay', 'Men 500 m', 'Men 1000 m', 'Men 1500 m', 'Men 5000 m Relay', 'Mixed Team Relay'];
const withStRows = items => [...items, ...ST_ROWS.filter(t => !items.some(x => x.title === t)).map(t => ({ title: t, podium: null }))];
const isFinal = n => n === 'Finals' || n === 'Final A' || n === 'Final';
const evLink = (extra) => '#' + new URLSearchParams({ tab: 'event', e: state.event, ...extra });
const medalCell = p => p ? `<td class="medal-name">${name(p.name)} <span class="noc">${esc(p.noc)}</span></td><td class="num small">${esc(p.time)}</td>` : '<td></td><td></td>';

// The shape on the Namu/Wikipedia season articles: one table per gender, a row per distance, gold/silver/bronze columns.
function medalTables(items, { byGender = true } = {}) {
  items = items.slice().sort(byDist);
  const groups = byGender ? GENDERS.map(([g, ko]) => [ko, items.filter(x => gender(x.title) === g)]) : [['종목', items]];
  return groups.filter(([, xs]) => xs.length).map(([label, xs]) => `<div class="tablewrap"><table class="medals">
    <thead><tr><th>${label}</th><th colspan="2" class="g">금</th><th colspan="2" class="s">은</th><th colspan="2" class="b">동</th></tr></thead><tbody>${
    xs.map(x => `<tr><th>${esc(title(x.title).replace(/^(남자|여자) /, ''))}</th>${[1, 2, 3].map(rk => medalCell((x.podium || []).find(p => p.rank === rk))).join('')}</tr>`).join('')
  }</tbody></table></div>`).join('');
}

function stPodium(dist) {
  for (const r of dist.rounds) {
    if (!isFinal(r.name)) continue;
    for (const h of r.heats) {
      if (['Final', 'Final A'].includes(h.name) && (h.status === 'Finished' || h.official === 'Official')) {
        const top = h.competitors.filter(c => [1, 2, 3].includes(c.rank));
        if (top.length) return top;
      }
    }
  }
  return null;
}
function fsPodium(cat) {
  const done = cat.rows.length && Object.values(cat.rows[0].segments).every(s => s.status === 'Finished');
  return done ? cat.rows.filter(r => [1, 2, 3].includes(r.rank)).map(r => ({ ...r, time: r.points })) : null;
}
function ssPodium(race) {
  if (!['A', null, undefined, ''].includes(race.division) || !race.official) return null;
  const top = race.rows.filter(r => [1, 2, 3].includes(r.rank));
  return top.length ? top : null;
}

// furthest round each Korean skater reached per distance
function koreaMatrix(d) {
  const dists = Object.entries(d.results || {}).sort((a, b) => byGenderDist(a[1], b[1]));
  const who = new Map();
  for (const [rid, dist] of dists) {
    for (const r of dist.rounds) for (const h of r.heats) for (const c of h.competitors) {
      if (c.noc !== 'KOR') continue;
      const row = who.get(c.name) || {};
      if (row[rid] && (row[rid].start || '') > (r.start_utc || '')) continue;
      row[rid] = { start: r.start_utc, round: r.name, heat: h.name, rank: c.rank, time: c.time, qual: c.qual, status: c.status, r: r.id };
      who.set(c.name, row);
    }
  }
  if (!who.size) return '';
  const used = dists.filter(([rid]) => [...who.values()].some(x => x[rid]));
  return `<h3>🇰🇷 한국 선수 진행 현황</h3><p class="small muted">종목별로 가장 마지막에 출전한 라운드 · 칸을 누르면 그 라운드 결과로 이동</p>
    <div class="tablewrap"><table class="matrix"><thead><tr><th>선수</th>${used.map(([, x]) => `<th>${esc(title(x.title))}</th>`).join('')}</tr></thead><tbody>${
    [...who.entries()].map(([n, row]) => `<tr><td class="name">${name(n)}</td>${used.map(([rid]) => {
      const x = row[rid];
      if (!x) return '<td class="muted">–</td>';
      const medal = isFinal(x.round) && x.heat !== 'Final B' && [1, 2, 3].includes(x.rank) ? ['', '🥇', '🥈', '🥉'][x.rank] : '';
      const res = x.rank == null && (!x.time || x.time === 'no time') && !x.status ? '출전 예정' : `${x.rank ?? '-'}위 ${esc(x.time)} <b class="q">${esc(x.qual)}</b>${x.status ? ' ' + esc(x.status) : ''}`;
      return `<td><a href="${evLink({ v: 'results', d: rid, r: x.r })}">${medal}${esc(round(x.round))}${x.heat === 'Final B' ? ' B' : ''}<br><span class="small">${res}</span></a></td>`;
    }).join('')}</tr>`).join('')
  }</tbody></table></div>`;
}

function stSummary(d) {
  const items = withStRows(Object.values(d.results || {}).map(x => ({ title: x.title, podium: stPodium(x) })));
  return '<h3>메달리스트</h3>' + medalTables(items) + koreaMatrix(d);
}

function distChips(d, current, link = rid => evLink({ v: 'results', d: rid })) {
  const entries = Object.entries(d.results || {});
  return GENDERS.map(([g, ko]) => {
    const xs = entries.filter(([, x]) => gender(x.title) === g).sort((a, b) => byDist(a[1], b[1]));
    if (!xs.length) return '';
    return `<div class="chiprow"><span class="lbl">${ko}</span>${xs.map(([rid, x]) => {
      const live = (x.rounds || []).some(r => r.status === 'Live');
      const kor = (x.rounds || []).some(r => r.heats.some(h => h.competitors.some(c => c.noc === 'KOR'))) || (x.rows || []).some(c => c.noc === 'KOR');
      return `<a class="chip ${rid === current ? 'on' : ''}" href="${link(rid)}">${esc(title(x.title).replace(/^(남자|여자) /, ''))}${live ? ' 🔴' : ''}${kor ? ' 🇰🇷' : ''}</a>`;
    }).join('')}</div>`;
  }).join('');
}

function stResults(d) {
  const entries = Object.entries(d.results || {});
  if (!entries.length) return '<p class="muted">아직 결과가 없습니다.</p>';
  const rid = state.d && d.results[state.d] ? state.d : (entries.find(([, x]) => x.rounds.some(r => r.status === 'Live')) || entries[0])[0];
  const dist = d.results[rid];
  const rounds = dist.rounds.slice().sort((a, b) => (a.start_utc || '9').localeCompare(b.start_utc || '9'));
  const withData = rounds.filter(r => r.heats.length);
  const cur = rounds.find(r => String(r.id) === state.r) || withData.find(r => r.status === 'Live') || withData[withData.length - 1] || rounds[0];
  const q = (state.eq || '').trim().toLowerCase();
  const heatMatch = h => (!state.onlyKor || h.competitors.some(c => c.noc === 'KOR')) &&
    (!q || h.competitors.some(c => [c.name, state.names[c.name], c.noc].join(' ').toLowerCase().includes(q)));
  const heats = cur.heats.filter(heatMatch);
  return distChips(d, rid) +
    `<div class="rounds">${rounds.map(r => `<a class="rstep ${r === cur ? 'on' : ''} st-${(r.status || '').toLowerCase()}" href="${evLink({ v: 'results', d: rid, r: r.id })}">${esc(round(r.name))}<span>${r.status === 'Live' ? 'LIVE' : r.status === 'Finished' ? '종료' : r.start_utc ? kstDay(r.start_utc) : '예정'}</span></a>`).join('<i>›</i>')}</div>
    <div class="roundhead"><h3>${esc(title(dist.title))} · ${esc(round(cur.name))}</h3>
      <span class="small muted">${cur.start_utc ? kstDay(cur.start_utc) + ' ' + kstTime(cur.start_utc) + ' KST' : ''}</span>
      <label class="toggle"><input type="checkbox" id="onlyKor" ${state.onlyKor ? 'checked' : ''}> 한국 선수 조만</label>
      <input type="search" id="eq" placeholder="이 종목에서 선수·국가 찾기" value="${esc(state.eq || '')}"></div>
    ${cur.rule ? `<div class="rule">진출 규칙: ${esc(cur.rule)}</div>` : ''}
    ${cur.heats.length ? (heats.length ? `<div class="heats">${heats.map(h => heatTable(h, q)).join('')}</div>` : '<p class="muted">조건에 맞는 조가 없습니다.</p>') : '<p class="muted">아직 결과가 없습니다.</p>'}
    ${cur.projection ? projection(cur.projection) : ''}`;
}

function fsTable(cat) {
  const segs = cat.segments || [];
  const SEG = { SP: '쇼트', FS: '프리', RD: '리듬', FD: '프리 댄스' };
  return `<div class="tablewrap"><table><thead><tr><th class="num">순위</th><th>선수</th>${segs.map(s => `<th class="num">${SEG[s] || esc(s)}</th>`).join('')}<th class="num">총점</th></tr></thead><tbody>${
    cat.rows.map(r => `<tr class="${r.noc === 'KOR' ? 'kor' : ''}"><td class="num">${r.rank ?? '-'}</td><td class="name">${name(r.name)} <span class="noc">${esc(r.noc)}</span></td>${
      segs.map(s => { const x = r.segments[s] || {}; return `<td class="num">${esc(x.total || '')}${x.rank ? ` <span class="small muted">(${x.rank})</span>` : ''}${x.tes ? `<br><span class="small muted">TES ${esc(x.tes)} · PCS ${esc(x.pcs)}</span>` : ''}</td>`; }).join('')
    }<td class="num"><b>${esc(r.points)}</b></td></tr>`).join('')}</tbody></table></div>`;
}
function fsResults(d) {
  const entries = Object.entries(d.results || {});
  if (!entries.length) return '<p class="muted">아직 결과가 없습니다.</p>';
  const rid = state.d && d.results[state.d] ? state.d : entries[0][0];
  return `<div class="chiprow">${entries.map(([k, x]) => `<a class="chip ${k === rid ? 'on' : ''}" href="${evLink({ v: 'results', d: k })}">${esc(title(x.title))}${x.rows.some(r => r.noc === 'KOR') ? ' 🇰🇷' : ''}</a>`).join('')}</div>
    <h3>${esc(title(d.results[rid].title))}</h3>${fsTable(d.results[rid])}`;
}
function fsSummary(d) {
  const items = Object.values(d.results || {}).map(x => ({ title: x.title, podium: fsPodium(x) }));
  const kor = Object.values(d.results || {}).flatMap(x => x.rows.filter(r => r.noc === 'KOR').map(r => ({ ...r, cat: x.title })));
  return '<h3>메달리스트</h3>' + medalTables(items, { byGender: false }) +
    (kor.length ? `<h3>🇰🇷 한국 선수</h3><div class="tablewrap"><table><thead><tr><th>종목</th><th>선수</th><th class="num">순위</th><th class="num">총점</th></tr></thead><tbody>${
      kor.map(r => `<tr class="kor"><td><a href="${evLink({ v: 'results', d: Object.keys(d.results).find(k => d.results[k].title === r.cat) })}">${esc(title(r.cat))}</a></td><td class="name">${name(r.name)}</td><td class="num">${r.rank ?? '-'}</td><td class="num">${esc(r.points)}</td></tr>`).join('')}</tbody></table></div>` : '');
}

function ssResults(d) {
  const entries = Object.entries(d.results || {});
  if (!entries.length) return '<p class="muted">아직 결과가 없습니다.</p>';
  const rid = state.d && d.results[state.d] ? state.d : entries[0][0];
  return distChips(d, rid) + `<h3>${esc(d.results[rid].title)}</h3>` + ssTable(d.results[rid]);
}
function ssTable(r) {
  return `<div class="tablewrap"><table><thead><tr><th class="num">순위</th><th>선수</th><th class="num">기록</th><th class="num">차이</th><th>조·레인</th></tr></thead><tbody>${
    r.rows.map(x => `<tr class="${x.noc === 'KOR' ? 'kor' : ''}"><td class="num">${x.rank ?? '-'}</td><td class="name">${name(x.name)} <span class="noc">${esc(x.noc)}</span></td>
      <td class="num">${esc(x.time)}</td><td class="num">${x.behind && x.behind !== '0.000' ? '+' + esc(x.behind) : ''}</td><td class="small muted">${x.pair ?? ''} ${esc(x.lane || '')}</td></tr>`).join('')}</tbody></table></div>`;
}
function ssSummary(d) {
  const items = Object.values(d.results || {}).filter(x => ['A', null, undefined, ''].includes(x.division)).map(x => ({ title: x.title.replace(/\s*Division A/, ''), podium: ssPodium(x) }));
  return '<h3>메달리스트 (디비전 A)</h3>' + (items.length ? medalTables(items) : '<p class="muted">아직 결과가 없습니다.</p>');
}

async function viewEvent() {
  const d = await loadEvent(state.event, true);
  const e = allEvents().find(x => x.id === state.event) || d?.event;  // the calendar can briefly miss an event the source dropped
  if (!e) return '<div class="empty">대회를 찾을 수 없습니다.</div>';
  const v = state.v || (phase(e) === 'live' && e.sport === 'short-track' ? 'results' : 'summary');
  let h = `<div class="sport ${e.sport}">${SPORTS[e.sport]} ${BADGE[phase(e)]}</div><h2 style="margin-top:4px">${esc(e.name)}</h2>
    <p class="muted">${fmtRange(e.start, e.end)} · ${esc(e.city)} (${esc(e.country)}) · <a href="${esc(e.url)}" target="_blank" rel="noopener">공식 페이지 ↗</a>${d?.checked_at ? ` · 수집 ${ago(d.checked_at)}` : ''}</p>`;
  if (!d) return h + '<div class="card muted">이 대회의 상세 일정·결과는 아직 수집되지 않았습니다. 대회 하루 전부터 자동 수집합니다.</div>';
  h += `<nav class="subtabs">${[['summary', '요약'], ['results', '종목별 결과'], ['schedule', '경기 일정']].map(([k, l]) => `<a class="${k === v ? 'on' : ''}" href="${evLink({ v: k })}">${l}</a>`).join('')}</nav>`;
  const fn = {
    'short-track': { summary: stSummary, results: stResults },
    'figure-skating': { summary: fsSummary, results: fsResults },
    'speed-skating': { summary: ssSummary, results: ssResults },
  }[e.sport] || {};
  if (v === 'schedule') return h + (sessionsTable(d) || '<p class="muted">일정 자료가 없습니다.</p>');
  return h + (fn[v] ? fn[v](d) : '<p class="muted">결과 자료가 없습니다.</p>');
}


// ---------- 종목별 (기본 탭): 종목 → 대회 → 세부종목 → 그 세부종목의 모든 라운드·조를 아래로 펼친다 ----------
// URL: #sport=<sport>&e=<event id>&d=<result key>
const evLabel = e => e.name.replace(/^ISU (CNSG )?/, '').replace(/(^| )(Speed Skating|Short Track|Figure Skating)( |$)/g, '$1').replace(/ 20\d\d$/, '')
  .replace(/^World Tour #(\d+)$/, '월드투어 $1차').replace(/^World Cup #(\d+)$/, '월드컵 $1차').replace(/^Junior World Cup #(\d+)$/, '주니어 월드컵 $1차')
  .replace(/^Junior Grand Prix /, '주니어 그랑프리 ').replace(/^Grand Prix /, '그랑프리 ').replace(/^World Championships$/, '세계선수권')
  .replace(/^Junior World Championships$/, '세계주니어선수권').replace(/^Four Continents Championships$/, '4대륙선수권')
  .replace(/^European Championships$/, '유럽선수권').replace(/^Grand Prix Final$/, '그랑프리 파이널').replace(/^World Figure Skating Team Trophy$/, '월드 팀 트로피');
const isJunior = e => /Junior/.test(e.category || '') || /Junior/.test(e.name);
const browseLink = (extra = {}) => '#' + new URLSearchParams(Object.fromEntries(Object.entries(extra).filter(([, v]) => v)));

function viewBrowse() {
  const evs = allEvents();
  const bar = `<nav class="sportbar">${Object.entries(SPORTS).map(([k, ko]) => {
    const live = evs.filter(e => e.sport === k && phase(e) === 'live').length;
    return `<a class="sportbtn ${k} ${k === state.sport ? 'on' : ''}" href="${browseLink(k === state.sport ? {} : { sport: k })}">${ko}${live ? ' <span class="badge live">LIVE</span>' : ''}</a>`;
  }).join('')}</nav>`;
  if (!state.sport || !SPORTS[state.sport]) return Promise.resolve(bar + '<div class="empty">종목을 누르면 이번 시즌 대회가 펼쳐집니다.</div>');
  return sportPanel(evs.filter(e => e.sport === state.sport)).then(h => bar + h);
}

async function sportPanel(evs) {
  if (!evs.length) return '<div class="empty">이 종목의 이번 시즌 일정이 아직 없습니다.</div>';
  let h = '';
  for (const [label, xs] of [['시니어', evs.filter(e => !isJunior(e))], ['주니어', evs.filter(isJunior)]]) {
    if (!xs.length) continue;
    h += `<h3>${label} <span class="muted small">${xs.length}개 대회</span></h3><div class="evlist">`;
    for (const e of xs) {
      const open = e.id === state.event;
      h += `<a class="evrow ${open ? 'on' : ''}" href="${browseLink({ sport: state.sport, e: open ? '' : e.id })}">
        <span class="lbl">${esc(evLabel(e))}</span><span class="m">${fmtRange(e.start, e.end)} · ${esc(e.city)}${e.country ? ' (' + esc(e.country) + ')' : ''}</span>${BADGE[phase(e)]}</a>`;
      if (open) h += `<div class="evbody">${await eventBody(e)}</div>`;
    }
    h += '</div>';
  }
  return h;
}

async function eventBody(e) {
  const d = await loadEvent(e.id);
  const official = e.url ? ` · <a href="${esc(e.url)}" target="_blank" rel="noopener">공식 페이지 ↗</a>` : '';
  if (!d) return `<p class="muted">상세 일정·결과가 아직 수집되지 않았습니다. 대회 하루 전부터 자동 수집합니다.${official}</p>`;
  const entries = Object.entries(d.results || {});
  let h = `<p class="small muted">${d.checked_at ? `수집 ${ago(d.checked_at)}` : ''}${official} · <a href="#tab=event&e=${encodeURIComponent(e.id)}">대회 상세 화면 →</a></p>`;
  if (!entries.length) return h + (sessionsTable(d) || '<p class="muted">아직 결과가 없습니다.</p>');
  const rid = state.d && d.results[state.d] ? state.d : null;
  h += distChips(d, rid, k => browseLink({ sport: state.sport, e: e.id, d: k === rid ? '' : k }));
  if (!rid) {
    const sum = { 'short-track': stSummary, 'figure-skating': fsSummary, 'speed-skating': ssSummary }[e.sport];
    return h + '<p class="small muted">세부종목을 누르면 모든 라운드·조 결과가 아래에 펼쳐집니다.</p>' + (sum ? sum(d) : '');
  }
  const x = d.results[rid];
  h += `<h3>${esc(title(x.title))}</h3>`;
  if (e.sport === 'short-track') return h + stAll(x);
  if (e.sport === 'figure-skating') return h + fsTable(x);
  return h + ssTable(x);
}

// every round of one short-track distance, in race order, heats and projected draws included
function stAll(dist) {
  const rounds = dist.rounds.slice().sort((a, b) => (a.start_utc || '9').localeCompare(b.start_utc || '9'));
  if (!rounds.length) return '<p class="muted">아직 라운드 정보가 없습니다.</p>';
  return rounds.map(r => {
    const st = r.status === 'Live' ? '<span class="badge live">LIVE</span>' : r.status === 'Finished' ? '<span class="badge done">종료</span>' : '<span class="badge soon">예정</span>';
    return `<section class="roundblock"><div class="roundhead"><h4>${esc(round(r.name))}</h4>${st}<span class="small muted">${r.start_utc ? kstDay(r.start_utc) + ' ' + kstTime(r.start_utc) + ' KST' : ''}</span></div>
      ${r.rule ? `<div class="rule">진출 규칙: ${esc(r.rule)}</div>` : ''}
      ${r.heats.length ? `<div class="heats">${r.heats.map(hh => heatTable(hh)).join('')}</div>` : '<p class="small muted">아직 결과가 없습니다.</p>'}
      ${r.projection ? projection(r.projection) : ''}</section>`;
  }).join('');
}

// ---------- season summary (Wikipedia / Namu season-article layout) ----------
async function viewSeason() {
  const sport = ['short-track', 'speed-skating', 'figure-skating'].includes(state.sport) ? state.sport : 'short-track';
  let s;
  try { s = await getJSON(`season-${sport}.json`); } catch { return '<div class="empty">시즌 정리 자료가 아직 없습니다.</div>'; }
  const evs = s.events.filter(e => sport !== 'figure-skating' || !/Junior/.test(e.category || e.name));
  const label = evLabel;
  let h = `<h2>${s.season} ${SPORTS[sport]} 시즌</h2>`;
  if (!state.sport) h += '<p class="small muted">위의 종목 버튼으로 쇼트트랙·스피드·피겨 시즌을 바꿔 볼 수 있습니다.</p>';
  h += `<h3>대회 일정</h3><div class="tablewrap"><table><thead><tr><th>기간</th><th>대회</th><th>개최지</th><th>상태</th></tr></thead><tbody>${
    evs.map(e => `<tr><td class="num">${fmtRange(e.start, e.end)}</td><td><a href="#tab=event&e=${encodeURIComponent(e.id)}">${esc(label(e))}</a></td><td>${esc(e.city)} (${esc(e.country)})</td><td>${BADGE[phase(e)]}</td></tr>`).join('')}</tbody></table></div>`;
  const played = evs.filter(e => e.podiums.length && phase(e) !== 'soon');
  h += '<h3>대회별 메달리스트</h3>' + (played.length ? played.map(e =>
    `<h4><a href="#tab=event&e=${encodeURIComponent(e.id)}">${esc(label(e))}</a>: ${esc(e.city)} <span class="muted small">${fmtRange(e.start, e.end)}</span></h4>` +
    medalTables(sport === 'short-track' ? withStRows(e.podiums) : e.podiums, { byGender: sport !== 'figure-skating' })).join('') : '<p class="muted">아직 시작된 대회가 없습니다.</p>');
  if (s.medals.length) h += `<h3>국가별 메달 집계</h3><div class="tablewrap"><table class="narrow"><thead><tr><th>국가</th><th class="num">금</th><th class="num">은</th><th class="num">동</th><th class="num">합계</th></tr></thead><tbody>${
    s.medals.map(([noc, g, sv, b, t]) => `<tr class="${noc === 'KOR' ? 'kor' : ''}"><td><b>${esc(noc)}</b></td><td class="num">${g}</td><td class="num">${sv}</td><td class="num">${b}</td><td class="num">${t}</td></tr>`).join('')}</tbody></table></div>`;
  if (s.season_best) h += '<h3>시즌 최고점</h3>' + Object.entries(s.season_best).map(([cat, rows]) => `<h4>${esc(title(cat))}</h4><div class="tablewrap"><table class="narrow"><tbody>${
    rows.slice(0, 5).map((r, i) => `<tr class="${r.noc === 'KOR' ? 'kor' : ''}"><td class="num">${i + 1}</td><td class="name">${name(r.name)} <span class="noc">${esc(r.noc)}</span></td><td class="num">${r.points.toFixed(2)}</td><td class="small"><a href="#tab=event&e=${encodeURIComponent(r.event_id)}">${esc(label({ name: r.event }))}</a></td></tr>`).join('')}</tbody></table></div>`).join('');
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
  state.tab = p.get('tab') || 'browse'; state.event = p.get('e'); state.column = p.get('c'); state.v = p.get('v'); state.d = p.get('d'); state.r = p.get('r'); state.sport = p.get('sport') || '';
}
function writeHash() {
  const p = new URLSearchParams();
  if (state.tab !== 'browse') p.set('tab', state.tab);
  if (state.tab === 'browse' && state.event) { p.set('e', state.event); if (state.d) p.set('d', state.d); }
  if (state.tab === 'event' && state.event) { p.set('e', state.event); for (const k of ['v', 'd', 'r']) if (state[k]) p.set(k, state[k]); }
  if (state.tab === 'columns' && state.column) p.set('c', state.column);
  if (state.sport) p.set('sport', state.sport);
  history.replaceState(null, '', p.toString() ? '#' + p : location.pathname);
}
let rendering = 0;
async function render() {
  const n = ++rendering;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('on', t.dataset.tab === state.tab));
  document.querySelectorAll('[data-sport]').forEach(c => c.classList.toggle('on', c.dataset.sport === state.sport));
  $('#eventTab').hidden = !(state.tab === 'event' && state.event);
  $('#controls').hidden = state.tab === 'browse';
  const html = await ({ browse: viewBrowse, now: viewNow, calendar: viewCalendar, korea: viewKorea, event: viewEvent, season: viewSeason, columns: viewColumns, status: viewStatus }[state.tab] || viewBrowse)();
  if (n !== rendering) return;
  const open = [...document.querySelectorAll('details.dist')].map(d => d.open);
  $('#view').innerHTML = html;
  if (state.keepOpen) document.querySelectorAll('details.dist').forEach((d, i) => { if (i < open.length) d.open = open[i]; });
  state.keepOpen = false;
}
document.addEventListener('click', e => {
  const t = e.target.closest('[data-tab]'); if (t) { if (t.dataset.tab !== state.tab && t.dataset.tab !== 'event') state.event = state.d = null; state.tab = t.dataset.tab; writeHash(); render(); return; }
  const s = e.target.closest('[data-sport]'); if (s) { state.sport = s.dataset.sport; writeHash(); render(); return; }
  const a = e.target.closest('[data-athlete]'); if (a) { $('#q').value = state.q = a.dataset.athlete; render(); }
});
$('#q').addEventListener('input', e => { state.q = e.target.value; render(); });
document.addEventListener('change', e => { if (e.target.id === 'onlyKor') { state.onlyKor = e.target.checked; render(); } });
document.addEventListener('input', e => {
  if (e.target.id !== 'eq') return;
  state.eq = e.target.value; const pos = e.target.selectionStart;
  render().then(() => { const el = $('#eq'); if (el) { el.focus(); el.setSelectionRange(pos, pos); } });
});
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
