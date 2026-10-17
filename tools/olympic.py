"""koreaolympics.github.io 구조 관리 툴 (PRINCIPLES.md 구현).

    python tools/olympic.py build   # 종목 · 세부종목 문서 생성/갱신, index 동계 목록 갱신 (본문 보존, 실시간 자료 갱신)
    python tools/olympic.py check   # 원칙 9장 검사 (실패 시 종료 코드 1)
    python tools/olympic.py todo    # LIVE 표시 · <!-- 추가: --> 자리 목록

명단은 data/olympic-structure.json 하나만 기준으로 한다.
build는 틀(경로·제목·도입문 링크·목차·내비박스·실시간 블록)만 다시 쓰고,
각 섹션 본문과 인포박스는 기존 파일에서 그대로 가져온다.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'data/olympic-structure.json'
GEN = 'koreaolympics-structure'
CSS = 'css/site.css'
SITE = '코리아 올림픽스'
GENDER = {'men': '남자', 'women': '여자', 'mixed': '혼성', 'open': '성별 구분 없음'}
E = lambda s: html.escape(str(s), quote=True)

HUB_SECTIONS = [('rules', '예선 규정'), ('schedule', '예선 일정'), ('previous', '직전 올림픽 메달리스트'),
                ('korea', '대한민국'), ('refs', '각주'), ('links', '외부 링크')]
EVENT_SECTIONS = [('rules', '예선 규정'), ('quota', '쿼터 획득 현황'), ('results', '주요 대회 결과'),
                  ('athletes', '주목 선수'), ('refs', '각주'), ('links', '외부 링크')]
OPTIONAL = {'rules'}  # 내용이 없으면 화면에서 숨긴다 (원칙 5.5)


# ---------------------------------------------------------------- registry
def load():
    reg = json.loads(REG.read_text(encoding='utf-8'))
    for season in ('summer', 'winter'):
        for s in reg[season]['sports']:
            s['season'] = season
            for e in s['events']:
                e['sport'] = s
    return reg


def sports(reg):
    return reg['summer']['sports'] + reg['winter']['sports']


def hub_path(s):
    return f"{s['file']}.html"


def event_path(s, e):
    return f"{s['file']}/{e['file']}.html"


def event_groups(s):
    """[(label, [events])] - 분야가 있으면 분야별, 없으면 성별."""
    if s.get('groups'):
        return [(g, [e for e in s['events'] if e.get('group') == g]) for g in s['groups']]
    out = []
    for g in ('men', 'women', 'mixed', 'open'):
        evs = [e for e in s['events'] if e['gender'] == g]
        if evs:
            out.append((GENDER[g], evs))
    return out


def short(e, s, label):
    """도입문·내비박스에서 성별 머리말 뒤의 짧은 이름."""
    name = e['name']
    if not s.get('groups') and name.startswith(label + ' '):
        return name[len(label) + 1:]
    return name


# ---------------------------------------------------------------- preserve
SEC_RE = re.compile(r'<section id="([a-z]+)"[^>]*>\s*(?:<h2[^>]*>.*?</h2>)?(.*?)</section>', re.S)
INFO_RE = re.compile(r'<aside class="infobox"[^>]*>.*?<tbody>(.*?)</tbody>', re.S)


def preserved(path):
    if not path.exists():
        return None
    text = path.read_text(encoding='utf-8')
    if f'content="{GEN}"' not in text:
        return None  # 구 구조 문서: 새 틀로 교체
    parts = {m.group(1): m.group(2).strip('\n') for m in SEC_RE.finditer(text)}
    m = INFO_RE.search(text)
    if m:
        parts['infobox'] = m.group(1).strip('\n')
    return parts


def visible(body):
    return bool(re.sub(r'<!--.*?-->|\s', '', body, flags=re.S))


# ---------------------------------------------------------------- live data
def _json(rel):
    p = ROOT / rel
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None


def _rank_table(caption, src, rows, extra=()):
    head = '<tr><th>순위</th><th>선수·팀</th><th>NOC</th><th>포인트</th></tr>'
    body = ''
    for r in rows:
        cls = ' class="kor"' if r['noc'] == 'KOR' else ''
        body += f"<tr{cls}><td>{E(r['rank'])}</td><td>{E(r['name'])}</td><td>{E(r['noc'])}</td><td>{E(r['points'])}</td></tr>"
    for r in extra:
        body += f"<tr class=\"kor\"><td>{E(r['rank'])}</td><td>{E(r['name'])}</td><td>{E(r['noc'])}</td><td>{E(r['points'])}</td></tr>"
    return (f'<table class="wikitable"><caption>{caption} · <a href="{E(src)}">원문</a></caption>'
            f'<thead>{head}</thead><tbody>{body}</tbody></table>')


def _top(rows, n=10):
    top = rows[:n]
    kor = [r for r in rows[n:] if r['noc'] == 'KOR']
    return top, kor


def live_ijf(key):
    d = _json('data/ijf-ranking.json')
    c = d and d['categories'].get(key)
    if not c:
        return None
    rows = [dict(rank=a['rank'], name=a['name'], noc=a['noc'], points=int(a['points'])) for a in c['athletes']]
    top, kor = _top(rows)
    return _rank_table(f"IJF 세계랭킹 ({d['checkedAt'][:10]} 기준)", c['source'], top, kor)


def _racket(rel, label, key):
    d = _json(rel)
    ev = d and d['events'].get(key)
    if not ev:
        return None
    rows = [dict(rank=r['rank'], name=' / '.join(r['names']), noc=r.get('noc', ''), points=r['points']) for r in ev['rows']]
    top, kor = _top(rows)
    kor += [dict(rank=r['rank'], name=' / '.join(r['names']), noc='KOR', points=r['points'])
            for r in ev.get('koreaOutsideTop20', [])]
    return _rank_table(f"{label} ({str(ev['date']).split(' ')[0]} 기준)", ev['source'], top, kor)


def live_bwf(key):
    return _racket('data/badminton-rankings.json', 'BWF 세계랭킹', key)


def live_ittf(key):
    return _racket('data/tabletennis-rankings.json', 'ITTF 세계랭킹', key)


def live_fie(key):
    d = _json('data/fie-team-ranking.json')
    ev = d and next((x for x in d['events'] if x['id'] == key), None)
    if not ev:
        return None
    rows = [dict(rank=t['rank'], name=t['country'], noc=t['code'], points=t['points']) for t in ev['teams']]
    top, kor = _top(rows, 16)
    return _rank_table(f"FIE 단체 랭킹 ({d['fetchedAt'][:10]} 기준)", ev['source'], top, kor)


def live_swim(key):
    b = _json('data/swimming-benchmarks.json') or {}
    r = _json('data/swimming-records.json') or {}
    be = b.get('events', {}).get(key)
    re_ = r.get('records', {}).get(key)
    if not be and not re_:
        return None
    rows = ''
    if be and be.get('world'):
        w = be['world']
        rows += (f"<tr><th>세계기록</th><td>{E(w['time'])}</td><td>{E(w['holder'])} ({E(w.get('noc', ''))})</td>"
                 f"<td>{E(w.get('date', ''))}</td><td><a href=\"{E(w['source'])}\">원문</a></td></tr>")
    if re_:
        rows += (f"<tr class=\"kor\"><th>한국기록</th><td>{E(re_['time'])}</td><td>{E(re_['holder'])}</td>"
                 f"<td>{E(re_.get('date', ''))}</td><td><a href=\"{E(re_['source'])}\">원문</a></td></tr>")
    if be and be.get('a'):
        note = f" · {E(be['a_reason'])}" if be.get('a_reason') else ''
        rows += f"<tr><th>LA28 기준기록</th><td>{E(be['a'])}</td><td colspan=\"3\">{E(b.get('standard_version', ''))}{note}</td></tr>"
    when = (b.get('checked_at') or r.get('checked_at') or '')[:10]
    return (f'<table class="wikitable"><caption>기록 ({E(when)} 기준)</caption>'
            f'<thead><tr><th></th><th>기록</th><th>보유자</th><th>일자</th><th>출처</th></tr></thead><tbody>{rows}</tbody></table>')


LIVE = {'ijf': live_ijf, 'bwf': live_bwf, 'ittf': live_ittf, 'fie': live_fie, 'swim': live_swim}
LIVE_RE = re.compile(r'(<!-- live:start ([a-z]+):([a-z0-9]+) -->)(.*?)(<!-- live:end -->)', re.S)


def fill_live(body):
    def sub(m):
        fn = LIVE.get(m.group(2))
        out = fn(m.group(3)) if fn else None
        if out is None:
            out = '<p>자료 없음</p>'
        return f'{m.group(1)}\n{out}\n{m.group(5)}'
    return LIVE_RE.sub(sub, body)


def live_block(e):
    return f"<!-- live:start {e['live']} -->\n<!-- live:end -->" if e.get('live') else ''


# ---------------------------------------------------------------- skeletons (첫 생성 때만 쓰임)
def hub_infobox(reg, s):
    g = reg[s['season']]
    return '\n'.join([
        f'<tr><th>대회</th><td>{E(g["games"])}</td></tr>',
        f'<tr><th>세부종목</th><td>{len(s["events"])}개</td></tr>',
        '<tr><th>장소</th><td>미정</td></tr>', '<tr><th>기간</th><td>미정</td></tr>',
        '<tr><th>출전 정원</th><td>미정</td></tr>', '<tr><th>NOC당 최대</th><td>미정</td></tr>',
        '<tr><th>한국 확보 쿼터</th><td>미정</td></tr>'])


def event_infobox(reg, s, e):
    g = reg[s['season']]
    prev = '신설' if e.get('new') else '미정'
    return '\n'.join([
        f'<tr><th>종목</th><td>{E(s["name"])}</td></tr>', f'<tr><th>대회</th><td>{E(g["games"])}</td></tr>',
        '<tr><th>장소</th><td>미정</td></tr>', '<tr><th>날짜</th><td>미정</td></tr>',
        '<tr><th>출전 정원</th><td>미정</td></tr>', '<tr><th>NOC당 최대</th><td>미정</td></tr>',
        '<tr><th>경기 방식</th><td>미정</td></tr>', f'<tr><th>직전 올림픽 금메달</th><td>{prev}</td></tr>'])


SCHEDULE_TABLE = ('<table class="wikitable schedule"><thead><tr><th>기간</th><th>대회</th><th>장소</th>'
                  '<th>배정 쿼터</th><th>결과</th></tr></thead><tbody>\n'
                  '<!-- 추가: 예선 대회 (시작일 순). 랭킹 종목은 "랭킹 기간 시작"·"랭킹 기간 종료" 행과 그 사이 주요 대회 -->\n'
                  '</tbody></table>')


def hub_skeleton(reg, s):
    prev = reg[s['season']]['previous']
    rows = ''.join(
        f"<tr><th><a href=\"{E(event_path(s, e))}\">{E(e['name'])}</a></th>"
        + ('<td colspan="3">신설</td>' if e.get('new') else '<td></td><td></td><td></td>') + '</tr>\n'
        for e in s['events'])
    return {
        'rules': '<!-- 추가: 최신 예선 규정 (쿼터 배분 · 개최국·보편성 · 참가 자격). 규정이 없으면 비워 둔다 -->',
        'schedule': SCHEDULE_TABLE,
        'previous': (f'<p>{E(prev)}</p>\n<table class="wikitable medals"><thead><tr><th>세부종목</th>'
                     f'<th>금</th><th>은</th><th>동</th></tr></thead><tbody>\n{rows}</tbody></table>\n'
                     '<!-- 추가: 칸에는 "선수명 (NOC)", 단체는 "NOC" -->'),
        'korea': ('<h3>주요 선수</h3>\n<!-- 추가: 선수 · 세부종목 · 최근 주요 성적 · 세계랭킹(기준일) -->\n'
                  '<h3>쿼터 확보 현황</h3>\n<table class="wikitable"><thead><tr><th>세부종목</th><th>확보 인원</th>'
                  '<th>상태</th><th>획득 대회</th></tr></thead><tbody>\n<!-- 추가: 상태는 확정 · 잠정 · 미확보 -->\n</tbody></table>\n'
                  '<h3>남은 예선 일정</h3>\n<!-- 추가: 한국이 출전권을 노릴 수 있는 남은 대회 (시간 순) -->'),
        'refs': '<ol class="references">\n<!-- 추가: 출처 (확인일 포함) -->\n</ol>',
        'links': '<ul>\n<!-- 추가: 공식 페이지 · 대회 정보 · 칼럼 -->\n</ul>',
    }


def event_skeleton(reg, s, e):
    rules = '<!-- 추가: 종목 규정 중 이 세부종목에 해당하는 것 -->'
    athletes = '<!-- 추가: 선수 · NOC · 근거(랭킹 · 주요 성적). 한국 선수 행은 class="kor" -->'
    if e.get('live', '').startswith('swim:'):
        rules = live_block(e) + '\n' + rules
    elif e.get('live'):
        athletes = live_block(e) + '\n' + athletes
    return {
        'rules': rules,
        'quota': ('<table class="wikitable"><thead><tr><th>NOC</th><th>선수</th><th>획득 경로</th><th>일자</th></tr></thead>'
                  '<tbody>\n<!-- 추가: 출전권 획득 (기준일 · 남은 쿼터 수 함께 표기) -->\n</tbody></table>'),
        'results': ('<table class="wikitable medals"><thead><tr><th>대회</th><th>금</th><th>은</th><th>동</th></tr></thead>'
                    '<tbody>\n<!-- 추가: 직전 올림픽 · 최근 세계선수권 등. 진행 중이면 대회명 뒤 <span class="live">LIVE</span> -->\n</tbody></table>'),
        'athletes': athletes,
        'refs': '<ol class="references">\n<!-- 추가: 출처 (확인일 포함) -->\n</ol>',
        'links': '<ul>\n<!-- 추가: 공식 페이지 · 대회 정보 · 칼럼 -->\n</ul>',
    }


# ---------------------------------------------------------------- render
def page(title, up, body, desc):
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="{GEN}">
<meta name="description" content="{E(desc)}">
<title>{E(title)}</title>
<link rel="stylesheet" href="{up}{CSS}">
</head>
<body>
<header class="site"><a href="{up}index.html">{SITE}</a></header>
<main class="article">
{body}
</main>
</body>
</html>
'''


def render_sections(defs, parts):
    toc, out = [], []
    for sid, title in defs:
        body = fill_live(parts.get(sid, ''))
        hidden = sid in OPTIONAL and not visible(body)
        if not hidden:
            toc.append(f'<li><a href="#{sid}">{E(title)}</a></li>')
        out.append(f'<section id="{sid}"{" hidden" if hidden else ""}>\n<h2>{E(title)}</h2>\n{body}\n</section>')
    return f'<nav class="toc"><h2>목차</h2><ol>{"".join(toc)}</ol></nav>', '\n'.join(out)


def infobox(caption, rows):
    return f'<aside class="infobox"><table><caption>{E(caption)}</caption><tbody>\n{rows}\n</tbody></table></aside>'


def navbox(title, groups, current=None):
    rows = ''
    for label, links in groups:
        items = ' · '.join(f'<strong>{E(t)}</strong>' if h == current else f'<a href="{E(h)}">{E(t)}</a>' for h, t in links)
        rows += f'<tr><th>{E(label)}</th><td>{items}</td></tr>'
    return f'<nav class="navbox"><table><caption>{title}</caption><tbody>{rows}</tbody></table></nav>'


def season_navbox(reg, season, up, current=None):
    g = reg[season]
    links = [(up + hub_path(s), s['name']) for s in g['sports']]
    return navbox(f'{E(g["games"])} 종목', [(g['label'], links)], current)


def render_hub(reg, s):
    path = ROOT / hub_path(s)
    parts = preserved(path) or {}
    sk = hub_skeleton(reg, s)
    for k, v in sk.items():
        parts.setdefault(k, v)
    info = parts.get('infobox') or hub_infobox(reg, s)
    g = reg[s['season']]
    lines = ''.join(
        f'<li><b>{E(label)}</b> ' + ' · '.join(f'<a href="{E(event_path(s, e))}">{E(short(e, s, label))}</a>' for e in evs) + '</li>'
        for label, evs in event_groups(s))
    basis = f' 세부종목은 {E(g["program_basis"])} 기준이다.' if g.get('program_basis') else ''
    lead = (f'<section id="intro" class="lead"><p>{E(g["games"])} {E(s["name"])}에는 '
            f'<b>{len(s["events"])}개</b> 세부종목이 있다.{basis}</p><ul class="event-list">{lines}</ul></section>')
    toc, secs = render_sections(HUB_SECTIONS, parts)
    body = '\n'.join([
        f'<nav class="crumb"><a href="index.html">목차</a> › {E(s["name"])}</nav>',
        f'<h1>{E(s["name"])} <span class="en">({E(s["name_en"])})</span></h1>',
        '<div class="top">', infobox(s['name'], info), lead, '</div>', toc, secs,
        season_navbox(reg, s['season'], '', hub_path(s))])
    return path, page(f'{s["name"]} | {g["games"]}', '', body, f'{g["games"]} {s["name"]} 세부종목·예선·한국 현황')


def render_event(reg, s, e):
    path = ROOT / event_path(s, e)
    parts = preserved(path) or {}
    for k, v in event_skeleton(reg, s, e).items():
        parts.setdefault(k, v)
    info = parts.get('infobox') or event_infobox(reg, s, e)
    intro = parts.get('intro') or '<p><!-- 추가: 이 세부종목이 무엇인지, 몇 명이 어떻게 겨루는지 2~3문장 --></p>'
    g = reg[s['season']]
    toc, secs = render_sections(EVENT_SECTIONS, parts)
    groups = [(label, [(e2['file'] + '.html', short(e2, s, label)) for e2 in evs]) for label, evs in event_groups(s)]
    nb = navbox(f'<a href="../{E(hub_path(s))}">{E(s["name"])}</a> 세부종목', groups, e['file'] + '.html')
    body = '\n'.join([
        f'<nav class="crumb"><a href="../index.html">목차</a> › <a href="../{E(hub_path(s))}">{E(s["name"])}</a> › {E(e["name"])}</nav>',
        f'<h1>{E(s["name"])} · {E(e["name"])}</h1>',
        '<div class="top">', infobox(e['name'], info), f'<section id="intro" class="lead">\n{intro}\n</section>', '</div>',
        toc, secs, nb])
    return path, page(f'{s["name"]} · {e["name"]} | {g["games"]}', '../', body,
                      f'{g["games"]} {s["name"]} {e["name"]} 예선·쿼터·주요 선수')


WD_RE = re.compile(r'(<nav class="wd-grid"[^>]*>).*?(</nav>)', re.S)


def render_index(reg):
    """index는 예외: 사람이 관리하는 대시보드다 (랭킹·현황 등 다른 내부 링크 허용).
    툴은 동계 종목 목록(wd-grid)만 명단대로 다시 쓴다. 하계 종목 연결은 check가 확인한다."""
    path = ROOT / 'index.html'
    with open(path, encoding='utf-8', newline='') as f:  # 원본 줄바꿈(CRLF) 유지
        text = f.read()
    pills = ''.join(f'<a class="wd-pill" href="./{E(hub_path(s))}">{E(s["name"])}</a>' for s in reg['winter']['sports'])
    if WD_RE.search(text):
        text = WD_RE.sub(lambda m: m.group(1) + pills + m.group(2), text, count=1)
    return path, text


def build():
    reg = load()
    pages = [render_index(reg)]
    for s in sports(reg):
        pages.append(render_hub(reg, s))
        pages += [render_event(reg, s, e) for e in s['events']]
    changed = 0
    for path, text in pages:
        path.parent.mkdir(parents=True, exist_ok=True)
        old = open(path, encoding='utf-8', newline='').read() if path.exists() else None
        if old != text:
            path.write_text(text, encoding='utf-8', newline='\n')
            changed += 1
    print(f'build: {len(pages)}개 문서, {changed}개 갱신')


# ---------------------------------------------------------------- check / todo
def managed(reg):
    files = {'index.html': ('index', None, None)}
    for s in sports(reg):
        files[hub_path(s)] = ('hub', s, None)
        for e in s['events']:
            files[event_path(s, e)] = ('event', s, e)
    return files


def links_of(rel, text):
    base = Path(rel).parent
    out = []
    for h in re.findall(r'(?:href|src)="([^"]+)"', text):
        if re.match(r'[a-z]+:', h) or h.startswith('#'):
            continue
        target = (base / h.split('#')[0].split('?')[0]).as_posix()
        parts = []
        for p in target.split('/'):
            if p == '..':
                parts.pop() if parts else parts.append('..')
            elif p not in ('', '.'):
                parts.append(p)
        out.append('/'.join(parts))
    return out


def check():
    reg = load()
    files = managed(reg)
    errors = []
    texts = {}
    for rel in files:
        p = ROOT / rel
        if not p.exists():
            errors.append(f'없음: {rel}')
        else:
            texts[rel] = p.read_text(encoding='utf-8')
    # 2. 폴더 안 명단 밖 파일
    for s in sports(reg):
        d = ROOT / s['file']
        if d.is_dir():
            for f in d.iterdir():
                if f'{s["file"]}/{f.name}' not in files:
                    errors.append(f'명단 밖 파일: {s["file"]}/{f.name}')
    # 3. 링크
    graph = {}
    for rel, t in texts.items():
        graph[rel] = []
        for target in links_of(rel, t):
            if target == CSS:
                continue
            if target not in files:
                if rel != 'index.html':
                    errors.append(f'{rel}: 관리 대상 밖 내부 링크 → {target}')
            elif not (ROOT / target).exists():
                errors.append(f'{rel}: 끊긴 링크 → {target}')
            else:
                graph[rel].append(target)
    seen, stack = {'index.html'}, ['index.html']
    while stack:
        for t in graph.get(stack.pop(), []):
            if t not in seen:
                seen.add(t)
                stack.append(t)
    errors += [f'index에서 도달 불가: {r}' for r in files if r in texts and r not in seen]
    # 4~6. 형식
    for s in sports(reg):
        if hub_path(s) not in graph.get('index.html', []):
            errors.append(f'index.html: 종목 문서 연결 없음 → {hub_path(s)}')
    for rel, t in texts.items():
        kind, s, e = files[rel]
        if kind == 'index':
            continue
        if f'content="{GEN}"' not in t:
            errors.append(f'{rel}: 관리 툴이 만든 문서가 아님 (build 필요)')
            continue
        css = re.findall(r'<link[^>]+rel="stylesheet"[^>]*>', t)
        if len(css) != 1 or CSS not in css[0]:
            errors.append(f'{rel}: 공통 CSS 하나만 써야 함')
        if '<script' in t:
            errors.append(f'{rel}: JavaScript 사용')
        ids = re.findall(r'<section id="([a-z]+)"', t)
        want = ['intro'] + [k for k, _ in (HUB_SECTIONS if kind == 'hub' else EVENT_SECTIONS)]
        if ids != want:
            errors.append(f'{rel}: 섹션 순서 {ids} ≠ {want}')
        if kind == 'hub':
            lead = re.search(r'<section id="intro".*?</section>', t, re.S).group(0)
            n = len(re.findall(r'<a href="' + re.escape(s['file']) + r'/', lead))
            if n != len(s['events']):
                errors.append(f'{rel}: 도입문 세부종목 링크 {n}개 ≠ 명단 {len(s["events"])}개')
    for x in errors:
        print('✗', x)
    print(f'check: 문서 {len(files)}개, 오류 {len(errors)}개')
    return 1 if errors else 0


def todo():
    reg = load()
    for rel in managed(reg):
        p = ROOT / rel
        if not p.exists():
            continue
        t = p.read_text(encoding='utf-8')
        live = t.count('class="live"')
        add = len(re.findall(r'<!-- 추가:', t))
        if live or add:
            print(f'{rel}\tLIVE {live}\t추가 {add}')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'build':
        build()
    elif cmd == 'check':
        sys.exit(check())
    elif cmd == 'todo':
        todo()
    else:
        sys.exit(__doc__)
