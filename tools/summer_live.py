"""하계 실시간·최근 대회 결과 (위키백과 대회 문서 → data/summer-live.json → 허브 '2026 주요 대회 결과'·summer-live.html).

    python tools/summer_live.py collect          # 진행 중이거나 막 끝난 대회(시작 1일 전 ~ 끝난 뒤 10일)만 다시 읽는다
    python tools/summer_live.py collect --all    # 목록의 모든 대회를 다시 읽는다
    python tools/summer_live.py render           # 자료로 허브 블록만 다시 그린다 (인터넷 없이)

대회 목록은 data/summer-live-sources.json. 위키백과 문서는 대회 중 몇 시간 안에 메달리스트가 채워진다.
출전권 표(Olympic qualification)가 있는 대회는 그 결과를 data/la28-qualified.json의 해당 허브에
'auto' 묶음으로 넣는다(손으로 쓴 묶음은 건드리지 않는다).
"""
import datetime as dt, html, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import wikiresults as wr  # noqa: E402
import korean_names  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data/summer-live-sources.json'
OUT = ROOT / 'data/summer-live.json'
QUAL = ROOT / 'data/la28-qualified.json'
FLAGS = ROOT / 'assets/flags'
E = lambda s: html.escape(str(s), quote=True)
BLOCK_RE = re.compile(r'<div class="results" id="recent-results">.*?</div><!-- /results -->\n?', re.S)
KST = dt.timezone(dt.timedelta(hours=9))

TERMS = [  # 긴 것부터 바꾼다
    ("Men's", '남자'), ("Women's", '여자'), ('Mixed', '혼성'), ('Men', '남자'), ('Women', '여자'),
    ('10 metre air pistol', '10m 공기권총'), ('10m Air Pistol', '10m 공기권총'), ('10 metre air rifle', '10m 공기소총'), ('10m Air Rifle', '10m 공기소총'),
    ('25 metre rapid fire pistol', '25m 속사권총'), ('25m Rapid Fire Pistol', '25m 속사권총'), ('25 metre centre fire pistol', '25m 센터파이어 권총'),
    ('25 metre standard pistol', '25m 스탠더드 권총'), ('25 metre pistol', '25m 권총'), ('25m Pistol', '25m 권총'), ('50 metre pistol', '50m 권총'),
    ('50 metre rifle three positions', '50m 소총 3자세'), ('50m Rifle 3 Positions', '50m 소총 3자세'), ('50 metre rifle prone', '50m 소총 복사'),
    ('rapid fire pistol', '속사권총'), ('air pistol', '공기권총'), ('air rifle', '공기소총'), ('rifle 3 positions', '소총 3자세'),
    ('rifle three positions', '소총 3자세'), ('rifle prone', '소총 복사'), ('skeet', '스키트'), ('Skeet', '스키트'), ('trap', '트랩'), ('Trap', '트랩'), ('double trap', '더블 트랩'),
    ('Clean & Jerk', '용상'), ('Snatch', '인상'), ('Total', '합계'),
    ('Team all-around', '단체'), ('Individual all-around', '개인종합'), ('All-around', '개인종합'), ('Floor', '마루'), ('Pommel horse', '안마'),
    ('Rings', '링'), ('Vault', '도마'), ('Parallel bars', '평행봉'), ('Horizontal bar', '철봉'), ('Uneven bars', '이단평행봉'), ('Balance beam', '평균대'),
    ('Team sprint', '단체 스프린트'), ('Team pursuit', '단체 추발'), ('Individual pursuit', '개인 추발'), ('Elimination race', '제외 경기'),
    ('Points race', '포인트 경기'), ('Scratch', '스크래치'), ('Keirin', '경륜'), ('Omnium', '옴니엄'), ('Madison', '매디슨'), ('Sprint', '스프린트'),
    ('time trial', '독주'), ('Time trial', '독주'),
    ('Freestyle', '자유형'), ('freestyle', '자유형'), ('Greco-Roman', '그레코로만형'), ('Individual épée', '에페 개인'), ('Individual foil', '플뢰레 개인'),
    ('Individual sabre', '사브르 개인'), ('Team épée', '에페 단체'), ('Team foil', '플뢰레 단체'), ('Team sabre', '사브르 단체'),
    ('épée', '에페'), ('foil', '플뢰레'), ('sabre', '사브르'), ('Épée', '에페'), ('Foil', '플뢰레'), ('Sabre', '사브르'),
    ("singles", '단식'), ("doubles", '복식'), ('Singles', '단식'), ('Doubles', '복식'), ('Recurve', '리커브'), ('recurve', '리커브'),
    ('Compound', '컴파운드'), ('compound', '컴파운드'), ('individual', '개인'), ('Individual', '개인'), ('teams', '단체'), ('team', '단체'), ('Team', '단체'),
    ('metre', 'm'), ('metres', 'm'), ('Pistol events', '권총'), ('Rifle events', '소총'), ('Shotgun events', '산탄총'),
    ('Pistol', '권총'), ('Rifle', '소총'), ('Shotgun', '산탄총'),
]
STAGE = {'Final': '파이널'}
VENUE = {'Granada': '그라나다', 'Munich': '뮌헨', 'Hangzhou': '항저우', 'Cairo': '카이로', 'Tangier': '탕헤르', 'Almaty': '알마티',
         'Lonato': '로나토', 'Rome': '로마', 'Lima': '리마', 'Doha': '도하', 'Baku': '바쿠', 'New Delhi': '뉴델리', 'Changwon': '창원'}


