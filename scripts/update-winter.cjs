/* Public-source winter results. Node 22+, no dependencies. */
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'data/winter-live.json');
const SEASON = '2026/2027';
const stamp = () => new Date().toISOString();
function clean(s) {
  return String(s).replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]*>/g, ' ').replace(/&#(?:x([\da-f]+)|(\d+));/gi, (_, h, d) => String.fromCodePoint(parseInt(h || d, h ? 16 : 10)))
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/\s+/g, ' ').trim();
}
async function get(url) {
  const r = await fetch(url, {headers: {'User-Agent': 'KoreaOlympics/1.0 (+https://koreaolympics.github.io)'}, signal: AbortSignal.timeout(25000)});
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${new URL(url).hostname}`);
  return r.text();
}
function flight(html) {
  return [...html.matchAll(/self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)/g)].map(m => JSON.parse(m[1])).join('');
}
function arrayAt(s, key) {
  const marker = '"' + key + '":[';
  let p = s.indexOf(marker);
  if (p < 0) throw new Error('Source structure changed: ' + key);
  const start = p + marker.length - 1;
  let depth = 0, quoted = false, escape = false;
  for (let i = start; i < s.length; i++) {
    const c = s[i];
    if (quoted) { if (escape) escape = false; else if (c === '\\') escape = true; else if (c === '"') quoted = false; }
    else if (c === '"') quoted = true;
    else if (c === '[') depth++;
    else if (c === ']' && --depth === 0) return JSON.parse(s.slice(start, i + 1));
  }
  throw new Error('Incomplete source array');
}
function isuEvents(html, sport, lang = 'en') {
  const body = flight(html);
  const events = arrayAt(body, body.includes('"data":[') ? 'data' : 'initialData').filter(x => x.event_id && x.from_date);
  if (!events.length) throw new Error('Empty ISU events');
  return events.map(x => ({id: `isu-${x.event_id}`, sport, name: x.name, season: x.season,
    start: x.from_date.slice(0, 10), end: x.to_date.slice(0, 10), location: `${x.city} / ${x.country_code}`,
    url: `https://isu-skating.com/${lang}/${sport}/events/eventdetail/${x.slug}/`,
    results_url: (x.buttons || []).find(b => b.title === 'Detailed Results')?.url || '',
    source_state: x.state, source_updated_at: x.updated_at}));
}
function cells(row) { return [...row.matchAll(/<t[dh]\b[^>]*>([\s\S]*?)<\/t[dh]>/gi)].map(m => clean(m[1])); }
function tableRows(html) { return [...html.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)].map(m => cells(m[1])); }
async function collectISU(sport, lang) {
  const source = `https://isu-skating.com/${lang}/${sport}/events/`;
  const events = isuEvents(await get(source), sport, lang).filter(e => e.season === SEASON);
  if (!events.length) throw new Error('No events for selected season');
  const resultIndex = `https://isu-skating.com/${lang}/${sport}/results/`;
  const recent = isuEvents(await get(resultIndex), sport, lang).sort((a, b) => b.start.localeCompare(a.start));
  let results = [], note = '';
  const latest = recent[0];
  if (sport === 'figure-skating') {
    let url = latest.results_url;
    if (!url) {
      const detail = await get(latest.url);
      url = [...detail.matchAll(/href="(https:\/\/(?:results\.isu\.org|www\.isuresults\.com)\/results\/[^"?#]+\/)"/g)][0]?.[1];
    }
    if (!url) throw new Error('ISU detailed result URL absent');
    const index = await get(url);
    const links = [...index.matchAll(/href=["']?(CAT\d+RS\.htm)["'\s>]/gi)].map(m => m[1]);
    if (!links.length) throw new Error('ISU final tables absent');
    for (const link of [...new Set(links)].slice(0, 4)) {
      const resultUrl = new URL(link, url).href, h = await get(resultUrl);
      const title = clean(h.match(/<title>([\s\S]*?)<\/title>/i)?.[1] || latest.name);
      const flat = h.replace(/<table><tr[^>]*>([\s\S]*?)<\/tr><\/table>/gi, (_, inner) => clean(inner));
      const rows = tableRows(flat).filter(c => /^\d+$/.test(c[0]) && c.some(v => /^[A-Z]{3}$/.test(v)));
      for (const c of rows.filter(c => Number(c[0]) <= 3 || c.includes('KOR'))) {
        const ci = c.findIndex(v => /^[A-Z]{3}$/.test(v));
        results.push({event: latest.name, discipline: title.replace(latest.name, '').replace(/^\s*-\s*/, ''), date: latest.end,
          rank: c[0], athlete: c.slice(1, ci).join(' '), country: c[ci], score: c[ci + 1], details: c.slice(ci + 2).join(' / '), source: resultUrl});
      }
    }
    if (!results.length) throw new Error('No classified figure results');
    note = '최근 ISU 결과 목록의 첫 대회: 최종 종합 순위 상위 3위 및 한국 선수. SP/FS·RD/FD 순서는 원문 참조.';
  } else {
    // The official season awards article publishes all nine World Champions in plain HTML.
    const sourceUrl = 'https://www.isu-skating.com/en/short-track/news/celebrating-the-seasons-best-winners-of-the-first-ever-isu-short-track-skating-awards/';
    const text = clean(await get(sourceUrl));
    const block = text.slice(text.indexOf('World Champions', text.indexOf('Crystal Globe Winner')));
    const re = /-\s*((?:Women|Men)\s+\d+\s*m(?:\s+Relay)?|Mixed Team Relay)\s*-\s*(.*?)(?=\s*-\s*(?:Women|Men|Mixed)|Women 1000m|Most Improved|scan_to|$)/g;
    for (const m of block.matchAll(re)) {
      const winner = m[2].match(/^(.+?)(?:\s*\(([A-Z]{3})\)|$)/);
      if (winner) results.push({event: '2026 세계선수권', discipline: m[1], date: '2026-03-15', rank: '1',
        athlete: winner[1].trim(), country: winner[2] || '', score: '금메달', source: sourceUrl});
    }
    if (results.length !== 9) throw new Error(`Expected 9 world champions; got ${results.length}`);
    note = '2025–26 시즌 마지막 세계선수권 우승자 9개 종목. 경기별 실시간 순위·기록 수집은 아직 연결되지 않았으며 공식 결과 링크에서 확인할 수 있다.';
  }
  return {source, result_index: resultIndex, checked_at: stamp(), status: 'ok', events, results, recent: recent.slice(0, 8), note};
}
async function collectSpeed() {
  const source = 'https://speedskatingresults.com/';
  const events = isuEvents(await get('https://isu-skating.com/en/speed-skating/events/?season=2026%2F2027'), 'speed-skating').filter(e => e.season === SEASON);
  const results = [];
  for (const gender of ['f', 'm']) for (const distance of [500, 1000, 1500]) {
    const url = `${source}api/json/topn.php?gender=${gender}&season=2026&distance=${distance}&max=20`;
    const j = JSON.parse(await get(url));
    if (!Array.isArray(j.topn) || j.season !== 2026) throw new Error('Unexpected SpeedskatingResults API schema');
    for (const r of j.topn.filter(r => r.rank <= 3 || r.skater.country === 'KOR')) {
      results.push({event: r.event, discipline: `${gender === 'f' ? '여자' : '남자'} ${distance}m 시즌 최고기록`,
        date: r.date, rank: String(r.rank), athlete: [r.skater.givenname, r.skater.familyname].join(' '), country: r.skater.country,
        score: r.time, details: r.location, source: url});
    }
  }
  if (!results.length || !events.length) throw new Error('Empty speed data');
  return {source, checked_at: stamp(), status: 'ok', events, results, recent: [],
    note: '자료 제공: SpeedskatingResults.com 공개 API(비상업적 이용). 남녀 500·1000·1500m 시즌 상위 3명과 상위 20명에 든 한국 선수. 시즌 기록 순위이며 월드컵 포인트 순위가 아니다.'};
}
function curlingEvents(html) {
  const out = [];
  for (const m of html.matchAll(/<a href="(https:\/\/livescores\.worldcurling\.org\/[^"/]+)"[^>]*>([\s\S]*?)<\/a>/g)) {
    const h = m[2];
    const name = clean(h.match(/class="event-tile-title"[^>]*>([\s\S]*?)<\/div>/)?.[1] || '');
    const description = clean(h.match(/class="event-tile-dates"[^>]*>([\s\S]*?)<\/div>/)?.[1] || '');
    if (name && description) out.push({name, description, url: m[1]});
  }
  if (!out.length) throw new Error('Empty World Curling calendar');
  return out;
}
async function collectCurling() {
  const source = 'https://livescores.worldcurling.org/';
  const items = curlingEvents(await get(source));
  const today = new Date().toLocaleDateString('en-CA', {timeZone: 'Asia/Seoul'});
  const events = items.map(x => {
    const parts = x.description.split('|'), dates = (parts[1] || '').trim();
    const year = dates.match(/20\d{2}/)?.[0];
    const months = {Jan:'01',Feb:'02',Mar:'03',Apr:'04',May:'05',Jun:'06',Jul:'07',Aug:'08',Sep:'09',Oct:'10',Nov:'11',Dec:'12'};
    const a = dates.match(/([A-Z][a-z]{2})\s+(\d{1,2})/), b = dates.match(/-\s*(?:([A-Z][a-z]{2})\s+)?(\d{1,2})/);
    if (!a || !year) throw new Error('Unrecognised curling date: ' + dates);
    const start = `${year}-${months[a[1]]}-${a[2].padStart(2,'0')}`;
    const end = b ? `${year}-${months[b[1] || a[1]]}-${b[2].padStart(2,'0')}` : start;
    return {id: x.url.split('/').pop(), sport:'curling', name:x.name, start, end, location:parts[0].trim(), url:x.url};
  });
  const current = events.filter(e => e.start <= today).sort((a,b) => b.end.localeCompare(a.end)).slice(0, 2);
  const results = [];
  for (const e of current) {
    const url = `${e.url}/aspnet/standingsall.aspx?EventID=1`;
    const h = await get(e.url); let group = '';
    for (const c of tableRows(h)) {
      const text = c.join(' '), g = text.match(/Group\s+[A-Z]/);
      if (g) group = g[0];
      const ci = c.findIndex(v => /^[A-Z]{3}$/.test(v));
      if (ci >= 0 && /^\d+$/.test(c[ci+1]) && /^\d+$/.test(c[ci+2])) {
        results.push({event:e.name, discipline:group || '라운드로빈', date:e.end, rank:'—', athlete:c[ci], country:c[ci],
          score:`${c[ci+1]}승 ${c[ci+2]}패`, details:'라운드로빈 성적 · 최종 메달 순위와 구분', source:url});
      }
    }
  }
  if (!results.length) throw new Error('No curling standings found');
  return {source, checked_at:stamp(), status:'ok', events, results, recent:current,
    note:'최근 개최 대회 2개의 라운드로빈 승패. 조별 성적이며 플레이오프 최종 순위가 아니다. 원문 Live Game Center에서 엔드별 점수를 확인할 수 있다.'};
}
async function main() {
  const old = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT,'utf8')) : {sports:{}};
  const next = {season:SEASON, attempted_at:stamp(), sports:{...old.sports}};
  const jobs = {'short-track':()=>collectISU('short-track','ko'), 'figure-skating':()=>collectISU('figure-skating','en'),
    'speed-skating':collectSpeed, curling:collectCurling};
  const settled = await Promise.allSettled(Object.values(jobs).map(fn=>fn()));
  let failures = 0;
  Object.keys(jobs).forEach((key,i)=>{
    const r=settled[i];
    if(r.status==='fulfilled') { next.sports[key]=r.value; console.log(key, r.value.events.length,'events;',r.value.results.length,'results'); }
    else { failures++; next.sports[key]={...(old.sports[key] || {}),status:'error',error:r.reason.message,attempted_at:stamp()}; console.error(key,r.reason.message); }
  });
  fs.mkdirSync(path.dirname(OUT),{recursive:true});
  fs.writeFileSync(OUT+'.tmp',JSON.stringify(next,null,2)+'\n'); fs.renameSync(OUT+'.tmp',OUT);
  if (failures) process.exitCode=1;
}
if(require.main===module) main().catch(e=>{console.error(e);process.exitCode=1;});
module.exports={clean,flight,arrayAt,isuEvents,tableRows,curlingEvents};
