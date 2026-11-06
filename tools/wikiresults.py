"""위키백과(영문) 대회 문서의 위키텍스트에서 메달리스트·메달 순위·올림픽 출전권 표를 읽는다.

    python tools/wikiresults.py "2026 ISSF World Shooting Championships"   # 읽은 결과를 보여 준다

- medalists(text): MedalistTable 표 → [{section, group, event, medals: [{names, noc, mark}]}]
  아직 치르지 않은 종목은 medals가 빈 목록이다(일정 확인용).
- medal_table(text): {{Medals table}} → [(NOC, 금, 은, 동)]
- quotas(text): '올림픽 출전권(Olympic qualification·Quota)' 절의 표 → [(종목, 자리 수, [NOC, ...])]
"""
import re, sys, time, urllib.error, urllib.parse, urllib.request

UA = 'KoreaOlympicsSiteBot/1.0 (+https://koreaolympics.github.io)'
LINK = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]')
FLAG = re.compile(r'\{\{\s*(?:(GYM National Team|flagicon|flagIOC2medalist|flagIOCmedalist|flagmedalist|flagIOC2athlete|flagIOCathlete|flagathlete|flagIOC2team|flagIOCteam|flagteam|flagOCA|flagPASO|flagCGF|flagIOC2|flagIOC|flag IOC|flagcountry|flagCountry|flag)\s*\||(?=[A-Z]{3}\}\}))([^{}]*)\}\}')
BR = re.compile(r'<br\s*/?\s*>', re.I)


def fetch(title, tries=5):
    url = 'https://en.wikipedia.org/w/index.php?' + urllib.parse.urlencode({'title': title, 'action': 'raw'})
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(1)  # 위키백과에 무리를 주지 않게 한 번에 하나씩
                return r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or k == tries - 1:
                raise
            time.sleep(10 * (k + 1))


def clean(s):
    s = re.sub(r'<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'\{\{\s*(?:nowrap|Nowrap|wrap|nobr|sortname)\s*\|([^{}|]*)(?:\|([^{}|]*))?[^{}]*\}\}',
               lambda m: (m.group(1) + (' ' + m.group(2) if m.group(2) and 'sortname' in m.group(0) else '')), s)
    s = re.sub(r'\{\{\s*nowrap (?:begin|end)\s*\}\}', '', s)
    s = re.sub(r'\{\{\s*(?:fbu?|fbwu?|fh|fhw|ru|rw|bk|bkw|vb|vbw|hb|hbw|wpo|wpow|crw?|lax)\s*\|(?:\d+\s*\|)?\s*([A-Z]{3})[^{}]*\}\}', r'{{flagteam|\1}}', s)  # 구기 국가 틀
    return s


