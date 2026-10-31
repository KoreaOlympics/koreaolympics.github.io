"""구기 종목 'LA28 예선 단계' (data/team-pathways.json → assets/pathways/<file>.svg + 허브 표).

    python tools/pathways.py [flag-icons 폴더]

대륙 예선처럼 올림픽 예선 앞 단계까지 단계마다 상자로 잇는다. 상자 모양으로 상태를 나눈다:
종료(파란 칠) · 진행 중(빨간 테두리) · 예정(회색 점선). 상자 아래에 다음 단계 진출 방식과 한국 상황을 적는다.
허브에는 'LA28 출전 확정' 표 다음, 목차 앞에 <div class="pathways">로 들어가며 tools/olympic.py build도 같은 자리에 다시 넣는다.
"""
import html, json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from summary_svg import text_width, wrap, t, FONT, INK, MUTED, LINE, BLUE  # noqa: E402
import qualified  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/team-pathways.json'
OUT = ROOT / 'assets/pathways'
W, PAD = 640, 20
RED, KOR = '#c9302c', '#b3122e'
E = lambda s: html.escape(str(s), quote=True)
BLOCK_RE = re.compile(r'<div class="pathways" id="la28-pathways">.*?</div><!-- /pathways -->\n?', re.S)
STATUS = {'done': '종료', 'live': '진행 중', 'soon': '예정'}


def load():
    return json.loads(DATA.read_text(encoding='utf-8'))


def nocs():
    q = qualified.load()
    return {**q['NOCS'], **load().get('NOCS_EXTRA', {})}


def track_svg(y, track):
    """한 경로: 단계 상자를 왼쪽에서 오른쪽으로, 마지막에 LA28 상자."""
    stages = track['stages']
    n = len(stages) + 1
    gap = 16
    bw = (W - 2 * PAD - (n - 1) * gap) / n
    out = [t(PAD, y, track['title'], 14, INK, 'bold')]
    y += 12
    boxes = []
    for st in stages:
        names = wrap(st['name'], 12, bw - 12)
        whens = wrap(st['when'], 10.5, bw - 12)
        boxes.append((names, whens))
    bh = 16 + 15 * max(len(a) for a, _ in boxes) + 13 * max(len(b) for _, b in boxes) + 14
    below = []
    for i, (st, (names, whens)) in enumerate(zip(stages, boxes)):
        x = PAD + i * (bw + gap)
        if st['status'] == 'done':
            out.append(f'<rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="{bh}" rx="6" fill="#e6eef9" stroke="{BLUE}" stroke-width="1.5"/>')
        elif st['status'] == 'live':
            out.append(f'<rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="{bh}" rx="6" fill="#fff" stroke="{RED}" stroke-width="2"/>')
        else:
            out.append(f'<rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="{bh}" rx="6" fill="#fff" stroke="#9aa1a9" stroke-dasharray="4 3"/>')
        tag = STATUS[st['status']]
        color = {'done': BLUE, 'live': RED, 'soon': MUTED}[st['status']]
        out.append(t(x + bw - 6, y + 13, tag, 10, color, 'bold', 'end'))
        out += [t(x + 6, y + 28 + 15 * k, line, 12, INK, 'bold') for k, line in enumerate(names)]
        out += [t(x + 6, y + 28 + 15 * len(names) + 13 * k, line, 10.5, MUTED) for k, line in enumerate(whens)]
        lines = [(l, MUTED, 'normal') for l in wrap(st.get('advance', ''), 10.5, bw)]
        if st.get('kor'):
            lines += [(l, KOR, 'bold') for l in wrap('한국: ' + st['kor'], 10.5, bw)]
        below.append((x, lines))
        ax = x + bw + 3
        out.append(f'<path d="M{ax:.0f} {y + bh / 2 - 5:.0f} L{ax + 9:.0f} {y + bh / 2:.0f} L{ax:.0f} {y + bh / 2 + 5:.0f}" fill="{BLUE}"/>')
    x = PAD + len(stages) * (bw + gap)
    out.append(f'<rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="{bh}" rx="6" fill="{BLUE}"/>')
    out.append(t(x + bw / 2, y + bh / 2 + 5, 'LA28 본선', 13, '#fff', 'bold', 'middle'))
    deepest = 0
    for x, lines in below:
        for k, (line, color, weight) in enumerate(lines):
            out.append(t(x, y + bh + 16 + 14 * k, line, 10.5, color, weight))
        deepest = max(deepest, len(lines))
    return out, 12 + bh + 16 + 14 * deepest + 8


