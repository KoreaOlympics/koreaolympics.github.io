"""탐색·갱신 현황 (원칙 8-5장).

    python tools/explore.py                 # data/site-index.json · data/freshness.json · explore.html · updates.html
    python tools/explore.py --checked       # 위와 같고, 자동 확인 시각을 지금으로 적는다 (매일 워크플로)
    python tools/explore.py stamp <파일…>   # 손으로 고친 자료 파일의 기준일(asof)을 오늘로 맞춘다 (푸시 워크플로)
"""
import datetime as dt, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from olympic import E, page, load, sports, hub_path, event_path, managed, GENDER  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
EDIT = 'https://github.com/koreaolympics/koreaolympics.github.io/edit/main/'
ASOF_KEYS = ('asof', 'as_of', 'asOf', 'checked', 'checked_at', 'checkedAt', 'fetchedAt', 'updated_at', 'generated')
# 자료 파일 · 이름 · 갱신 방식 · 보이는 곳
SOURCES = [
    ('data/la28-qualified.json', 'LA28 출전 확정 (쿼터)', '자동(매시) + 손 편집', 'la28-qualification.html'),
    ('data/summer-live.json', '하계 대회 결과', '자동(매시)', 'summer-live.html'),
    ('data/winter/status.json', '동계 일정·결과', '자동(매시)', 'winter/'),
    ('data/index-schedule.json', '임박한 대회 일정', '손 편집', 'index.html#upcoming'),
    ('data/team-pathways.json', '구기 예선 단계', '손 편집', 'olfootball.html#la28-pathways'),
    ('data/ijf-ranking.json', '유도 IJF 랭킹', '자동(매일)', 'oljudo.html'),
    ('data/fie-team-ranking.json', '펜싱 FIE 단체 랭킹', '자동(매일)', 'olfencing.html'),
    ('data/private-rankings/totalintel.json', '역도 잠정 OQR', '자동(매일)', 'olweightlifting.html'),
    ('data/la28-ranking-details.json', '예선 랭킹 판정 종목', '손 실행', 'index.html#ranking'),
    ('data/badminton-rankings.json', '배드민턴 BWF 랭킹', '손 실행', 'olbadminton.html'),
    ('data/tabletennis-rankings.json', '탁구 ITTF 랭킹', '손 실행', 'oltabletennis.html'),
    ('data/swimming-records.json', '수영 기록', '손 실행', 'olswimming.html'),
    ('data/taekwondo-pathways.json', '태권도 예선 경로', '손 편집', 'oltaekwondo.html'),
    ('data/shooting-pathways.json', '사격 예선 경로', '손 편집', 'olshooting.html'),
    ('data/archery-pathways.json', '양궁 예선 경로', '손 편집', 'olarchery.html'),
    ('data/boxing-pathways.json', '복싱 예선 경로', '손 편집', 'olboxing.html'),
    ('data/weightlifting-pathways.json', '역도 예선 경로', '손 편집', 'olweightlifting.html'),
]


def today():
    return dt.datetime.now(KST).strftime('%Y-%m-%d')


def date_of(path):
    """자료 파일의 기준일 (YYYY-MM-DD). 날짜 필드가 없으면 ''."""
    try:
        d = json.loads((ROOT / path).read_text(encoding='utf-8'))
    except Exception:
        return ''
    for k in ASOF_KEYS + ('fetched',):
        m = re.match(r'(\d{4})[-.](\d{2})[-.](\d{2})', str(d.get(k, ''))) if isinstance(d, dict) else None
        if m:
            return '-'.join(m.groups())
    return ''


def stamp(files):
    for f in files:
        p = ROOT / f
        if not f.endswith('.json') or not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        m = re.search(r'"(asof|as_of|asOf)":\s*"(\d{4})([-.])(\d{2})\3(\d{2})"', text)  # 날짜만 든 기준일 (시각이 붙은 자동 자료는 건드리지 않는다)
        if m:
            new = today().replace('-', m.group(3))
            old = m.group(0).split('"')[-2]
            if old != new:
                p.write_text(text[:m.start()] + m.group(0).replace(old, new) + text[m.end():], encoding='utf-8', newline='\n')
                print(f'{f}: 기준일 {old} → {new}')


def site_index(reg):
    q = json.loads((ROOT / 'data/la28-qualified.json').read_text(encoding='utf-8'))
    kor = {f: sum(1 for g in d['groups'] for r in g['rows'] if r[0] == 'KOR') for f, d in q.items() if isinstance(d, dict) and 'groups' in d}
    out, hubs = [], {}
    for season in ('summer', 'winter'):
        for s in reg[season]['sports']:
            hubs[s['file']] = (s['name'], season)
            out.append({'k': 'sport', 'n': s['name'], 'e': s['name_en'], 'u': hub_path(s), 's': season, 'sp': s['name'],
                        'c': len(s['events']), 'q': kor.get(s['file'], 0)})
            for e in s['events']:
                out.append({'k': 'event', 'n': e['name'], 'e': e.get('group', ''), 'u': event_path(s, e), 's': season, 'sp': s['name'],
                            'g': e.get('gender', ''), 'w': 1 if e.get('new') else 0})
    done = set(managed(reg))
    for p in sorted(ROOT.glob('*.html')):
        if p.name in done or re.search(r'_1\.html$|^index1|^google', p.name) or p.name in ('explore.html', 'updates.html'):
            continue
        head = p.read_text(encoding='utf-8', errors='replace')[:4000]
        m = re.search(r'<title>(.*?)</title>', head, re.S)
        if not m or 'http-equiv="refresh"' in head.lower():
            continue
        hub = hubs.get(re.split(r'[-_]', p.stem)[0])
        out.append({'k': 'doc', 'n': html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip(), 'u': p.name,
                    's': hub[1] if hub else '', 'sp': hub[0] if hub else ('아시안게임' if '아시안게임' in m.group(1) else '')})
    return out