def ko(s):
    for a, b in TERMS:
        s = re.sub(rf'(?<![A-Za-z]){re.escape(a)}(?![A-Za-z])', b, s, flags=re.I)
    return re.sub(r'(\d+) m\b', r'\1m', s).strip()


def load(p, default=None):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default


def today():
    return dt.datetime.now(KST).date().isoformat()


def status(src, day=None):
    day = day or today()
    if day < src['start']:
        return 'soon'
    return 'live' if day <= src['end'] else 'done'


def in_window(src, day=None):
    d = dt.date.fromisoformat(day or today())
    return dt.date.fromisoformat(src['start']) - dt.timedelta(days=1) <= d <= dt.date.fromisoformat(src['end']) + dt.timedelta(days=10)


# ── 수집 ─────────────────────────────────────────────

def collect_one(src):
    text = wr.fetch(src['wiki'])
    if text.lstrip().lower().startswith('#redirect'):
        target = re.search(r'\[\[([^\]|#]+)', text).group(1)
        text = wr.fetch(target)
    item = {'fetched': dt.datetime.now(KST).strftime('%Y-%m-%d %H:%M'), 'events': [], 'season': [], 'table': [], 'quotas': []}
    if src.get('kind') == 'season':
        item['season'] = wr.season(text)
    else:
        item['events'] = wr.medalists(text)
    kor = {n for e in item['events'] + item['season'] for m in e['medals'] if m['noc'] == 'KOR' for n in m['names']}
    if kor:  # 새 한국 선수: 위키백과 선수 문서에서 한글 이름 확인, 없으면 로마자에서 옮긴다
        links = {}
        for a, b in re.findall(r'\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]', text):
            links.setdefault((b or a).strip(), a.strip())
        korean_names.resolve(kor, links, wr.fetch)
    item['table'] = wr.medal_table(text)
    item['quotas'] = wr.quotas(text)
    return item


def collect(all_=False):
    srcs = load(SRC)['events']
    data = load(OUT, {'results': {}})
    n = 0
    for src in srcs:
        if not all_ and not in_window(src) and src['id'] in data['results']:
            continue
        try:
            got = collect_one(src)
        except Exception as e:  # 한 대회가 실패해도 나머지는 계속
            print(f'{src["id"]}: 읽기 실패 {e}')
            continue
        old = data['results'].get(src['id'])
        if old and not (got['events'] or got['season']) and (old.get('events') or old.get('season')):
            print(f'{src["id"]}: 메달리스트 표를 못 읽어 이전 자료를 둔다')
            continue
        if old and {k: v for k, v in old.items() if k != 'fetched'} == {k: v for k, v in got.items() if k != 'fetched'}:
            continue  # 바뀐 것 없음: 읽은 시각만으로 커밋하지 않는다
        data['results'][src['id']] = got
        n += 1
        done = sum(1 for e in got['events'] if e['medals']) + sum(1 for e in got['season'] if e['medals'])
        print(f'{src["id"]}: 종목 {len(got["events"]) or len(got["season"])}개 중 {done}개 결과, 출전권 {sum(len(q[2]) for q in got["quotas"])}자리')
    if n:
        data['asof'] = dt.datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    update_quotas(srcs, data)
    return n


def _tokens(label):
    return frozenset(ko(label).replace("'", '').split())


