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


def lane_of(when, name, prev):
    """시기 문자열 → 타임라인 칸 (상시 / 2026 / 2027 / 2028). 연도가 없으면 앞 경로와 같은 칸."""
    years = re.findall(r'20(2[6-8])', when)
    if years:
        return int('20' + years[0])
    if when in ('—', '') and re.search(r'개최국|보편성|초청|혼성 단체$', name):
        return 0
    return prev


def circuit_block(y, rows, total, label):
    """예선 연결도: 경로 상자를 시기 칸에 놓고, 각 상자에서 버스로 선을 이어 'LA28 본선'에 모은다.
    점선은 앞 경로에서 자리를 얻지 못한 국가·선수가 다음 경로로 넘어가는 흐름이다."""
    lanes, prev = [], 2026
    for when, name, _, _ in rows:
        lane = lane_of(when, name, prev)
        lanes.append(lane)
        prev = lane or prev
    used = sorted(set(lanes), key=lambda v: (v != 0, v))
    lane_w = 58
    lx = {v: PAD + 6 + i * lane_w for i, v in enumerate(used)}
    x_bus = W - PAD - 118
    pill = max([text_width(c, 12) for _, _, c, _ in rows if c] + [20]) + 16
    x_end = x_bus - pill - 18
    out = []
    # timeline header
    for v in used:
        out.append(t(lx[v] + 2, y, '상시' if v == 0 else str(v), 12, MUTED, 'bold'))
    if label:
        out.append(t(x_bus - 6, y, label, 12, MUTED, 'normal', 'end'))
    y += 12
    boxes, yy = [], y
    for (when, name, count, how), lane in zip(rows, lanes):
        x0 = lx[lane]
        names = wrap(name, 13, x_end - x0 - 20)
        sub = ' · '.join(v for v in (when if not re.fullmatch(r'—|', when) else '', how) if v)
        subs = wrap(sub, 11, x_end - x0 - 20) if sub else []
        h = 12 + 17 * len(names) + 15 * len(subs)
        boxes.append((x0, yy, h, count, lane))
        out.append(f'<rect x="{x0}" y="{yy}" width="{x_end - x0}" height="{h}" rx="5" fill="{BOX}" stroke="{BLUE}" stroke-width="1.2"/>')
        out += [t(x0 + 10, yy + 18 + 17 * k, line, 13, INK, 'bold') for k, line in enumerate(names)]
        out += [t(x0 + 10, yy + 17 * len(names) + 16 + 15 * k, line, 11, MUTED) for k, line in enumerate(subs)]
        yy += h + 14
    bottom = yy - 14
    # lane guides behind everything
    guides = [f'<line x1="{lx[v] - 3}" y1="{y - 4}" x2="{lx[v] - 3}" y2="{bottom}" stroke="#e3e6ea" stroke-dasharray="2 3"/>' for v in used]
    # carry-over (dashed): from box i to box i+1 when the next route is not a host/universality slot
    for (x0, y0, h, _, lane), (x1, y1, _, _, lane1) in zip(boxes, boxes[1:]):
        if lane == 0 or lane1 == 0: continue
        cx0, cx1 = x0 + 14, x1 + 14
        mid = y0 + h + 7
        out.append(f'<path d="M{cx0} {y0 + h} V{mid} H{cx1} V{y1}" fill="none" stroke="#8aa4c8" stroke-width="1.4" stroke-dasharray="4 3"/>')
    # wires into the bus, count pill on each wire
    for x0, y0, h, count, _ in boxes:
        cy = y0 + h / 2
        out.append(f'<line x1="{x_end}" y1="{cy:.0f}" x2="{x_bus}" y2="{cy:.0f}" stroke="{BLUE}" stroke-width="2"/>')
        out.append(f'<circle cx="{x_bus}" cy="{cy:.0f}" r="3.5" fill="{BLUE}"/>')
        if count:
            pw = text_width(count, 12) + 14
            px = x_end + 9 + (pill - pw) / 2
            out.append(f'<rect x="{px:.0f}" y="{cy - 10:.0f}" width="{pw:.0f}" height="20" rx="10" fill="#fff" stroke="{BLUE}"/>')
            out.append(t(px + pw / 2, cy + 4.5, count, 12, BLUE, 'bold', 'middle'))
    first, last = boxes[0][1] + boxes[0][2] / 2, boxes[-1][1] + boxes[-1][2] / 2
    out.append(f'<line x1="{x_bus}" y1="{first:.0f}" x2="{x_bus}" y2="{last:.0f}" stroke="{BLUE}" stroke-width="3"/>')
    # terminal: LA28 본선
    tl = wrap(total, 13, 88)
    th = 40 + 17 * len(tl)
    ty = (first + last) / 2 - th / 2
    out.append(f'<line x1="{x_bus}" y1="{(first + last) / 2:.0f}" x2="{x_bus + 14}" y2="{(first + last) / 2:.0f}" stroke="{BLUE}" stroke-width="3"/>')
    out.append(f'<rect x="{x_bus + 14}" y="{ty:.0f}" width="{W - PAD - x_bus - 14}" height="{th}" rx="8" fill="{BLUE}"/>')
    cxx = (x_bus + 14 + W - PAD) / 2
    out.append(t(cxx, ty + 22, 'LA28 본선', 14, '#fff', 'bold', 'middle'))
    out += [t(cxx, ty + 42 + 17 * k, line, 13, '#fff', 'normal', 'middle') for k, line in enumerate(tl)]
    out.append(t(PAD, bottom + 22, '점선: 앞 경로에서 자리를 얻지 못한 국가·선수가 다음 경로로 넘어간다.', 11, MUTED))
    return guides + out, bottom + 30 - (y - 12)


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
    out += heading(y, 'LA28 예선 연결도'); y += 30
    o, h = circuit_block(y, d['flow'], d['total'], d.get('flowlabel')); out += o; y += h + 16
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
