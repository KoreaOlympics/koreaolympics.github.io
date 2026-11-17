"""동계 허브 '직전 올림픽 메달리스트' 표를 2026 밀라노·코르티나 결과로 채운다 (data/milano2026-medals.json).

    python tools/milano_medals.py fetch   # Wikipedia 각 종목 메달 표를 다시 읽어 자료 파일을 만든다
    python tools/milano_medals.py         # 자료 파일로 허브 표를 채운다 (여러 번 실행해도 같다)

- 2030 세부종목 가운데 2026 대회에도 있던 것: 금·은·동 칸을 채운다.
- 2026 대회에 없던 세부종목(2030 신설·제안): "2026 대회에 없던 세부종목"으로 적는다.
- 표기는 파리 2024 표(tools/paris_medals.py)와 같다: 3명 이하는 "이름 (NOC)", 그보다 큰 팀은 NOC, 공동 메달은 ' / '.
  한국 선수는 자료 파일의 `ko`에 확인된 한글 이름이 있으면 한글로 적는다.
자료는 Wikipedia "<Sport> at the 2026 Winter Olympics"의 메달 표에서 뽑는다.
"""
import datetime as dt, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/milano2026-medals.json'
E = lambda s: html.escape(str(s), quote=False)
TR = re.compile(r'<tr>.*?</tr>\n?', re.S)
ABSENT = '<td colspan="3">2026 대회에 없던 세부종목</td>'
NOTE = '<p class="note milano-note">출처: Wikipedia 각 종목 2026 동계 올림픽 메달 표. 3명을 넘는 팀은 NOC만 적고, 공동 메달은 " / "로 나란히 적는다.</p>'

PAGES = {'wialpine': 'Alpine skiing', 'wibiathlon': 'Biathlon', 'wibobsleigh': 'Bobsleigh', 'wicrosscountry': 'Cross-country skiing',
         'wicurling': 'Curling', 'wifigure': 'Figure skating', 'wifreestyle': 'Freestyle skiing', 'wiicehockey': 'Ice hockey', 'wiluge': 'Luge',
         'wishorttrack': 'Short-track speed skating', 'wiskeleton': 'Skeleton', 'wiskijumping': 'Ski jumping',
         'wiskimountaineering': 'Ski mountaineering', 'wisnowboard': 'Snowboarding', 'wispeedskating': 'Speed skating'}

# Wikipedia 종목 이름(소문자) → 허브 세부종목 이름에서 성별을 뺀 부분
EVENT = {
    'wialpine': {'downhill': '활강', 'super-g': '슈퍼대회전', 'giant slalom': '대회전', 'slalom': '회전', 'team combined': '팀 복합'},
    'wibiathlon': {'individual': '개인', 'sprint': '스프린트', 'pursuit': '추적', 'mass start': '매스스타트', 'relay': '계주'},
    'wibobsleigh': {'two-man': '남자 2인승', 'four-man': '남자 4인승', 'two-woman': '여자 2인승', "women's monobob": '여자 모노봅'},
    'wicrosscountry': {'sprint classical': '스프린트', 'team sprint freestyle': '팀 스프린트', '10 kilometre freestyle': '10km',
                       '20 kilometre skiathlon': '스키애슬론', '50 kilometre classical': '매스스타트', '4 × 7.5 kilometre relay': '계주'},
    'wicurling': {'men': '남자', 'women': '여자', 'mixed doubles': '믹스더블'},
    'wifigure': {"men's singles": '남자 싱글', "women's singles": '여자 싱글', 'pairs': '페어', 'ice dance': '아이스댄스', 'team event': '단체전'},
    'wifreestyle': {'moguls': '모굴', 'dual moguls': '듀얼 모굴', 'aerials': '에어리얼', 'ski cross': '스키 크로스', 'halfpipe': '하프파이프',
                    'slopestyle': '슬로프스타일', 'big air': '빅에어', 'team aerials': '혼성 에어리얼 단체'},
    'wiicehockey': {"men's": '남자', "women's": '여자'},
    'wiluge': {"men's singles": '남자 싱글', "men's doubles": '남자 더블', "women's singles": '여자 싱글', "women's doubles": '여자 더블',
               'team relay': '팀 릴레이'},
    'wishorttrack': {'500 metres': '500m', '1000 metres': '1000m', '1500 metres': '1500m', '5000 metre relay': '5000m 계주',
                     '3000 metre relay': '3000m 계주', '2000 metre relay': '혼성 팀 계주'},
    'wiskeleton': {"men's": '남자', "women's": '여자', 'mixed team': '혼성 단체'},
    'wiskijumping': {"men's normal hill individual": '남자 노멀힐', "men's large hill individual": '남자 라지힐',
                     "men's large hill super team": '남자 슈퍼팀', "women's normal hill individual": '여자 노멀힐',
                     "women's large hill individual": '여자 라지힐', 'mixed normal hill team': '혼성 단체'},
    'wiskimountaineering': {"men's": '남자 스프린트', "women's": '여자 스프린트', 'mixed team': '혼성 계주'},
    'wisnowboard': {'parallel giant slalom': '평행 대회전', 'snowboard cross': '스노보드 크로스', 'halfpipe': '하프파이프',
                    'slopestyle': '슬로프스타일', 'big air': '빅에어', 'team snowboard cross': '혼성 단체 스노보드 크로스'},
    'wispeedskating': {'500 metres': '500m', '1000 metres': '1000m', '1500 metres': '1500m', '3000 metres': '3000m', '5000 metres': '5000m',
                       '10,000 metres': '10000m', 'mass start': '매스스타트', 'team pursuit': '팀 추월'},
}
ALIAS = {'혼성 2000m 계주': '혼성 팀 계주'}  # 허브 표의 행 이름 → 세부종목 이름
# 확인된 한글 이름 (허브 '대한민국' 섹션의 2026 결과 표기와 같다)
KO = {'Kim Gil-li': '김길리', 'Choi Min-jeong': '최민정', 'Hwang Dae-heon': '황대헌', 'Rim Jong-un': '임종언',
      'Kim Sang-kyum': '김상겸', 'Choi Ga-on': '최가온', 'Yu Seung-eun': '유승은'}


