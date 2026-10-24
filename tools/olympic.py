"""koreaolympics.github.io 구조 관리 툴 (PRINCIPLES.md 구현).

    python tools/olympic.py build   # 종목 · 세부종목 문서 생성/갱신, index 동계 목록 갱신 (본문 보존, 실시간 자료 갱신)
    python tools/olympic.py check   # 원칙 9장 검사 (실패 시 종료 코드 1)
    python tools/olympic.py todo    # LIVE 표시 · <!-- 추가: --> 자리 목록

명단은 data/olympic-structure.json 하나만 기준으로 한다.
build는 틀(경로·제목·도입문 링크·목차·내비박스·실시간 블록)만 다시 쓰고,
각 섹션 본문과 인포박스는 기존 파일에서 그대로 가져온다.
"""
import html, json, re, sys
from datetime import date
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
TAEKWONDO_EVENT_SECTIONS = [('rules', '예선 규정 및 통과자'), ('results', '주요 대회 결과'),
                            ('athletes', '주목 선수'), ('refs', '각주'), ('links', '외부 링크')]
OPTIONAL = {'rules'}  # 내용이 없으면 화면에서 숨긴다 (원칙 5.5)


# 종목별 맞춤 구조 (영어 Wikipedia 구조 기준). 없는 종목은 기본 구조를 쓴다.
LAYOUT = {
    'olwrestling': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olweightlifting': {'hub': [('timeline', '예선 일정 (Timeline)'), ('qualification', '예선 규정 (Qualification)'), ('men', "남자 종목 (Men's events)"), ('women', "여자 종목 (Women's events)"), ('medals', '2024 메달리스트'), ('korea', '한국 역도 역사와 현황'), ('refs', '각주'), ('links', '외부 링크'), ('results_summary', '대회별 메달 요약')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olboxing': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'oljudo': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olbasketball': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olfootball': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olwaterpolo': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olrugby': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olbaseball': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'ollacrosse': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olcricket': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olflagfootball': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olhockey': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olhandball': {'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')], 'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')]},
    'olvolleyball': {
        'hub': [('qualification', '예선 요약'), ('medals', '2024 메달리스트'), ('korea', '한국 상황 분석'), ('refs', '각주'), ('links', '외부 링크')],
        'event': [('quota', '확보 팀'), ('refs', '각주'), ('links', '외부 링크')],
    },
}


def hub_sections(s):
    return LAYOUT.get(s['file'], {}).get('hub', HUB_SECTIONS)


def event_sections(s):
    if s['file'] in LAYOUT:
        return LAYOUT[s['file']]['event']
    return TAEKWONDO_EVENT_SECTIONS if s['file'] == 'oltaekwondo' else EVENT_SECTIONS


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
SEC_RE = re.compile(r'<section id="([a-z0-9]+)"[^>]*>\s*(?:<h2[^>]*>(.*?)</h2>)?(.*?)</section>', re.S)
INFO_RE = re.compile(r'<aside class="infobox"[^>]*>.*?<tbody>(.*?)</tbody>', re.S)


def preserved(path):
    if not path.exists():
        return None
    text = path.read_text(encoding='utf-8')
    if f'content="{GEN}"' not in text:
        return None  # 구 구조 문서: 새 틀로 교체
    parts = {m.group(1): m.group(3).strip('\n') for m in SEC_RE.finditer(text)}
    titles = {m.group(1): re.sub(r'<[^>]+>', '', m.group(2) or m.group(1)).strip() for m in SEC_RE.finditer(text)}
    parts['__titles__'] = titles
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



TW_OPEN, TW_CLOSE = '<div class="tw">', '</div><!-- /tw -->'


