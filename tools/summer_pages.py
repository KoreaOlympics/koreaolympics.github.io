"""하계 메뉴 페이지 2개 (메인 하계 종목 박스 끝의 링크).

    python tools/summer_pages.py

- summer-live.html        하계 실시간: 진행 중·다가오는 LA28 예선 대회(data/index-schedule.json)와 실시간 결과 페이지
- la28-qualification.html 랭킹·출전권: 종목별·국가별 LA28 출전 확정(data/la28-qualified.json)과 예선 랭킹 페이지

진행 중/종료 표시는 페이지의 작은 스크립트가 보는 날짜(KST)로 정한다. 자료가 바뀌면 이 스크립트를 다시 돌린다.
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from olympic import E, page, load, sports, hub_path  # noqa: E402
from qualified import load as load_qualified, nation  # noqa: E402

KIND = {'direct': '직행', 'worlds': '세계선수권', 'cont': '대륙 예선', 'rank': '랭킹·기간', 'etc': '준비·마감'}
LIVE_PAGES = [('olarchery-live.html', '양궁 실시간 결과'), ('oltabletennis-live.html', '탁구 실시간 결과'), ('winter/', '동계 실시간 센터')]
STATUS_JS = '''<script>
// 오늘(KST) 기준으로 진행 중·예정·종료를 표시하고, 끝난 지 30일이 지난 대회는 접는다.
(function () {
  var today = new Date().toLocaleDateString('en-CA', {timeZone: 'Asia/Seoul'});
  var old = new Date(Date.now() - 30 * 864e5).toLocaleDateString('en-CA', {timeZone: 'Asia/Seoul'});
  document.querySelectorAll('tr[data-start]').forEach(function (tr) {
    var s = tr.dataset.start, e = tr.dataset.end || s, cell = tr.querySelector('.st');
    if (e < today) { cell.textContent = '종료'; tr.className = 'done'; if (e < old) tr.hidden = true; }
    else if (s <= today) { cell.innerHTML = '<b class="ongoing">진행 중</b>'; tr.className = 'now'; }
    else { cell.textContent = '예정'; }
  });
})();
</script>'''
STYLE = '''<style>
tr.now td { background: #fdf0f0; } tr.done td { color: #72777d; } b.ongoing { color: #d33; }
.menu-links a { margin-right: 12px; } .nowrap { white-space: nowrap; } td.num { text-align: right; }
</style>'''


def hubs():
    return {s['file']: (hub_path(s), s['name']) for s in sports(load()) if s['season'] == 'summer'}


def summer_live():
    sched = json.loads((ROOT / 'data/index-schedule.json').read_text(encoding='utf-8'))
    hub = hubs()
    rows = []
    for ev in sorted(sched['events'], key=lambda e: e['start']):
        end = ev.get('end') or ''
        when = ev['start'] + (f' ~ {end[5:]}' if end and end != ev['start'] else '')
        sp = hub.get(ev['sport'])
        label = f'<a href="{E(sp[0])}">{E(ev["label"])}</a>' if sp else E(ev['label'])
        rows.append(f'<tr data-start="{E(ev["start"])}" data-end="{E(end)}"><td class="nowrap">{E(when)}</td><td>{label}</td>'
                    f'<td>{E(ev["title"])}</td><td>{E(KIND.get(ev["kind"], ev["kind"]))}</td><td class="st"></td></tr>')
    body = f'''<nav class="crumb"><a href="index.html">목차</a> › 하계 실시간</nav>
<h1>하계 실시간 <span class="en">(LA28 예선)</span></h1>
<p>LA28 출전권이 걸린 하계 종목 대회를 진행 중·예정 순서로 모았다. 결과가 나오면 각 종목 문서의 'LA28 출전 확정' 표와
<a href="la28-qualification.html">랭킹·출전권</a> 페이지에 반영한다.</p>
<p class="menu-links">{" ".join(f'<a href="{E(u)}">🔴 {E(t)}</a>' for u, t in LIVE_PAGES)}</p>
<h2>예선 대회 일정</h2>
<div class="tw"><table class="wikitable"><thead><tr><th>기간</th><th>종목</th><th>대회</th><th>구분</th><th>상태</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<p class="note">일정 출처: data/index-schedule.json (메인 '예선 일정'과 같은 자료). 끝난 지 30일이 지난 대회는 숨긴다.</p>'''
    return page('하계 실시간 | LA28 예선', '', STYLE + body + STATUS_JS, 'LA28 하계 종목 예선 대회 진행 상황과 실시간 결과 페이지')


def qualification():
    q = load_qualified()
    hub = hubs()
    sport_rows, by_noc = [], defaultdict(list)
    for file, d in q.items():
        if not isinstance(d, dict) or 'groups' not in d or file not in hub:
            continue
        path, name = hub[file]
        cells = []
        for g in d['groups']:
            if not g['rows']:
                continue
            cells.append(f'<b>{E(g["title"])}</b>: ' + ', '.join(nation(noc, q['NOCS']) for noc, _, _ in g['rows']))
            for noc, route, _ in g['rows']:
                by_noc[noc].append((name, path, route))
        sport_rows.append(f'<tr><td class="nowrap"><a href="{E(path)}#la28-qualified">{E(name)}</a></td><td>{"<br>".join(cells)}</td></tr>')
    order = sorted(by_noc, key=lambda n: (n != 'KOR', -len({s for s, _, _ in by_noc[n]}), q['NOCS'].get(n, [n])[0]))
    noc_rows = ''.join(
        f'<tr{" class=\"kor\"" if n == "KOR" else ""}><td class="nowrap">{nation(n, q["NOCS"])}</td><td class="num">{len({s for s, _, _ in by_noc[n]})}</td><td>'
        + ' · '.join(f'<a href="{E(p)}#la28-qualified">{E(s)}</a>' for s, p in dict.fromkeys((s, p) for s, p, _ in by_noc[n])) + '</td></tr>'
        for n in order)
    ranking = [('la28-qualifier-ranking.html', '전 종목 실제 예선 랭킹'), ('la28-qualifier-ranking.html?korea=1', '랭킹 속 한국 선수')]
    ranking += [(f.name, f.stem) for f in sorted(ROOT.glob('ol*-ranking.html'))]
    names = {f: n for f, (_, n) in hub.items()}
    def rank_label(stem):
        base = stem.split('-')[0]
        return f'{names.get(base, base)} 랭킹' + (f' ({stem.split("-")[1]})' if stem.count('-') > 1 else '')
    rank_links = ' · '.join(f'<a href="{E(u)}">{E(t if not t.startswith("ol") else rank_label(t))}</a>' for u, t in ranking)
    body = f'''<nav class="crumb"><a href="index.html">목차</a> › 랭킹·출전권</nav>
<h1>LA28 랭킹·출전권</h1>
<p>{E(q["asof"])} 기준으로 정해진 LA28 하계 출전권을 종목별·국가별로 모았다. 각 종목의 경로·비고·출처는 종목 문서의 'LA28 출전 확정' 표에 있다.
아직 정해지지 않은 자리는 예선 랭킹에서 본다.</p>
<h2>예선 랭킹</h2>
<p>{rank_links}</p>
<h2>종목별 출전 확정</h2>
<div class="tw"><table class="wikitable qualified"><thead><tr><th>종목</th><th>확정 국가</th></tr></thead><tbody>{"".join(sport_rows)}</tbody></table></div>
<h2>국가별 출전 확정</h2>
<p>한 종목에서 여러 자리를 얻어도 종목 수로 한 번만 센다. 대한민국을 맨 위에 둔다.</p>
<div class="tw"><table class="wikitable qualified"><thead><tr><th>국가</th><th>종목 수</th><th>종목</th></tr></thead><tbody>{noc_rows}</tbody></table></div>'''
    return page('LA28 랭킹·출전권', '', STYLE + body, 'LA28 하계 종목 출전 확정 국가와 예선 랭킹 모음')


def main():
    (ROOT / 'summer-live.html').write_text(summer_live(), encoding='utf-8', newline='\n')
    (ROOT / 'la28-qualification.html').write_text(qualification(), encoding='utf-8', newline='\n')
    print('summer-live.html · la28-qualification.html')


if __name__ == '__main__':
    main()