def plain(s):
    s = re.sub(r'\{\{DetailsLink\|[^}]*\}\}', '', s)
    s = re.sub(r'\{\{(?:WR|OR|CR|AR|ER|NR|WJ|WB)\b[^}]*\}\}', lambda m: ' ' + m.group(0)[2:4].strip('|}'), s)
    s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    s = BR.sub(' ', LINK.sub(r'\1', s))
    s = re.sub(r"'''?|&nbsp;|\(\s*\)", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def cells_of(row):
    body = row.split('\n', 1)[1] if '\n' in row else ''
    while re.search(r'\{\{[^{}]*?\|\|', body):  # 틀 안의 빈 인자(||)는 칸 나눔이 아니다
        body = re.sub(r'(\{\{[^{}]*?)\|\|', r'\1| |', body)
    out = []
    for c in re.split(r'\n\||\|\|', '\n' + body.strip()):
        c = c.strip()
        if not c or c.startswith('}'):
            continue
        c = re.sub(r'^\s*(?:rowspan|colspan|style|valign|align|bgcolor)\s*=[^|{\[]*\|(?!\|)', '', c).strip()
        out.append(c)
    return out


def medal(cell):
    m = FLAG.search(cell)
    if not m:
        return None
    kind, args = (m.group(1) or '').replace(' ', ''), [a.strip() for a in LINK.sub(r'\1', m.group(2)).split('|')]
    if kind.endswith(('medalist', 'athlete')):
        noc = next((a for a in args[1:] if re.fullmatch(r'[A-Z]{3}', a)), '')
        names = [plain(x) for x in BR.split(args[0])]
        names = [n for n in names if n and not n.startswith('on ')]
        rest = [plain(x) for x in BR.split(cell[m.end():])]
        names += [n for n in rest if n and not re.match(r'^[\d(]', n) and not n.startswith('on ')]
    else:
        noc = args[0] if re.fullmatch(r'[A-Z]{3}', args[0]) else ''
        names = [plain(x) for x in re.split(r'<br\s*/?\s*>|\n|\*', cell[m.end():], flags=re.I)]
        names = [re.sub(r'\s*\([\d.:,]+\)$', '', n.lstrip('}| ')).strip() for n in names]  # 계영 구간 기록 '(57.66)'은 뗀다
        names = [n for n in names if n and not n.startswith(('on ', '(')) and not re.match(r'^[\d.,]+\s*(kg|pts?)?$', n)]
    names = [re.sub(r'\s*\([\d.:,]+\)$', '', n).strip('{}| ').strip() for n in names]  # 계영 구간 기록 '(57.66)'은 뗀다
    return {'names': [n for n in names if n], 'noc': noc, 'mark': ''}


def medalists(text):
    text = clean(text)
    res = []
    tables = [m for m in re.finditer(r'\{\|[^\n]*(?:MedalistTable|wikitable).*?\n\|\}', text, re.S)
              if 'MedalistTable' in m.group(0)[:200] or re.search(r"Gold'*\s*\n.*Silver", m.group(0)[:900], re.S)]
    for m in tables:
        heads = re.findall(r'\n(={2,4})\s*([^=\n]+?)\s*\1', text[:m.start()])
        section = heads[-1][1] if heads else ''
        group = ''
        for row in re.split(r'\n\|-[^\n]*', m.group(0))[1:]:
            row = row.strip('\n')
            if row.startswith('!'):
                first, _, rest = row.partition('\n')
                head = plain(re.sub(r'^!\s*(?:[a-z]+\s*=[^|]*\|(?!\|))*', '', first))
                if not FLAG.search(rest):
                    if head and head.lower() not in ('event', 'events'):
                        group = head
                    continue
                row = '| ' + head + '\n' + rest
            cells = cells_of('\n' + row.strip('\n')) if not row.startswith('\n') else cells_of(row)
            if not cells:
                continue
            if not FLAG.search(cells[0]):
                label, cells = plain(cells[0]), cells[1:]
            elif res:  # 이어지는 줄(동메달 둘째 자리)
                res[-1]['medals'] += [x for x in map(medal, cells) if x]
                continue
            else:
                label = ''
            meds = []
            for c in cells:
                x = medal(c)
                if x:
                    meds.append(x)
                elif meds and c.strip() and not meds[-1]['mark']:
                    meds[-1]['mark'] = plain(c)
            if not label and not meds:
                continue
            ev = f'{group} {label}'.strip() if group else label
            res.append({'section': section, 'group': group, 'event': ev, 'medals': meds})
    return res


def season(text):
    """시즌 문서(월드컵 등): 종목마다 '! colspan | 종목' 머리와 차수별 줄 → [{section, event, stage, venue, medals}]"""
    text = clean(text)
    out = []
    for t in re.finditer(r'\n\{\|[^\n]*wikitable[^\n]*\n!\s*colspan\s*=\s*"?\d"?\s*\|([^\n]*)(.*?)\n\|\}', text, re.S):
        heads = re.findall(r'\n(={2,4})\s*([^=\n]+?)\s*\1', text[:t.start()])
        h2 = max((i for i, h in enumerate(heads) if len(h[0]) == 2), default=-1)
        sub = next((h[1] for h in reversed(heads[h2 + 1:]) if len(h[0]) == 3), '')
        section = ' '.join(x for x in (heads[h2][1] if h2 >= 0 else '', sub) if x)
        event = plain(t.group(1))
        for row in re.split(r'\n\|-[^\n]*', t.group(2))[1:]:
            m = re.match(r'\s*!\s*([^\n|]+)\n(.*)', row.strip('\n'), re.S)
            if not m or not re.match(r'\s*(\d+|Final)\s*$', m.group(1)):
                continue
            cells = cells_of('\n' + m.group(2))
            if not cells:
                continue
            venue = plain(re.sub(r'\{\{flagicon\|[^}]*\}\}', '', cells[0]))
            meds = [x for x in map(medal, cells[1:]) if x and x['noc']]
            out.append({'section': section, 'event': event, 'stage': m.group(1).strip(), 'venue': venue, 'medals': meds})
    return out


def medal_table(text):
    m = re.search(r'\{\{\s*Medals table(.*?)\n\}\}', text, re.S)
    if not m:
        return []
    get = lambda k, c: int((re.search(rf'\b{k}_{c}\s*=\s*(\d+)', m.group(1)) or [0, 0])[1])
    nocs = sorted(set(re.findall(r'\b(?:gold|silver|bronze)_([A-Z]{3})\b', m.group(1))))
    rows = [(c, get('gold', c), get('silver', c), get('bronze', c)) for c in nocs]
    return sorted((r for r in rows if sum(r[1:])), key=lambda r: (-r[1], -r[2], -r[3], r[0]))


def quotas(text):
    text = clean(text)
    m = re.search(r'\n==+\s*(?:Olympic qualification|Olympic quota[^=]*|Quota places[^=]*|Qualification for the 2028[^=]*)\s*==+(.*?)(?=\n==[^=]|\Z)', text, re.S | re.I)
    if not m:
        return []
    out = []
    for t in re.finditer(r'\{\|.*?\n\|\}', m.group(1), re.S):
        for row in re.split(r'\n\|-[^\n]*', t.group(0))[1:]:
            ev, n = None, None
            for c in cells_of('\n' + row.strip('\n')):
                if c.startswith('!'):
                    continue
                nocs = re.findall(r'\{\{\s*flag(?:IOC| IOC|country)?\s*\|([A-Z]{3})', c)
                p = plain(c)
                if nocs or (ev and n is not None and not p):
                    out.append((ev, n, nocs))
                    ev, n = None, None
                elif re.fullmatch(r'\d+', p):
                    n = int(p)
                elif p:
                    ev = p
    return [(e, n, l) for e, n, l in out if e]


if __name__ == '__main__':
    t = fetch(' '.join(sys.argv[1:]))
    for r in medalists(t):
        print(r['section'], '|', r['event'], '|', ' ; '.join(f'{"·".join(x["names"])} ({x["noc"]}) {x["mark"]}' for x in r['medals']))
    print(medal_table(t)[:10])
    for q in quotas(t):
        print(q)
