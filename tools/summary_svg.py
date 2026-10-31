"""하계 종목 '한눈에 보기' 그림 (data/summer-summary.json → assets/summary/<file>.svg).

    python tools/summary_svg.py          # SVG를 만들고 허브 첫머리에 그림을 넣거나 갱신한다

그림 구성: 경기 방식(단계 흐름) · 핵심 규칙 3개 · LA28 예선 구조(경로를 순서대로: 시기·경로·자리·조건)
· 출전권 배분(막대). 허브에는
목차 바로 앞에 <figure class="summary-figure">로 들어가며, tools/olympic.py build도 같은 자리에 다시 넣는다.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/summer-summary.json'
OUT = ROOT / 'assets/summary'
W, PAD = 640, 20
FONT = "'Malgun Gothic','Apple SD Gothic Neo','Noto Sans KR',sans-serif"
INK, MUTED, LINE, BLUE, BOX = '#202122', '#54595d', '#c8ccd1', '#3265a8', '#eef3fa'
PALETTE = ['#3265a8', '#4f9a94', '#e0a42f', '#c9564c', '#8a6bbf', '#6b8e23', '#d97c3f', '#7b8794']
E = lambda s: html.escape(str(s), quote=True)


def text_width(s, size):
    w = 0
    for ch in s:
        if '가' <= ch <= '힣' or ch in '·→–': w += 1.0
        elif ch.isupper() or ch.isdigit(): w += 0.62
        elif ch == ' ': w += 0.3
        elif ch in '.,()/:': w += 0.35
        else: w += 0.55
    return w * size


def wrap(s, size, width):
    lines, cur = [], ''
    for word in s.split(' '):
        nxt = (cur + ' ' + word).strip()
        if cur and text_width(nxt, size) > width:
            lines.append(cur); cur = word
        else:
            cur = nxt
    return lines + [cur] if cur else lines


def t(x, y, s, size=14, fill=INK, weight='normal', anchor='start'):
    return f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{E(s)}</text>'


def heading(y, label):
    return [f'<rect x="{PAD}" y="{y - 13}" width="4" height="16" fill="{BLUE}"/>', t(PAD + 12, y, label, 15, BLUE, 'bold')]


def steps_block(y, steps):
    n = len(steps)
    gap = 22
    bw = (W - 2 * PAD - (n - 1) * gap) / n
    lines = [wrap(s, 13, bw - 16) for s in steps]
    h = 16 + 18 * max(len(l) for l in lines)
    out = []
    for i, (s, ls) in enumerate(zip(steps, lines)):
        x = PAD + i * (bw + gap)
        out.append(f'<rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="{h}" rx="6" fill="{BOX}" stroke="{BLUE}"/>')
        y0 = y + h / 2 - 9 * (len(ls) - 1) + 5
        out += [t(x + bw / 2, y0 + 18 * k, line, 13, INK, 'bold' if i == n - 1 else 'normal', 'middle') for k, line in enumerate(ls)]
        if i < n - 1:
            ax = x + bw + 5
            out.append(f'<path d="M{ax:.0f} {y + h / 2 - 6:.0f} L{ax + 11:.0f} {y + h / 2:.0f} L{ax:.0f} {y + h / 2 + 6:.0f}" fill="{BLUE}"/>')
    return out, h


def rules_block(y, rules):
    out, yy = [], y
    for i, r in enumerate(rules, 1):
        ls = wrap(r, 14, W - 2 * PAD - 34)
        out.append(f'<circle cx="{PAD + 10}" cy="{yy - 5}" r="10" fill="{BLUE}"/>')
        out.append(t(PAD + 10, yy, str(i), 12, '#fff', 'bold', 'middle'))
        out += [t(PAD + 30, yy + 20 * k, line, 14) for k, line in enumerate(ls)]
        yy += 20 * len(ls) + 8
    return out, yy - y


def flow_block(y, rows, label):
    """예선 경로를 우선순위 순서로: 번호 · 경로 이름 · 자리 수 · 시기와 조건."""
    out = []
    if label:
        out.append(t(W - PAD, y - 22, label, 12, MUTED, 'normal', 'end'))
    x0, x1 = PAD + 34, W - PAD
    yy = y
    for i, (when, name, count, how) in enumerate(rows, 1):
        sub = ' · '.join(x for x in (when if when not in ('—', '') else '', how) if x)
        cw = text_width(count, 13) + 20 if count else 0
        names = wrap(name, 14, x1 - x0 - 24 - cw)
        subs = wrap(sub, 12, x1 - x0 - 24) if sub else []
        h = 14 + 19 * len(names) + 17 * len(subs)
        if i < len(rows):
            out.append(f'<line x1="{PAD + 12}" y1="{yy + 12}" x2="{PAD + 12}" y2="{yy + h + 10}" stroke="{BLUE}" stroke-width="2"/>')
        out.append(f'<circle cx="{PAD + 12}" cy="{yy + 12}" r="11" fill="{BLUE}"/>')
        out.append(t(PAD + 12, yy + 16.5, str(i), 12, '#fff', 'bold', 'middle'))
        out.append(f'<rect x="{x0}" y="{yy}" width="{x1 - x0}" height="{h}" rx="6" fill="{BOX}" stroke="#d5deea"/>')
        out += [t(x0 + 12, yy + 20 + 19 * k, line, 14, INK, 'bold') for k, line in enumerate(names)]
        if count:
            out.append(f'<rect x="{x1 - cw - 8:.0f}" y="{yy + 6}" width="{cw:.0f}" height="22" rx="11" fill="{BLUE}"/>')
            out.append(t(x1 - 8 - cw / 2, yy + 21, count, 13, '#fff', 'bold', 'middle'))
        out += [t(x0 + 12, yy + 19 * len(names) + 18 + 17 * k, line, 12, MUTED) for k, line in enumerate(subs)]
        yy += h + 10
    return out, yy - y


def units_block(y, units):
    """체급·세부종목마다 쿼터가 따로 정해진 종목: 한 줄에 한 체급(세부종목), 같은 경로는 같은 색."""
    colors = {}
    for _, _, segs in units['rows']:
        for seg in segs:
            colors.setdefault(seg[0], PALETTE[len(colors) % len(PALETTE)])
    lw = max(text_width(r[0], 13) for r in units['rows']) + 12
    tw = max(text_width(r[1], 13) for r in units['rows']) + 10
    x0, x1 = PAD + lw, W - PAD - tw
    top = max(sum(seg[1] for seg in r[2]) for r in units['rows'])
    out = ['<defs><pattern id="var" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           '<rect width="6" height="6" fill="#e3e6ea"/><line x1="0" y1="0" x2="0" y2="6" stroke="#9aa1a9" stroke-width="3"/></pattern></defs>']
    yy = y
    for label, total, segs in units['rows']:
        out.append(t(PAD, yy + 15, label, 13, INK))
        x = x0
        for seg in segs:
            name, n, var = seg[0], seg[1], len(seg) > 2 and seg[2]
            w = (x1 - x0) * n / top
            out.append(f'<rect x="{x:.1f}" y="{yy}" width="{max(w - 1.5, 1):.1f}" height="20" fill="{"url(#var)" if var else colors[name]}"/>')
            if not var and text_width(str(n), 12) + 6 < w:
                out.append(t(x + w / 2, yy + 15, str(n), 12, '#fff', 'bold', 'middle'))
            x += w
        out.append(t(W - PAD, yy + 15, total, 13, BLUE, 'bold', 'end'))
        yy += 26
    ly, lx = yy + 12, PAD
    for name, c in colors.items():
        var = any(len(seg) > 2 and seg[2] for _, _, segs in units['rows'] for seg in segs if seg[0] == name)
        iw = 18 + text_width(name, 13) + 16
        if lx + iw > W - PAD:
            lx, ly = PAD, ly + 20
        out.append(f'<rect x="{lx:.0f}" y="{ly - 11}" width="12" height="12" rx="2" fill="{"url(#var)" if var else c}"/>')
        out.append(t(lx + 18, ly, name, 13))
        lx += iw
    yy = ly + 8
    for line in wrap(units.get('note', ''), 12, W - 2 * PAD) if units.get('note') else []:
        yy += 17
        out.append(t(PAD, yy, line, 12, MUTED))
    return out, yy - y + 10


def bar_block(y, bar):
    total = sum(n for _, n in bar['segs'])
    out = [t(PAD, y, bar['label'], 13, MUTED, 'bold')]
    y += 8
    x, width = PAD, W - 2 * PAD
    for i, (label, n) in enumerate(bar['segs']):
        w = width * n / total
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w - 1.5, 1):.1f}" height="26" fill="{PALETTE[i % len(PALETTE)]}"/>')
        if text_width(str(n), 13) + 8 < w:
            out.append(t(x + w / 2, y + 18, str(n), 13, '#fff', 'bold', 'middle'))
        x += w
    # legend: colored square + label n, flowing
    ly, lx = y + 46, PAD
    for i, (label, n) in enumerate(bar['segs']):
        item = f'{label} {n}'
        iw = 18 + text_width(item, 13) + 16
        if lx + iw > W - PAD:
            lx, ly = PAD, ly + 20
        out.append(f'<rect x="{lx:.0f}" y="{ly - 11}" width="12" height="12" rx="2" fill="{PALETTE[i % len(PALETTE)]}"/>')
        out.append(t(lx + 18, ly, item, 13))
        lx += iw
    return out, ly - (y - 8) + 10


def render(name, d):
    out, y = [], 38
    out.append(t(PAD, y, f'{name} 한눈에 보기', 22, INK, 'bold'))
    out.append(t(W - PAD, y, d['total'], 18 if text_width(d['total'], 18) < 330 else 15, BLUE, 'bold', 'end'))
    out.append(t(W - PAD, y + 20, 'LA28 출전 규모', 12, MUTED, 'normal', 'end'))
    y += 38
    out += heading(y, '경기 방식'); y += 14
    o, h = steps_block(y, d['steps']); out += o; y += h + 34
    out += heading(y, '핵심 규칙'); y += 28
    o, h = rules_block(y, d['rules']); out += o; y += h + 18
    out += heading(y, 'LA28 예선 구조 (위에서부터 차례로 배정)'); y += 30
    o, h = flow_block(y, d['flow'], d.get('flowlabel')); out += o; y += h + 16
    if d.get('pathnote'):
        out.append(t(PAD, y - 4, d['pathnote'], 12, MUTED)); y += 16
    if d.get('units'):
        out += heading(y, d['units']['title']); y += 16
        o, h = units_block(y, d['units']); out += o; y += h + 18
    if d.get('bars'):
        out += heading(y, '출전권 배분'); y += 26
        for bar in d['bars']:
            o, h = bar_block(y, bar); out += o; y += h + 22
    if d.get('barnote'):
        out.append(t(PAD, y, d['barnote'], 12, MUTED)); y += 18
    out.append(t(PAD, y + 6, '숫자는 이 문서의 예선 규정 정리 기준이다. 세부 조건과 출처는 본문에 있다.', 11, MUTED))
    H = y + 22
    body = '\n'.join(out)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{E(name)} 한눈에 보기" font-family="{FONT}"><title>{E(name)} 한눈에 보기</title>'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="#fff" stroke="{LINE}"/>\n{body}\n</svg>\n')


def alt_text(name, d):
    parts = [f'{name} 한눈에 보기. LA28 출전 규모 {d["total"]}.', '경기 방식: ' + ' → '.join(d['steps']) + '.',
             '핵심 규칙: ' + ' '.join(d['rules'])]
    for b in d.get('bars', []):
        parts.append(f'출전권 배정 ({b["label"]}): ' + ', '.join(f'{l} {n}' for l, n in b['segs']) + '.')
    if d.get('units'):
        parts.append(d['units']['title'] + ': ' + '; '.join(
            f'{label} {total} (' + ', '.join(f'{seg[0]} {"가변" if len(seg) > 2 and seg[2] else seg[1]}' for seg in segs) + ')'
            for label, total, segs in d['units']['rows']) + '.')
    parts.append('예선 구조 (차례대로): ' + '; '.join(
        ' '.join(x for x in (name, count, f'({when}{", " + how if how else ""})' if when not in ('—', '') else (f'({how})' if how else '')) if x)
        for when, name, count, how in d['flow']) + '.' + (' ' + d['pathnote'] if d.get('pathnote') else ''))
    return ' '.join(parts)


def figure(file, name, d):
    """허브 첫머리 그림 (tools/olympic.py도 이 함수를 쓴다)."""
    return (f'<figure class="summary-figure"><a href="assets/summary/{file}.svg"><img src="assets/summary/{file}.svg" '
            f'alt="{E(alt_text(name, d))}" loading="lazy"></a></figure>')


def load():
    return {k: v for k, v in json.loads(DATA.read_text(encoding='utf-8')).items() if not k.startswith('_')}


FIG_RE = re.compile(r'<figure class="summary-figure">.*?</figure>\n?', re.S)


def main():
    reg = json.loads((ROOT / 'data/olympic-structure.json').read_text(encoding='utf-8'))
    names = {s['file']: s['name'] for s in reg['summer']['sports']}
    data = load()
    OUT.mkdir(parents=True, exist_ok=True)
    for file, d in data.items():
        (OUT / f'{file}.svg').write_text(render(names[file], d), encoding='utf-8')
        page = ROOT / f'{file}.html'
        text = FIG_RE.sub('', page.read_text(encoding='utf-8'))
        fig = figure(file, names[file], d)
        if '<nav class="toc">' not in text:
            print('목차 없음, 건너뜀:', file); continue
        text = text.replace('<nav class="toc">', fig + '\n<nav class="toc">', 1)
        page.write_text(text, encoding='utf-8', newline='\n')
    missing = sorted(set(names) - set(data))
    print(f'{len(data)}개 그림 생성' + (f' · 자료 없음: {", ".join(missing)}' if missing else ''))


if __name__ == '__main__':
    main()