def quota_holder(res, quota_event, noc):
    """출전권 표는 국가만 적으므로, 같은 대회 개인 종목 결과에서 그 나라 선수를 찾는다. ' · 반효진 (금)' 또는 ''."""
    want = _tokens(quota_event)
    names = kor_names()
    for e in res.get('events', []):
        if _tokens(e['event']) != want:
            continue
        for i, m in enumerate(e['medals']):
            if m['noc'] == noc and len(m['names']) == 1:
                p = m['names'][0]
                shown = names.get(p, (p, False))[0] if noc == 'KOR' else p
                return f' · {shown} ({"금은동"[min(i, 2)]})'
        return ' · 결선 메달 밖 (선수 확인 필요)'
    return ''


def korea_summary(data=None):
    """진행 중·최근 대회에서 한국이 얻은 LA28 출전권과 메달 — summer-live.html 맨 위."""
    data = data or load(OUT, {'results': {}})
    srcs = sorted(load(SRC)['events'], key=lambda s: s['start'], reverse=True)
    names = kor_names()
    items = []
    for src in srcs:
        res = data['results'].get(src['id'])
        if not res or not in_window(src) or status(src) == 'soon':
            continue
        quotas = [ko(ev) + quota_holder(res, ev, 'KOR') for ev, _, nocs in res.get('quotas', []) if 'KOR' in nocs]
        meds = []
        for grp, ev, stage, ms in rows_of(src, res):
            for i, m in enumerate(ms[:4]):
                if m['noc'] == 'KOR':
                    who_ = '·'.join(names.get(p, (p, False))[0] for p in m['names'][:4]) if len(m['names']) <= 4 else f'{len(m["names"])}명'
                    label = f'{grp.split(" ", 1)[-1]} {ev}' if stage else ev  # 시즌 문서: '남자 개인 10m 공기소총'
                    meds.append(f'{"🥇🥈🥉"[min(i, 2)]} {label}{" · " + stage if stage else ""} {who_}')
        if quotas or meds:
            items.append((src, quotas, meds))
    if not items:
        return ''
    out = ['<div class="korea-news"><h2>🇰🇷 한국 소식 <span class="asof">' + E(data.get('asof', '')) + '</span></h2>']
    for src, quotas, meds in items:
        out.append(f'<h3>{E(src["title"])} <span class="small">{E(src.get("place", ""))} · {"진행 중" if status(src) == "live" else "종료"}</span></h3><ul>')
        out += [f'<li><b>LA28 출전권 획득</b>: {E(q)}</li>' for q in quotas]
        out += [f'<li>{E(m)}</li>' for m in meds]
        out.append('</ul>')
    out.append('<p class="small">사격 출전권은 선수가 아니라 국가(NOC)가 받는다. 선수 이름은 같은 대회 결선 결과에서 찾은 것이다.</p></div>')
    return '\n'.join(out)