def wrap_tables(body):
    """본문 표를 전체 폭 + 가로 스크롤 상자로 감싼다 (여러 번 실행해도 같다)."""
    body = body.replace(TW_OPEN, '').replace(TW_CLOSE, '')
    out, i = [], 0
    tok = re.compile(r'<(/?)table\b[^>]*>')
    while True:
        m = re.compile(r'<table class="wikitable[^"]*"[^>]*>').search(body, i)
        if not m:
            out.append(body[i:])
            return ''.join(out)
        depth = 0
        for t in tok.finditer(body, m.start()):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                out.append(body[i:m.start()] + TW_OPEN + body[m.start():t.end()] + TW_CLOSE)
                i = t.end()
                break
        else:
            out.append(body[i:])
            return ''.join(out)


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
    if s['file'] == 'oltaekwondo':
        rule_rows = [
            ('D1 · WT 세계 랭킹', '2028년 1월 올림픽 랭킹 체급별 상위 5명'),
            ('D2 · 그랜드슬램 메리트', '2028년 1월 체급별 메리트 랭킹 1위'),
            ('D3 · 대륙 예선', '아시아·유럽·아프리카·아메리카 상위 2명씩, 오세아니아 상위 1명 (체급별 9명). D1·D2로 해당 성별 2명 이상을 확보한 NOC는 참가할 수 없다.'),
            ('D4 · 개최국', '미국에 남녀 각 최소 2명 보장. 미국이 일반 경로로 얻은 출전권 수에 따라 조정된다.'),
            ('D5 · 보편성', '남녀 각 2명, 총 4명. 3자위원회가 배정한다.'),
        ]
        rules = ('<div class="tk-table-wrap tk-compact">'
                 '<table class="wikitable"><thead><tr><th>예선 항목</th><th>예선 방식</th></tr></thead><tbody>\n'
                 + ''.join(f'<tr><th scope="row">{E(label)}</th><td>{E(method)}</td></tr>\n' for label, method in rule_rows)
                 + '</tbody></table></div>\n'
                 + '<div class="tk-table-wrap tk-compact">'
                 + '<table class="wikitable"><thead><tr><th>예선 항목</th><th>합격자 명단</th></tr></thead><tbody>\n'
                 + ''.join(f'<tr><th scope="row">{E(label.split(" · ")[0])}</th><td></td></tr>\n' for label, _ in rule_rows)
                 + '</tbody></table></div>')
    athletes = '<!-- 추가: 선수 · NOC · 근거(랭킹 · 주요 성적). 한국 선수 행은 class="kor" -->'
    if e.get('live', '').startswith('swim:'):
        rules = live_block(e) + '\n' + rules
    elif e.get('live'):
        athletes = live_block(e) + '\n' + athletes
    result = {
        'rules': rules,
        'quota': ('<table class="wikitable"><thead><tr><th>NOC</th><th>선수</th><th>획득 경로</th><th>일자</th></tr></thead>'
                  '<tbody>\n<!-- 추가: 출전권 획득 (기준일 · 남은 쿼터 수 함께 표기) -->\n</tbody></table>'),
        'results': ('<table class="wikitable medals"><thead><tr><th>대회</th><th>금</th><th>은</th><th>동</th></tr></thead>'
                    '<tbody>\n<!-- 추가: 직전 올림픽 · 최근 세계선수권 등. 진행 중이면 대회명 뒤 <span class="live">LIVE</span> -->\n</tbody></table>'),
        'athletes': athletes,
        'refs': '<ol class="references">\n<!-- 추가: 출처 (확인일 포함) -->\n</ol>',
        'links': '<ul>\n<!-- 추가: 공식 페이지 · 대회 정보 · 칼럼 -->\n</ul>',
    }
    if s['file'] == 'oltaekwondo':
        result.pop('quota')
    return result


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