CSS_JS = '''<script>
(function () {
  var $ = function (i) { return document.getElementById(i); }, P = new URLSearchParams(location.search), all = [];
  var st = {q: P.get('q') || '', s: P.get('s') || '', k: P.get('k') || '', g: P.get('g') || '', kor: P.get('kor') || ''};
  var KIND = {sport: '종목', event: '세부종목', doc: '문서'}, SEASON = {summer: '하계', winter: '동계'}, G = {men: '남자', women: '여자', mixed: '혼성', open: '공통'};
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function norm(t) { return String(t || '').toLowerCase().replace(/\\s/g, ''); }
  function draw() {
    var words = st.q.toLowerCase().split(/\\s+/).filter(Boolean).map(norm);
    var hit = all.filter(function (x) {
      if (st.s && x.s !== st.s) return false;
      if (st.k && x.k !== st.k) return false;
      if (st.g && x.g !== st.g) return false;
      if (st.kor && !x.q) return false;
      return words.every(function (w) { return x.h.indexOf(w) >= 0; });
    });
    var filtered = st.q || st.k || st.g || st.kor, out = '';
    if (!filtered) {  // 둘러보기: 종목 → 세부종목
      ['summer', 'winter'].forEach(function (s) {
        if (st.s && st.s !== s) return;
        out += '<h2>' + SEASON[s] + '</h2>';
        all.forEach(function (x) {
          if (x.k !== 'sport' || x.s !== s) return;
          var ev = all.filter(function (y) { return y.k === 'event' && y.sp === x.n && y.s === s; }),
              docs = all.filter(function (y) { return y.k === 'doc' && y.sp === x.n; });
          out += '<details class="xp"><summary><a href="' + x.u + '">' + esc(x.n) + '</a> <span class="small">' + esc(x.e) + ' · 세부종목 ' + x.c +
            (docs.length ? ' · 관련 문서 ' + docs.length : '') + (x.q ? ' · <b class="korq">한국 ' + x.q + '자리 확정</b>' : '') + '</span></summary><p>' +
            ev.map(function (y) { return '<a href="' + y.u + '">' + esc(y.n) + '</a>' + (y.w ? '<sup>신설</sup>' : ''); }).join(' · ') + '</p>' +
            (docs.length ? '<p class="small">관련 문서: ' + docs.map(function (y) { return '<a href="' + y.u + '">' + esc(y.n.split(' | ')[0]) + '</a>'; }).join(' · ') + '</p>' : '') + '</details>';
        });
      });
    } else {
      out = '<p class="small">' + hit.length + '건</p><ul class="xr">' + hit.slice(0, 200).map(function (x) {
        return '<li><a href="' + x.u + '">' + esc(x.n) + '</a><div class="small">' + [KIND[x.k], SEASON[x.s], x.sp !== x.n ? x.sp : '', G[x.g], x.w ? '신설' : '',
          x.q ? '한국 ' + x.q + '자리 확정' : ''].filter(Boolean).map(esc).join(' › ') + '</div></li>'; }).join('') + '</ul>' +
        (hit.length > 200 ? '<p class="small">앞의 200건만 보인다. 검색어를 더 넣는다.</p>' : '') + (hit.length ? '' : '<p>맞는 문서가 없다.</p>');
    }
    $('xout').innerHTML = out;
    document.querySelectorAll('.filters button').forEach(function (b) { b.classList.toggle('on', st[b.dataset.f] === b.dataset.v); });
    var u = new URLSearchParams(); Object.keys(st).forEach(function (k) { if (st[k]) u.set(k, st[k]); });
    history.replaceState(null, '', u.toString() ? '?' + u : location.pathname);
  }
  $('xq').value = st.q;
  $('xq').addEventListener('input', function () { st.q = this.value.trim(); draw(); });
  $('xform').addEventListener('submit', function (e) { e.preventDefault(); });
  document.querySelectorAll('.filters button').forEach(function (b) { b.addEventListener('click', function () { st[b.dataset.f] = b.dataset.v; draw(); }); });
  fetch('data/site-index.json', {cache: 'no-cache'}).then(function (r) { return r.json(); }).then(function (d) {
    all = d; all.forEach(function (x) { x.h = norm([x.n, x.e, x.sp, x.u, KIND[x.k], G[x.g]].join(' ')); }); draw();
  }).catch(function () { $('xout').innerHTML = '<p>색인을 읽지 못했다. 새로 고친다.</p>'; });
})();
</script>'''