def update_quotas(srcs, data):
    """출전권 표가 있는 대회 → la28-qualified.json의 허브에 'auto' 묶음."""
    q = load(QUAL)
    changed = False
    for src in srcs:
        res = data['results'].get(src['id'])
        if not res or not src.get('quota_route'):
            continue
        rows = [[noc, src['quota_route'], ko(ev) + quota_holder(res, ev, noc)] for ev, _, nocs in res['quotas'] for noc in nocs]
        hub = q.setdefault(src['sport'], {'groups': []})
        groups = [g for g in hub['groups'] if g.get('auto') != src['id']]
        if rows:
            groups.append({'title': src['quota_title'], 'auto': src['id'], 'rows': rows})
        if groups != hub['groups']:
            hub['groups'] = groups
            src_link = [f'위키백과: {src["wiki"]}', 'https://en.wikipedia.org/wiki/' + src['wiki'].replace(' ', '_')]
            if src_link not in hub.setdefault('sources', []):
                hub['sources'].append(src_link)
            changed = True
    if changed:
        q['asof'] = today()
        QUAL.write_text(json.dumps(q, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print('출전 확정 자료 갱신')


# ── 그리기 ───────────────────────────────────────────

def nocs():
    n = load(ROOT / 'data/nocs.json', {'NOCS': {}})['NOCS']
    return {**n, **load(QUAL)['NOCS']}


def flag(noc, up=''):
    if (FLAGS / f'{noc}.svg').exists():
        return f'<img class="flag" src="{up}assets/flags/{noc}.svg" alt="" width="20" height="15">'
    return '<span class="flag none"></span>'


def kor_names():
    """{로마자: (한글, 추정 여부)} — data/korean-names.json의 확인(names)·추정(guessed)."""
    d = load(ROOT / 'data/korean-names.json', {})
    return {**{k: (v, True) for k, v in d.get('guessed', {}).items()}, **{k: (v, False) for k, v in d.get('names', {}).items()}}


def person(p, names):
    ko, guessed = names.get(p, (None, False))
    if not ko:
        return E(p)
    if guessed:
        return f'<span class="guess" title="{E(p)} — 로마자 표기에서 옮긴 이름 (확인 전)">{E(ko)}</span>'
    return f'<span title="{E(p)}">{E(ko)}</span>'


def who(m, codes, names, up=''):
    noc = m['noc']
    nat = codes.get(noc, [noc])[0]
    people = m['names']
    if not people or (len(people) == 1 and people[0] in (nat, noc)):
        txt = E(nat)
    elif len(people) > 4:
        txt = f'{E(nat)} <span class="small">({len(people)}명)</span>'
    else:
        txt = '·'.join(person(p, names) if noc == 'KOR' else E(p) for p in people) + f' <span class="small">{E(nat)}</span>'
    mark = f' <span class="small">{E(m["mark"])}</span>' if m.get('mark') else ''
    cls = ' class="kor"' if noc == 'KOR' else ''
    return f'<span{cls}>{flag(noc, up)}{txt}</span>{mark}'


def rows_of(src, res):
    """[(묶음, 종목, 차수/장소, 메달)]"""
    if res.get('season'):
        return [(ko(e['section']), ko(e['event']), STAGE.get(e['stage'], e['stage'] + '차') + ' ' + VENUE.get(e['venue'], e['venue']), e['medals']) for e in res['season']]
    return [(ko(e['section']), ko(e['event']), '', e['medals']) for e in res['events']]


def kor_line(rows):
    g = [0, 0, 0]
    for *_, meds in rows:
        for i, m in enumerate(meds[:4]):
            if m['noc'] == 'KOR':
                g[min(i, 2)] += 1
    return g


def event_card(src, res, codes, names, up='', open_=False, limit=None):
    st = status(src)
    rows = rows_of(src, res)
    done = [r for r in rows if r[3]]
    g = kor_line(rows)
    tag = {'live': '<b class="ongoing">진행 중</b>', 'done': '종료', 'soon': '예정'}[st]
    wiki = 'https://en.wikipedia.org/wiki/' + src['wiki'].replace(' ', '_')
    head = (f'<summary><b>{E(src["title"])}</b> <span class="small">{E(src.get("place", ""))} · {E(src["start"][5:].replace("-", "."))}~{E(src["end"][5:].replace("-", "."))}</span> '
            f'{tag} <span class="small">결과 {len(done)}/{len(rows)}종목 · 한국 금{g[0]} 은{g[1]} 동{g[2]}</span></summary>')
    body = []
    show = done if not limit else done[-limit:]
    if show:
        tr = []
        last = None
        for grp, ev, stage, meds in show:
            if grp != last and not src.get('kind') == 'season':
                tr.append(f'<tr class="grp"><th colspan="4">{E(grp)}</th></tr>')
                last = grp
            cells = ''.join(f'<td>{who(m, codes, names, up)}</td>' for m in meds[:3])
            extra = ''.join(f'<br>{who(m, codes, names, up)}' for m in meds[3:])
            if extra:
                cells = cells[:-5] + extra + '</td>'
            label = E(ev) + (f' <span class="small">{E(stage)}</span>' if stage else '')
            kor = ' class="has-kor"' if any(m['noc'] == 'KOR' for m in meds) else ''
            tr.append(f'<tr{kor}><th scope="row">{label}</th>{cells}</tr>')
        body.append('<div class="tw"><table class="wikitable medal-rows"><thead><tr><th>종목</th><th>금</th><th>은</th><th>동</th></tr></thead>'
                    f'<tbody>{"".join(tr)}</tbody></table></div>')
    else:
        body.append('<p class="muted">아직 결과가 없다.</p>')
    pending = [ev for _, ev, _, meds in rows if not meds]
    if pending and st != 'soon':
        body.append(f'<p class="small">남은 종목: {E(", ".join(pending))}</p>')
    if res.get('table'):
        top = res['table'][:8]
        if not any(r[0] == 'KOR' for r in top):
            top += [r for r in res['table'] if r[0] == 'KOR']
        body.append('<p class="small">메달 순위: ' + ' · '.join(f'{flag(c, up)}{E(codes.get(c, [c])[0])} {a}-{b}-{d}' for c, a, b, d in top) + '</p>')
    if res.get('quotas'):
        body.append('<p class="small"><b>LA28 출전권</b>: ' + ' · '.join(
            f'{E(ko(ev))} ' + ', '.join(f'{flag(c, up)}{E(codes.get(c, [c])[0])}' for c in l) for ev, _, l in res['quotas']) + '</p>')
    body.append(f'<p class="src">출처: <a href="{E(wiki)}">위키백과 {E(src["wiki"])}</a> · {E(res["fetched"])} 읽음</p>')
    return f'<details class="result-card"{" open" if open_ else ""}>{head}{"".join(body)}</details>'


def hub_block(file, data=None):
    data = data or load(OUT, {'results': {}})
    srcs = [s for s in load(SRC)['events'] if s['sport'] == file and s['id'] in data['results']]
    if not srcs:
        return ''
    codes, names = nocs(), kor_names()
    srcs.sort(key=lambda s: s['start'], reverse=True)
    cards = ''.join(event_card(s, data['results'][s['id']], codes, names, open_=status(s) == 'live' and s.get('kind') != 'season') for s in srcs)
    return (f'<div class="results" id="recent-results"><h2>2026 주요 대회 결과 <span class="asof">{E(data.get("asof", ""))}</span></h2>'
            f'<p class="small">위키백과 대회 문서에서 자동으로 모은다. 대회 중에는 한 시간마다 새로 읽는다. 한국 선수가 있는 줄은 붉게 칠했다. '
            f'<a href="summer-live.html">하계 실시간 전체 →</a></p>{cards}</div><!-- /results -->')


def render():
    data = load(OUT, {'results': {}})
    n = 0
    for page in sorted(ROOT.glob('ol*.html')):
        if '-' in page.stem:
            continue
        orig = page.read_text(encoding='utf-8')
        text = BLOCK_RE.sub('', orig)
        b = hub_block(page.stem, data)
        if b and '<nav class="toc">' in text:
            text = text.replace('<nav class="toc">', b + '\n<nav class="toc">', 1)
            n += 1
        if text != orig:
            page.write_text(text, encoding='utf-8', newline='\n')
    print(f'{n}개 허브에 대회 결과')


def live_section():
    """summer-live.html 첫머리: 진행 중이거나 열흘 안에 끝난 대회 결과, 그 밖의 2026 대회 목록."""
    data = load(OUT, {'results': {}})
    codes, names = nocs(), kor_names()
    reg = json.loads((ROOT / 'data/olympic-structure.json').read_text(encoding='utf-8'))
    hub = {s['file']: s['name'] for s in reg['summer']['sports']}
    srcs = sorted(load(SRC)['events'], key=lambda s: s['start'], reverse=True)
    now = [s for s in srcs if s['id'] in data['results'] and in_window(s) and status(s) != 'soon']
    out = [korea_summary(data), f'<h2>진행 중·최근 대회 결과 <span class="asof">{E(data.get("asof", ""))}</span></h2>']
    if now:
        out += [f'<h3>{E(hub.get(s["sport"], ""))}</h3>' + event_card(s, data['results'][s['id']], codes, names, open_=s.get('kind') != 'season') for s in now]
    else:
        out.append('<p class="muted">지금 진행 중인 대회가 없다.</p>')
    rest = [s for s in srcs if s['id'] in data['results'] and s not in now]
    if rest:
        out.append('<h2>2026 대회 결과 모음</h2><div class="tw"><table class="wikitable"><thead><tr><th>기간</th><th>종목</th><th>대회</th><th>결과</th><th>한국</th></tr></thead><tbody>')
        for s in rest:
            rows = rows_of(s, data['results'][s['id']])
            g = kor_line(rows)
            out.append(f'<tr><td class="nowrap">{E(s["start"])} ~ {E(s["end"][5:])}</td><td><a href="{E(s["sport"])}.html#recent-results">{E(hub.get(s["sport"], s["sport"]))}</a></td>'
                       f'<td>{E(s["title"])} <span class="small">{E(s.get("place", ""))}</span></td><td class="c">{sum(1 for r in rows if r[3])}/{len(rows)}</td>'
                       f'<td class="nowrap">금{g[0]} 은{g[1]} 동{g[2]}</td></tr>')
        out.append('</tbody></table></div>')
    return '\n'.join(out)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'render'
    if cmd == 'active':  # 지금 진행 중인 대회 수 (워크플로가 반복 여부를 정한다)
        print(sum(1 for s in load(SRC)['events'] if status(s) == 'live' and s.get('kind') != 'season'))
        sys.exit()
    if cmd == 'collect':
        collect('--all' in sys.argv)
    render()