def related_block(s, today=None):
    """관련 대회·랭킹 (자동): 일정 자료(index-schedule)와 랭킹 자료(la28-ranking-details)에서 종목별로 가져온다."""
    today = today or date.today().isoformat()
    html_parts = []
    sched = _json('data/index-schedule.json') or {'events': []}
    evs = [x for x in sched['events'] if x['sport'] == s['file'] and (x.get('end') or x['start']) >= today]
    if evs:
        rows = ''.join(
            f'<tr><td>{E(x["start"])}{("–" + E(x["end"][5:])) if x.get("end") else ""}</td>'
            f'<td>{E(x["title"])}</td><td>{E(x.get("kind", ""))}</td></tr>'
            for x in sorted(evs, key=lambda x: x['start'])[:8])
        html_parts.append('<h3>관련 대회</h3><table class="wikitable narrow"><thead><tr><th>기간</th><th>대회</th><th>경로</th></tr></thead>'
                          f'<tbody>{rows}</tbody></table>')
    d = _json('data/la28-ranking-details.json') or {'rankings': []}
    for r in d['rankings']:
        if r.get('page') != hub_path(s) or not r.get('rows'):
            continue
        body = ''
        for row in r['rows'][:10]:
            cls = ' class="kor"' if row.get('noc') == 'KOR' else ''
            body += f'<tr{cls}><td>{E(row.get("rank", ""))}</td><td>{E(row.get("name", ""))}</td><td>{E(row.get("noc", ""))}</td><td>{E(row.get("score", ""))}</td></tr>'
        html_parts.append(f'<h3>{E(r.get("name", ""))}</h3><p class="note">기준: {E(r.get("updated", ""))} · <a href="{E(r.get("source", ""))}">원문</a></p>'
                          '<table class="wikitable narrow"><thead><tr><th>순위</th><th>선수·팀</th><th>NOC</th><th>점수</th></tr></thead>'
                          f'<tbody>{body}</tbody></table>')
    if not html_parts:
        return ''
    return '<section id="related">\n<h2>관련 대회 · 랭킹</h2>\n' + '\n'.join(html_parts) + '\n</section>'