def render(name, d):
    out, y = [], 36
    out.append(t(PAD, y, f'{name} LA28 예선 단계', 20, INK, 'bold'))
    legend = [('#e6eef9', BLUE, '', '종료'), ('#fff', RED, '', '진행 중'), ('#fff', '#9aa1a9', '4 3', '예정')]
    lx = W - PAD - 190
    for fill, stroke, dash, label in legend:
        out.append(f'<rect x="{lx}" y="{y - 12}" width="16" height="12" rx="2" fill="{fill}" stroke="{stroke}"'
                   + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
        out.append(t(lx + 20, y - 2, label, 11, MUTED))
        lx += 20 + text_width(label, 11) + 14
    y += 30
    for track in d['tracks']:
        o, h = track_svg(y, track)
        out += o
        y += h + 14
    H = y + 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{E(name)} LA28 예선 단계" font-family="{FONT}"><title>{E(name)} LA28 예선 단계</title>'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="#fff" stroke="{LINE}"/>\n' + '\n'.join(out) + '\n</svg>\n')


def alt_text(name, d):
    parts = [f'{name} LA28 예선 단계.']
    for tr in d['tracks']:
        parts.append(tr['title'] + ': ' + ' → '.join(
            f'{st["name"]} ({st["when"]}, {STATUS[st["status"]]}{", " + st["advance"] if st.get("advance") else ""}'
            f'{", 한국 " + st["kor"] if st.get("kor") else ""})' for st in tr['stages']) + ' → LA28 본선.')
    return ' '.join(parts)


def block(file, data=None):
    data = data or load()
    d = data.get(file)
    if not d or file.startswith('_'):
        return ''
    reg = json.loads((ROOT / 'data/olympic-structure.json').read_text(encoding='utf-8'))
    name = next(s['name'] for s in reg['summer']['sports'] if s['file'] == file)
    codes = {**qualified.load()['NOCS'], **data.get('NOCS_EXTRA', {})}
    out = [f'<div class="pathways" id="la28-pathways"><h2>LA28 예선 단계 <span class="asof">{E(data["asof"])} 기준</span></h2>',
           f'<figure class="summary-figure"><a href="assets/pathways/{file}.svg"><img src="assets/pathways/{file}.svg" alt="{E(alt_text(name, d))}" loading="lazy"></a></figure>']
    for tr in d['tracks']:
        rows = []
        for st in tr['stages']:
            res = ', '.join(qualified.nation(noc, codes) + (f' <span class="small">{E(note)}</span>' if note else '')
                            for noc, note in st.get('result', []))
            rows.append(f'<tr class="st-{st["status"]}"><td>{E(st["name"])}</td><td class="nowrap">{E(st["when"])}</td><td>{E(STATUS[st["status"]])}</td>'
                        f'<td>{E(st.get("advance", ""))}</td><td>{res}</td><td>{E(st.get("kor", ""))}</td></tr>')
        out.append(f'<div class="tw"><table class="wikitable"><caption>{E(tr["title"])}</caption><thead><tr><th>단계</th><th>시기</th><th>상태</th>'
                   f'<th>다음 단계</th><th>결과·진출</th><th>한국</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    if d.get('note'):
        out.append(f'<p class="note">{E(d["note"])}</p>')
    if d.get('sources'):
        out.append('<p class="src">출처: ' + ' · '.join(f'<a href="{E(u)}">{E(t_)}</a>' for t_, u in d['sources']) + '</p>')
    out.append('</div><!-- /pathways -->')
    return '\n'.join(out)


def main(argv):
    data = load()
    reg = json.loads((ROOT / 'data/olympic-structure.json').read_text(encoding='utf-8'))
    names = {s['file']: s['name'] for s in reg['summer']['sports']}
    if argv:  # 표에 새로 나오는 국가의 국기
        for noc, (_, iso) in data.get('NOCS_EXTRA', {}).items():
            shutil.copyfile(Path(argv[0]) / 'flags/4x3' / f'{iso}.svg', qualified.FLAGS / f'{noc}.svg')
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for file, d in data.items():
        if file.startswith('_') or not isinstance(d, dict) or 'tracks' not in d:
            continue
        (OUT / f'{file}.svg').write_text(render(names[file], d), encoding='utf-8')
        page = ROOT / f'{file}.html'
        orig = page.read_text(encoding='utf-8')
        text = BLOCK_RE.sub('', orig)
        anchor = '<nav class="toc">'
        text = text.replace(anchor, block(file, data) + '\n' + anchor, 1)
        if text != orig:
            page.write_text(text, encoding='utf-8', newline='\n')
        n += 1
    print(f'{n}개 종목 예선 단계')


if __name__ == '__main__':
    main(sys.argv[1:])
