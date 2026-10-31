"""허브 '직전 올림픽 메달리스트' 표의 빈 칸을 채운다 (data/paris2024-medals.json).

    python tools/paris_medals.py

비어 있거나 '확인 필요'인 칸만 바꾸고, 이미 적힌 칸은 그대로 둔다.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = lambda s: html.escape(str(s), quote=False)
ROW = re.compile(r'(<tr><th[^>]*>)((?:(?!</?t[hrd][ >]).)*?)(</th>)((?:<td[^>]*>.*?</td>)+)(</tr>)', re.S)
TD = re.compile(r'<td([^>]*)>(.*?)</td>', re.S)


def fill(text, medals):
    sec = re.search(r'<section id="(?:previous|medals)"[^>]*>.*?</section>', text, re.S)
    if not sec:
        return text, 0
    n = 0
    def row(m):
        nonlocal n
        label = html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
        vals = medals.get(label)
        if not vals:
            return m.group(0)
        tds = TD.findall(m.group(4))
        if isinstance(vals, str):  # '@설명': 세 칸을 합친다
            if len(tds) == 3 and all(not c.strip() or c.strip() == '확인 필요' for _, c in tds):
                n += 1
                return f'{m.group(1)}{m.group(2)}{m.group(3)}<td colspan="3" class="muted">{E(vals[1:])}</td>{m.group(5)}'
            return m.group(0)
        if len(tds) != 3:
            return m.group(0)
        cells = []
        for (attrs, cur), new in zip(tds, vals):
            if new is not None and new != cur.strip() and (not cur.strip() or cur.strip() == '확인 필요'):
                cur = f'<span class="nat">{E(new[4:])}</span>' if new.startswith('nat:') else E(new)  # 단체 구기: 국가 이름
                n += 1
            cells.append(f'<td{attrs}>{cur}</td>')
        return f'{m.group(1)}{m.group(2)}{m.group(3)}{"".join(cells)}{m.group(5)}'
    body = ROW.sub(row, sec.group(0))
    return text[:sec.start()] + body + text[sec.end():], n


def main():
    data = json.loads((ROOT / 'data/paris2024-medals.json').read_text(encoding='utf-8'))['medals']
    total = 0
    for file, medals in data.items():
        page = ROOT / f'{file}.html'
        text, n = fill(page.read_text(encoding='utf-8'), medals)
        if n:
            page.write_text(text, encoding='utf-8', newline='\n')
        total += n
        missing = [k for k in medals if k not in html.unescape(re.sub(r'<[^>]+>', '', page.read_text(encoding='utf-8')))]
        if missing:
            print(file, '표에 없는 행:', missing)
    print(f'{total}칸 채움')


if __name__ == '__main__':
    main()