AGE_JS = '''<script>
(function () {
  var t = new Date(new Date().toLocaleDateString('en-CA', {timeZone: 'Asia/Seoul'}));
  document.querySelectorAll('td[data-date]').forEach(function (td) {
    if (!td.dataset.date) return;
    var n = Math.round((t - new Date(td.dataset.date)) / 864e5);
    td.textContent = n <= 0 ? '오늘' : n + '일 전'; if (n > 14) td.className = 'stale';
  });
})();
</script>'''


def buttons(f, items):
    return ''.join(f'<button type="button" data-f="{f}" data-v="{v}">{E(t)}</button>' for v, t in items)


def explore_page(n):
    body = f'''<h1>탐색 <span class="en">(문서 {n}개)</span></h1>
<form id="xform" role="search"><input type="search" id="xq" name="q" placeholder="종목·세부종목·선수·대회 검색 (예: 리커브, 유도 -60kg, 쇼트트랙)" aria-label="문서 검색" autofocus></form>
<div class="filters" role="group" aria-label="구분">{buttons('s', [('', '전체'), ('summer', '하계'), ('winter', '동계')])}</div>
<div class="filters" role="group" aria-label="종류">{buttons('k', [('', '모든 종류'), ('sport', '종목'), ('event', '세부종목'), ('doc', '문서')])}{buttons('g', [('', '성별 전체'), ('men', '남자'), ('women', '여자'), ('mixed', '혼성')])}{buttons('kor', [('', '모든 종목'), ('1', '한국 출전 확정')])}</div>
<div id="xout"><p>색인을 읽는 중…</p></div>
<noscript><p>검색은 스크립트가 필요하다. <a href="index.html">대문</a>의 종목 목록에서 찾을 수 있다.</p></noscript>'''
    return page('탐색 | 코리아 올림픽스', '', body, '종목·세부종목·선수 문서 탐색').replace('</body>', CSS_JS + '\n</body>')


def updates_page(fresh):
    rows = ''.join(
        f'<tr><td><a href="{E(i["page"])}">{E(i["label"])}</a></td><td class="nowrap">{E(i["date"] or "—")}</td><td data-date="{E(i["date"])}"></td>'
        f'<td>{E(i["mode"])}</td><td><a href="{EDIT}{E(i["file"])}">편집</a></td></tr>' for i in fresh['items'])
    body = f'''<h1>갱신 현황</h1>
<p>문서에 "○○ 기준"으로 적힌 값이 어느 자료에서 오고 언제 마지막으로 바뀌었는지 모았다. 매일 자동 확인: <b>{E(fresh.get("checked") or "아직 없음")}</b></p>
<div class="tw"><table class="wikitable"><thead><tr><th>자료</th><th>기준일</th><th>경과</th><th>갱신 방식</th><th>고치기</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>고치는 방법</h2>
<ol><li>표의 <b>편집</b>이나 문서의 <span class="edit">[<a href="{EDIT}data/la28-qualified.json">편집</a>]</span>을 눌러 GitHub에서 자료 파일(JSON)을 고치고 저장(Commit)한다.</li>
<li>저장하면 워크플로 <a href="https://github.com/koreaolympics/koreaolympics.github.io/actions/workflows/refresh.yml">Refresh</a>가 기준일을 오늘로 맞추고 관련 문서를 다시 만들어 몇 분 안에 사이트에 올린다.</li>
<li>손대지 않아도 매일 새벽(KST) 같은 워크플로가 자동 자료를 다시 읽는다. 바로 돌리려면 워크플로 화면의 <b>Run workflow</b>.</li></ol>'''
    return page('갱신 현황 | 코리아 올림픽스', '', body, '자료별 기준일과 갱신 방식').replace('</body>', AGE_JS + '\n</body>')


def write(rel, text):
    p = ROOT / rel
    if not p.exists() or p.read_text(encoding='utf-8') != text:
        p.write_text(text, encoding='utf-8', newline='\n')


def main(argv):
    if argv[:1] == ['stamp']:
        return stamp(argv[1:])
    idx = site_index(load())
    write('data/site-index.json', json.dumps(idx, ensure_ascii=False, separators=(',', ':')) + '\n')
    fp = ROOT / 'data/freshness.json'
    old = json.loads(fp.read_text(encoding='utf-8')) if fp.exists() else {}
    fresh = {'checked': dt.datetime.now(KST).strftime('%Y-%m-%d %H:%M KST') if '--checked' in argv else old.get('checked', ''),
             'items': [{'file': f, 'label': l, 'mode': m, 'page': pg, 'date': date_of(f)} for f, l, m, pg in SOURCES if (ROOT / f).exists()]}
    write('data/freshness.json', json.dumps(fresh, ensure_ascii=False, indent=1) + '\n')
    write('explore.html', explore_page(len(idx)))
    write('updates.html', updates_page(fresh))
    print(f'탐색 색인 {len(idx)}건 · 자료 {len(fresh["items"])}개')


if __name__ == '__main__':
    main(sys.argv[1:])