# ---------- Wikipedia 메달 표 읽기 ----------
LINK = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]')
FLAG = re.compile(r'\{\{\s*flag(\w*)\s*\|([^{}]*)\}\}', re.I)
OTHER = re.compile(r'\{\{(?!\s*flag)[^{}]*\}\}', re.I)


def entries(cell):
    """메달 칸 하나 → [(NOC, [이름, ...]), ...] (공동 메달이면 여럿)."""
    cell = LINK.sub(lambda m: m.group(1), cell)
    for _ in range(3):
        cell = OTHER.sub('', cell)  # ref label · DetailsLink · Plainlist 같은 틀
    out, marks = [], list(FLAG.finditer(cell))
    for i, m in enumerate(marks):
        args = [a.strip() for a in m.group(2).split('|')]
        tail = cell[m.end():marks[i + 1].start() if i + 1 < len(marks) else len(cell)]
        if 'medalist' in m.group(1).lower() or 'athlete' in m.group(1).lower():
            noc, names = args[1], [n.strip() for n in re.split(r'<br\s*/?>', args[0]) if n.strip()]  # 페어·아이스댄스는 한 칸에 두 이름
        else:
            noc = args[0]
            names = [re.sub(r"<[^>]+>|'''?|^\*\s*", '', n).strip() for n in re.split(r'<br\s*/?>|\n', tail)]
            names = [n for n in names if n and not n.startswith(('|', '}', '{'))]
        if re.fullmatch(r'[A-Z]{3}\d?', noc):
            out.append((noc, names))
    return out


def medal_tables(text):
    """[(절 제목, 종목 이름, [금, 은, 동 칸의 entries])]."""
    res = []
    text = re.sub(r'\{\{\s*nowrap\s*\|([^{}]*)\}\}', r'\1', text, flags=re.I)
    tables = [m for m in re.finditer(r'\{\|[^\n]*(?:MedalistTable|wikitable).*?\n\|\}', text, re.S)
              if 'MedalistTable' in m.group(0)[:200] or re.search(r"Gold'*\s*\n.*Silver", m.group(0)[:900], re.S)]
    for m in tables:
        heads = re.findall(r'\n(={2,5})\s*([^=\n]+?)\s*\1', text[:m.start()])
        section = heads[-1][1] if heads else ''
        for row in re.split(r'\n\|-[^\n]*', m.group(0))[1:]:
            lines = [l for l in re.split(r'\n(?=[|!])', row.strip('\n')) if l.strip()]
            if not lines:
                continue
            first = re.sub(r'^(?:\s*[a-z]+\s*=\s*"[^"]*"\s*)+\|', '', lines[0].lstrip('|! '))  # scope="row" style="…" | 이름
            label = re.sub(r"<br.*|\{\{.*|'''?", '', LINK.sub(lambda x: x.group(1), first), flags=re.S).strip()
            cells = [entries(l.split('||')[0]) for l in lines[1:]]
            cells = [c for c in cells if c]
            if label and cells:
                res.append((section, label, cells))
    return res


def show(cell, ko):
    """entries → 표에 적는 문자열."""
    parts = []
    for noc, names in cell:
        if not names or len(names) > 3:
            parts.append(noc)
        else:
            parts.append(f'{"·".join(ko.get(n, n) if noc == "KOR" else n for n in names)} ({noc})')
    return ' / '.join(parts)