def render_sections(defs, parts):
    toc, out = [], []
    titles = parts.get('__titles__', {})
    extra = [k for k in parts if k not in {d[0] for d in defs} | {'__titles__', 'infobox', 'intro', 'related'}]
    defs = list(defs) + [(k, titles.get(k, k)) for k in extra if k not in {d[0] for d in defs}]
    for sid, title in defs:
        body = wrap_tables(fill_live(parts.get(sid, '')))
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
    layout_ids = {k for k, _ in hub_sections(s)}
    for k, v in sk.items():
        if k in layout_ids:  # 허브 구조에 없는 빈 기본 섹션(규정·일정·직전 메달 표)은 만들지 않는다
            parts.setdefault(k, v)
    info = parts.get('infobox') or hub_infobox(reg, s)
    g = reg[s['season']]
    def line(label, evs):
        if len(evs) == 1 and evs[0]['name'] == label:  # 단체 구기: 남자 / 여자
            return f'<li><a href="{E(event_path(s, evs[0]))}">{E(label)}</a></li>'
        return (f'<li><b>{E(label)}</b> ' + ' · '.join(
            f'<a href="{E(event_path(s, e))}">{E(short(e, s, label))}</a>' for e in evs) + '</li>')
    lines = ''.join(line(label, evs) for label, evs in event_groups(s))
    basis = f' 세부종목은 {E(g["program_basis"])} 기준이다.' if g.get('program_basis') else ''
    lead = (f'<section id="intro" class="lead"><p>{E(g["games"])} {E(s["name"])}에는 '
            f'<b>{len(s["events"])}개</b> 세부종목이 있다.{basis}</p><ul class="event-list">{lines}</ul></section>')
    toc, secs = render_sections(hub_sections(s), parts)
    rel = related_block(s)
    if rel and '<section id="results_summary"' in secs:  # 마지막 섹션(대회별 메달 요약)을 맨 아래에 둔다
        secs = secs.replace('<section id="results_summary"', rel + '\n<section id="results_summary"', 1)
        rel = ''
    body = '\n'.join([
        f'<nav class="crumb"><a href="index.html">목차</a> › {E(s["name"])}</nav>',
        f'<h1>{E(s["name"])} <span class="en">({E(s["name_en"])})</span></h1>',
        '<div class="top">', infobox(s['name'], info), lead, '</div>', toc, secs, rel,
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
    toc, secs = render_sections(event_sections(s), parts)
    groups = [(label, [(e2['file'] + '.html', short(e2, s, label)) for e2 in evs]) for label, evs in event_groups(s)]
    nb = navbox(f'<a href="../{E(hub_path(s))}">{E(s["name"])}</a> 세부종목', groups, e['file'] + '.html')
    body = '\n'.join([
        f'<nav class="crumb"><a href="../index.html">목차</a> › <a href="../{E(hub_path(s))}">{E(s["name"])}</a> › {E(e["name"])}</nav>',
        f'<h1>{E(s["name"])} · {E(e["name"])}</h1>',
        '<div class="top">', infobox(e['name'], info), f'<section id="intro" class="lead">\n{intro}\n</section>', '</div>',
        toc, secs, nb])
    return path, page(f'{s["name"]} · {e["name"]} | {g["games"]}', '../', body,
                      f'{g["games"]} {s["name"]} {e["name"]} 예선·쿼터·주요 선수')


INDEX_SECTIONS = [('upcoming', '임박한 대회'), ('korea', '한국 출전권'), ('ranking', '랭킹'),
                  ('athletes', '한국 선수 문서'), ('links', '외부 링크')]
INDEX_GENERATED = {'upcoming'}
SPORT_BOLD = {'summer': ['배드민턴', '사격', '양궁', '유도', '태권도', '펜싱'], 'winter': ['쇼트트랙', '컬링', '스노보드']}


def sport_box(reg, season):
    """index 상단 종목 박스. 하계는 첫 줄 볼드 종목 + 줄바꿈 + 가나다순, 동계는 가나다순 한 줄(볼드 표시)."""
    g = reg[season]
    links = {s['name']: hub_path(s) for s in g['sports']}
    bold = [n for n in SPORT_BOLD[season] if n in links]
    link = lambda n: f'<a href="{E(links[n])}">{E(n)}</a>'
    if season == 'summer':
        rest = sorted(n for n in links if n not in bold)
        top = ' · '.join(f'<b>{link(n)}</b>' for n in bold)
        body = f'{top}<br>' + ' · '.join(link(n) for n in rest)
        caption = f'{E(g["games"])} 종목'
    else:
        names = sorted(links)
        body = ' · '.join(f'<b>{link(n)}</b>' if n in bold else link(n) for n in names)
        body += ' · <a href="winter/">🔴 동계 실시간 센터</a>'  # 일정·결과 자동 수집 앱 (winter/, 원칙 8장 예외)
        caption = f'{E(g["games"])} 종목'
    return (f'<nav class="navbox"><table><caption>{caption}</caption>'
            f'<tbody><tr><th>{E(g["label"])}</th><td>{body}</td></tr></tbody></table></nav>')
SCHEDULE = 'data/index-schedule.json'


def _d(s):
    return s.replace('-', '.')


def render_upcoming(reg, today):
    """임박한 대회 표: data/index-schedule.json에서 만든다. 상태(LIVE · D-n)와 지난 일정 숨김은 스크립트가 오늘 날짜로 다시 계산한다."""
    import datetime as dt
    d = json.loads((ROOT / SCHEDULE).read_text(encoding='utf-8'))
    kinds = d['kinds']
    names = {s['file']: s['name'] for s in sports(reg)}
    rows = ''
    for x in sorted(d['events'], key=lambda x: x['start']):
        end = x.get('end') or x['start']
        if end < today:
            continue
        a, b = dt.date.fromisoformat(x['start']), dt.date.fromisoformat(today)
        status = '<span class="live">LIVE</span>' if x['start'] <= today else f'D-{(a - b).days}'
        when = _d(x['start']) + (f'–{_d(x["end"])[5:]}' if x.get('end') and x['end'][:4] == x['start'][:4]
                                  else f'–{_d(x["end"])}' if x.get('end') else '')
        title = f'<b>{E(x["title"])}</b>' if x.get('major') else E(x['title'])
        rows += (f'<tr data-start="{x["start"]}" data-end="{end}" data-kind="{x["kind"]}"{" class=\"major\"" if x.get("major") else ""}>'
                 f'<td>{when}</td><td><a href="{E(x["sport"])}.html">{E(x.get("label") or names.get(x["sport"], x["sport"]))}</a></td>'
                 f'<td>{E(kinds[x["kind"]])}</td><td class="status">{status}</td><td class="content">{title}</td></tr>\n')
    buttons = '<button type="button" data-kind="" class="on">전체</button>' + ''.join(
        f'<button type="button" data-kind="{k}">{E(v)}</button>' for k, v in kinds.items())
    return (f'<p>진행 중이거나 다가오는 예선 대회·랭킹 기간·마감일. <b>굵은 글씨</b>는 출전권이 많이 걸린 주요 대회다. '
            f'일정 자료: <code>{SCHEDULE}</code></p>\n'
            f'<div class="filters" role="group" aria-label="경로별 보기">{buttons}</div>\n'
            '<table class="wikitable upcoming"><thead><tr><th>날짜</th><th>종목</th><th>경로</th><th>상태</th><th>내용</th></tr></thead>'
            f'<tbody>\n{rows}</tbody></table>\n<p><button type="button" id="upcoming-more">전체 일정 보기</button></p>')


def render_sports_index(reg):
    out = ['<p><input type="search" id="sport-search" placeholder="종목·세부종목 검색 (예: 리커브, judo, 쇼트트랙)" aria-label="종목 검색"></p>']
    for season in ('summer', 'winter'):
        g = reg[season]
        n = sum(len(s['events']) for s in g['sports'])
        rows = ''
        for s in g['sports']:
            kw = ' '.join([s['name_en'].lower()] + [e['name'] for e in s['events']] + s.get('groups', []))
            rows += (f'<tr data-kw="{E(kw)}"><td><a href="{E(hub_path(s))}">{E(s["name"])}</a></td>'
                     f'<td>{E(s["name_en"])}</td><td>{len(s["events"])}</td></tr>')
        note = f' 세부종목은 {E(g["program_basis"])} 기준.' if g.get('program_basis') else ''
        out.append(f'<h3>{E(g["label"])} · {E(g["games"])}</h3><p>{len(g["sports"])}개 종목 · {n}개 세부종목.{note}</p>'
                   f'<table class="wikitable portal sports-table"><thead><tr><th>종목</th><th>영문</th><th>세부종목</th></tr></thead>'
                   f'<tbody>{rows}</tbody></table>')
    return '\n'.join(out)


def live_rankings(_key):
    d = _json('data/la28-ranking-details.json')
    if not d:
        return None
    by = {}
    for r in d['rankings']:
        if not r.get('rows'):
            continue
        x = by.setdefault(r['sport'], {'count': 0, 'kor': 0})
        x['count'] += 1
        if r.get('korea') or any(v.get('noc') == 'KOR' for v in r['rows']):
            x['kor'] += 1
    from urllib.parse import quote
    items = ' · '.join(
        (f'<a href="la28-qualifier-ranking.html?sport={quote(s)}{"&amp;korea=1" if x["kor"] else ""}">'
         + (f'<b>{E(s)}</b>' if x['kor'] else E(s)) + '</a>')
        for s, x in sorted(by.items(), key=lambda kv: (-(kv[1]['kor'] > 0), kv[0])))
    return (f'<p>현재 순위표가 형성된 예선 랭킹 {len(by)}개 종목 ({E(d["generated"][:10])} 기준). '
            f'<b>굵은 글씨</b>는 대한민국이 랭킹에 있는 종목.</p><p>{items}</p>')


LIVE['rankings'] = live_rankings

INDEX_SCRIPT = """<script>
(function(){
  function day(s){var a=s.split('-');return new Date(+a[0],+a[1]-1,+a[2]);}
  var now=new Date(),today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
  var rows=[].slice.call(document.querySelectorAll('table.upcoming tbody tr')),kind='',all=false;
  rows.forEach(function(tr){
    var a=day(tr.dataset.start),b=day(tr.dataset.end),st=tr.querySelector('.status');
    tr.dataset.past=b<today?'1':'';
    st.innerHTML=a<=today?'<span class="live">LIVE</span>':'D-'+Math.round((a-today)/864e5);
  });
  function show(){var n=0;rows.forEach(function(tr){var ok=!tr.dataset.past&&(!kind||tr.dataset.kind===kind);
    if(ok)n++;tr.hidden=!ok||(!all&&n>10);});
    var m=document.getElementById('upcoming-more');if(m)m.textContent=all?'처음 10개만 보기':'전체 일정 보기';}
  document.querySelectorAll('.filters button').forEach(function(btn){btn.addEventListener('click',function(){
    kind=btn.dataset.kind;document.querySelectorAll('.filters button').forEach(function(b){b.classList.toggle('on',b===btn);});show();});});
  var more=document.getElementById('upcoming-more');if(more)more.addEventListener('click',function(){all=!all;show();});
  show();
  var q=document.getElementById('sport-search');
  if(q)q.addEventListener('input',function(){var v=q.value.trim().toLowerCase().replace(/\\s/g,'');
    document.querySelectorAll('.sports-table tbody tr').forEach(function(tr){
      var h=(tr.textContent+' '+tr.dataset.kw).toLowerCase().replace(/\\s/g,'');tr.hidden=!!v&&h.indexOf(v)<0;});});
})();
</script>"""


def render_index(reg, today=None):
    """index: 대문. 임박한 대회·종목 목록·랭킹 블록은 툴이 만들고, 나머지 섹션은 사람이 쓴다.
    예외 규정(원칙 8장): 종목 문서 외 내부 페이지 링크와 스크립트를 허용한다."""
    import datetime as dt
    today = today or dt.date.today().isoformat()
    path = ROOT / 'index.html'
    parts = preserved(path) or {}
    gen = {'upcoming': render_upcoming(reg, today)}
    intro = parts.get('intro') or '<p><!-- 추가: 사이트 소개 --></p>'
    secs = []
    toc = []
    for sid, title in INDEX_SECTIONS:
        body = wrap_tables(gen.get(sid) or fill_live(parts.get(sid, '<!-- 추가 -->')))
        if sid == 'korea':  # 목차 오른쪽 박스
            korea = f'<section id="korea" class="quota-box">\n<h2>{E(title)}</h2>\n{body}\n</section>'
            continue
        toc.append(f'<li><a href="#{sid}">{E(title)}</a></li>')
        secs.append(f'<section id="{sid}">\n<h2>{E(title)}</h2>\n{body}\n</section>')
    body = '\n'.join([
        '<h1>올림픽예선 <span class="en">(LA28 종목별 예선 시스템)</span></h1>',
        sport_box(reg, 'summer'), sport_box(reg, 'winter'),
        f'<section id="intro" class="lead">\n{intro}\n</section>',
        '<div class="toc-row">', f'<nav class="toc"><h2>목차</h2><ol>{"".join(toc)}</ol></nav>', korea, '</div>',
        *secs])
    html_ = page('올림픽예선 | 코리아 올림픽스', '', body, '2028 LA 올림픽·동계 올림픽 종목별 예선, 임박한 대회, 한국 출전권과 랭킹')
    return path, html_.replace('</body>', INDEX_SCRIPT + '\n</body>')


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
            if re.search(r'\.(png|jpe?g|webp|gif|svg|pdf)$', target):  # 이미지·첨부 파일은 허용 (존재만 확인)
                if not (ROOT / target).exists():
                    errors.append(f'{rel}: 없는 파일 → {target}')
                continue
            if target not in files:
                if (files[rel][1] is not None and files[rel][1]['file'] == 'oltaekwondo'
                        and re.fullmatch(r'oltaekwondo-p-[a-z0-9-]+\.html', target)
                        and (ROOT / target).is_file()):
                    continue
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
        layout_ids = {k for k, _ in (hub_sections(s) if kind == 'hub' else event_sections(s))}
        ids = [i for i in re.findall(r'<section id="([a-z0-9_]+)"', t) if i == 'intro' or i in layout_ids]
        want = ['intro'] + [k for k, _ in (hub_sections(s) if kind == 'hub' else event_sections(s))]
        if ids != want:
            errors.append(f'{rel}: 섹션 순서 {ids} ≠ {want}')
        # Validate local anchors on the taekwondo pages, including headings
        # that look like links and point to sections that have been removed.
        if s['file'] == 'oltaekwondo':
            page_ids = set(re.findall(r'\bid="([^"]+)"', t))
            for href in re.findall(r'<a\b[^>]*\bhref="([^"]*)"', t):
                if not href or re.match(r'^(?:[a-z]+:|//)', href, re.I):
                    continue
                raw_path, _, fragment = href.partition('#')
                target = (Path(rel).parent / raw_path).as_posix() if raw_path else rel
                target = str(Path(target))
                target_text = texts.get(target)
                if target_text is None and (ROOT / target).is_file():
                    target_text = (ROOT / target).read_text(encoding='utf-8')
                if target_text is None:
                    errors.append(f'{rel}: 끊긴 내부 링크 → {href}')
                    continue
                if fragment and not re.search(r'\bid="' + re.escape(fragment) + r'"', target_text):
                    errors.append(f'{rel}: 없는 내부 문서 위치 → {href}')
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
