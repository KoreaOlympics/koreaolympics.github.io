"""종목 '문서 안내' (data/sport-guides.json).

    python tools/sport_guide.py

- 허브: 목차 앞에 <div class="guide" id="sport-guide"> — 갈래(예: 권총·소총·산탄총)별 세부종목 표
  (쿼터 · 파리 2024 금 · 한국 주요 선수 · 예선 대회별 바로가기 · 성적 상세)와 하위 문서 지도.
- 세부종목 문서: 목차 앞에 <div class="guide" id="event-guide"> — 이 종목의 갈래 문서, 대회별 결과(해당 종목 위치),
  한국 문서, 같은 갈래의 다른 세부종목.
tools/olympic.py build도 같은 자리에 다시 넣는다.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/sport-guides.json'
E = lambda s: html.escape(str(s), quote=True)
HUB_RE = re.compile(r'<div class="guide" id="sport-guide">.*?</div><!-- /guide -->\n?', re.S)
EV_RE = re.compile(r'<div class="guide" id="event-guide">.*?</div><!-- /guide -->\n?', re.S)


def load():
    return json.loads(DATA.read_text(encoding='utf-8'))


def paris_gold(file):
    p = ROOT / 'data/paris2024-medals.json'
    rows = json.loads(p.read_text(encoding='utf-8'))['medals'].get(file, []) if p.exists() else []
    return {r['label']: r['medals'][0] for r in rows}


def hub_block(file, data=None):
    data = data or load()
    g = data.get(file)
    if not g:
        return ''
    gold = paris_gold(file)
    stage_heads = ''.join(f'<th title="{E(d)}">{E(l)}</th>' for _, l, d in g['stages'])
    rows = []
    for grp in g['groups']:
        rows.append(f'<tr class="grp"><th colspan="{5 + len(g["stages"])}"><a href="{E(grp["doc"])}">{E(grp["name"])}</a> '
                    f'<span class="small">선발 경로·MQS·한국 전망 →</span></th></tr>')
        for ev in grp['events']:
            stages = ''.join(f'<td class="c"><a href="{E(u)}#event-{E(ev["code"])}">보기</a></td>' for u, _, _ in g['stages'])
            detail = g['detail'][0].format(code=ev['code'])
            quota = f'{ev["quota"]}명' if ev.get('quota') else '<span class="small">개인 출전자로 구성</span>'
            rows.append(f'<tr><th scope="row"><a href="{E(file)}/{E(ev["file"])}.html">{E(ev["label"])}</a></th>'
                        f'<td class="c">{quota}</td><td>{E(gold.get(ev["label"], "신설"))}</td><td>{E(ev.get("korea", ""))}</td>'
                        f'{stages}<td class="c"><a href="{E(detail)}">{E(g["detail"][1])}</a></td></tr>')
    table = (f'<div class="tw"><table class="wikitable guide-matrix"><thead><tr><th>세부종목</th><th>LA28 쿼터</th><th>파리 2024 금</th>'
             f'<th>한국 주요 선수</th>{stage_heads}<th>상세</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    cards = ''.join(
        f'<div class="guide-card"><h3>{E(c["title"])}</h3><ul>' +
        ''.join(f'<li><a href="{E(u)}">{E(l)}</a>' + (f' <span class="small">{E(d)}</span>' if d else '') + '</li>' for u, l, d in c['links']) +
        '</ul></div>' for c in g['docs'])
    return (f'<div class="guide" id="sport-guide"><h2>{E(g["title"])}</h2><p>{E(g["lead"])}</p>{table}'
            f'<div class="guide-cards">{cards}</div></div><!-- /guide -->')


def event_block(file, event_file, data=None, up='../'):
    data = data or load()
    g = data.get(file)
    if not g:
        return ''
    grp = next((x for x in g['groups'] if any(e['file'] == event_file for e in x['events'])), None)
    if not grp:
        return ''
    ev = next(e for e in grp['events'] if e['file'] == event_file)
    stages = ' · '.join(f'<a href="{up}{E(u)}#event-{E(ev["code"])}">{E(l)}</a>' for u, l, _ in g['stages'])
    korea = next((c for c in g['docs'] if c['title'] == '한국'), {'links': []})['links']
    sib = ' · '.join(f'<strong>{E(e["label"])}</strong>' if e is ev else f'<a href="{E(e["file"])}.html">{E(e["label"])}</a>' for e in grp['events'])
    rows = [('갈래', f'<a href="{up}{E(grp["doc"])}">{E(grp["name"])}</a> <span class="small">선발 경로·대회별 쿼터·MQS</span>'),
            ('대회별 결과', stages + f' · <a href="{up}{E(g["detail"][0].format(code=ev["code"]))}">{E(g["detail"][1])} 상세</a>'),
            ('한국', ' · '.join(f'<a href="{up}{E(u)}">{E(l)}</a>' for u, l, _ in korea) + (f' <span class="small">주요 선수: {E(ev["korea"])}</span>' if ev.get('korea') else '')),
            (f'같은 {grp["name"]}', sib),
            ('전체', f'<a href="{up}{E(file)}.html#sport-guide">{E(g["title"])}</a> · <a href="{up}olshooting-events.html">예선 대회 전체</a>' if file == 'olshooting'
                     else f'<a href="{up}{E(file)}.html#sport-guide">{E(g["title"])}</a>')]
    body = ''.join(f'<tr><th scope="row">{E(k)}</th><td>{v}</td></tr>' for k, v in rows)
    return f'<div class="guide" id="event-guide"><table class="guide-box"><caption>이 종목 문서</caption><tbody>{body}</tbody></table></div><!-- /guide -->'


def insert(text, regex, block):
    text = regex.sub('', text)
    anchor = next((a for a in ('<div class="results" id="recent-results">', '<nav class="toc">') if a in text), None)
    if block and anchor:  # 문서 안내 → 대회 결과 → 목차
        text = text.replace(anchor, block + '\n' + anchor, 1)
    return text


def main():
    data = load()
    n = 0
    for file, g in data.items():
        if file.startswith('_'):
            continue
        page = ROOT / f'{file}.html'
        orig = page.read_text(encoding='utf-8')
        new = insert(orig, HUB_RE, hub_block(file, data))
        if new != orig:
            page.write_text(new, encoding='utf-8', newline='\n')
        for grp in g['groups']:
            for ev in grp['events']:
                p = ROOT / file / f'{ev["file"]}.html'
                o = p.read_text(encoding='utf-8')
                nw = insert(o, EV_RE, event_block(file, ev['file'], data))
                if nw != o:
                    p.write_text(nw, encoding='utf-8', newline='\n')
                n += 1
    print(f'{len(data) - 1}개 종목 문서 안내 · 세부종목 {n}개')


if __name__ == '__main__':
    main()