def fetch():
    sys.path.insert(0, str(Path(__file__).parent))
    import wikiresults
    reg = json.loads((ROOT / 'data/olympic-structure.json').read_text(encoding='utf-8'))
    sports = {s['file']: s for s in _sports(reg)}
    out = {}
    for file, page in PAGES.items():
        title = f'{page} at the 2026 Winter Olympics'
        found = {}
        for section, label, cells in medal_tables(wikiresults.fetch(title)):
            ko = EVENT[file].get(label.lower())
            if not ko:
                print(f'{file}: 대응하는 세부종목 없음 → {section} | {label}', file=sys.stderr)
                continue
            sex = '남자 ' if section.lower().startswith('men') else '여자 ' if section.lower().startswith('women') else '혼성 ' if section.lower().startswith('mixed') else ''
            name = ko if ko.startswith(('남자', '여자', '혼성', '믹스', '페어', '아이스', '단체', '팀 릴레이')) else sex + ko
            medals = [show(c, KO) for c in cells[:3]]
            found[name] = {'en': f'{section} | {label}', 'medals': medals + [''] * (3 - len(medals))}
        rows = []
        for e in sports[file]['events']:
            f = found.pop(e['name'], None)
            rows.append({'label': e['name'], 'in2026': bool(f), **(f or {'medals': []})})
        for name in found:
            print(f'{file}: 허브에 없는 2026 종목 → {name}', file=sys.stderr)
        out[file] = rows
        print(f'{file}: {sum(r["in2026"] for r in rows)}/{len(rows)} 세부종목')
    for file, s in sports.items():  # 2026 대회에 없던 종목 (프리라이딩)
        if file.startswith('wi') and file not in out:
            out[file] = [{'label': e['name'], 'in2026': False, 'medals': []} for e in s['events']]
            print(f'{file}: 2026 대회에 없던 종목 ({len(s["events"])}개 세부종목)')
    DATA.write_text(json.dumps({
        '_note': f'2026 밀라노·코르티나 올림픽 메달리스트. Wikipedia 각 종목 메달 표({dt.date.today():%Y.%m.%d} 확인)에서 뽑았다. '
                 'in2026=false는 2026 대회에 없던 2030 세부종목. 3명 이하는 선수 이름, 그보다 큰 팀은 NOC, 공동 메달은 " / ". 빈 칸은 공동 수상으로 수여되지 않은 메달.',
        'source': 'https://en.wikipedia.org/wiki/<Sport>_at_the_2026_Winter_Olympics', 'ko': KO, 'medals': out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def _sports(reg):
    if isinstance(reg, dict):
        if 'file' in reg and 'events' in reg:
            yield reg
        for v in reg.values():
            yield from _sports(v)
    elif isinstance(reg, list):
        for v in reg:
            yield from _sports(v)


# ---------- 허브 표 채우기 ----------
def label_of(tr):
    m = re.match(r'<tr><th[^>]*>((?:(?!</th>).)*)</th>', tr, re.S)
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else None


def apply(text, rows):
    sec = re.search(r'<section id="previous"[^>]*>.*?</section>', text, re.S)
    tb = sec and re.search(r'<tbody>(.*?)</tbody>', sec.group(0), re.S)
    if not tb:
        return text, [r['label'] for r in rows]
    by_label = {r['label']: r for r in rows}
    out, seen = [], set()
    if not any(r['in2026'] for r in rows):  # 종목 전체가 2026 대회에 없었다 (프리라이딩)
        s = sec.group(0)
        s = s[:tb.start(1)] + '\n<tr><td colspan="4">2026 대회에 없던 종목이다.</td></tr>\n' + s[tb.end(1):]
        return text[:sec.start()] + s.replace('\n' + NOTE, '') + text[sec.end():], []
    for tr in TR.findall(tb.group(1)):
        lab = label_of(tr)
        r = by_label.get(ALIAS.get(lab, lab))
        if r:
            th = re.match(r'<tr>(<th[^>]*>.*?</th>)', tr, re.S).group(1)
            cells = ''.join(f'<td>{E(m) if m else "—"}</td>' for m in r['medals']) if r['in2026'] else ABSENT
            tr = f'<tr>{th}{cells}</tr>\n'
            seen.add(r['label'])
        out.append(tr)
    s = sec.group(0)
    s = s[:tb.start(1)] + '\n' + ''.join(out) + s[tb.end(1):]
    s = s.replace('\n' + NOTE, '').replace(NOTE, '')
    end = '</table></div><!-- /tw -->' if '</table></div><!-- /tw -->' in s else '</table>'
    s = s.replace(end, end + '\n' + NOTE, 1)
    return text[:sec.start()] + s + text[sec.end():], [l for l, r in by_label.items() if l not in seen and r['in2026']]


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))['medals']
    for file, rows in data.items():
        page = ROOT / f'{file}.html'
        orig = page.read_text(encoding='utf-8')
        new, miss = apply(orig, rows)
        if new != orig:
            page.write_text(new, encoding='utf-8', newline='\n')
        if miss:
            print(file, '표에 넣지 못한 행:', miss)
    print(len(data), '종목')


if __name__ == '__main__':
    fetch() if sys.argv[1:] == ['fetch'] else main()
