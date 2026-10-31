"""허브 '직전 올림픽 메달리스트' 표를 2024 파리 결과로 채운다 (data/paris2024-medals.json).

    python tools/paris_medals.py

- LA28에도 있는 세부종목: 기존 행(세부종목 링크)의 금·은·동 칸을 자료 값으로 바꾼다.
- 파리에만 있던 세부종목(경보, 경량급 조정, 바뀐 복싱 체급 등): 링크 없는 행으로 자료 순서에 맞춰 끼워 넣는다.
- LA28에서 새로 생긴 '신설' 행은 그대로 두고, 파리 체급과 맞지 않는 '해당 없음' 행은 뺀다.
자료는 Wikipedia 각 종목 메달 표에서 뽑았다 (data 파일의 source 참고).
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = lambda s: html.escape(str(s), quote=False)
TR = re.compile(r'<tr>.*?</tr>\n?', re.S)
NOTE = '<p class="note paris-note">링크 없는 행은 LA28에 없는 파리 2024 세부종목이다. 출처: Wikipedia 각 종목 2024 하계 올림픽 메달 표.</p>'


def label_of(tr):
    m = re.match(r'<tr><th[^>]*>((?:(?!</th>).)*)</th>', tr, re.S)
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else None


def cells(medals):
    return ''.join(f'<td>{E(m) if m else "—"}</td>' for m in medals)


def apply(text, rows):
    sec = re.search(r'<section id="(?:previous|medals)"[^>]*>.*?</section>', text, re.S)
    if not sec:
        return text
    s = sec.group(0)
    tb = re.search(r'<tbody>(.*?)</tbody>', s, re.S)
    existing = [tr for tr in TR.findall(tb.group(1))]
    by_label = {r['label']: r for r in rows}
    out = []
    for tr in existing:
        lab = label_of(tr)
        if '파리 2024와 체급이 달라' in tr or 'class="paris-only"' in tr:
            continue  # 예전 안내 행·지난번에 넣은 파리 전용 행은 다시 만든다
        if lab in by_label and by_label[lab]['la28']:
            th = re.match(r'<tr>(<th[^>]*>.*?</th>)', tr, re.S).group(1)
            tr = f'<tr>{th}{cells(by_label[lab]["medals"])}</tr>\n'
        out.append([lab, tr])
    order = [r['label'] for r in rows]
    for i, r in enumerate(rows):  # 파리 전용 행을 앞 세부종목 다음에 넣는다
        if r['la28']:
            continue
        tr = [r['label'], f'<tr><th class="paris-only">{E(r["label"])}</th>{cells(r["medals"])}</tr>\n']
        prev = next((order[j] for j in range(i - 1, -1, -1) if any(l == order[j] for l, _ in out)), None)
        pos = 0 if prev is None else max(k for k, (l, _) in enumerate(out) if l == prev) + 1
        out.insert(pos, tr)
    body = s[:tb.start(1)] + '\n' + ''.join(t for _, t in out) + s[tb.end(1):]
    body = body.replace(NOTE, '')
    if any(not r['la28'] for r in rows):
        body = body.replace('</table></div><!-- /tw -->', '</table></div><!-- /tw -->\n' + NOTE, 1)
    return text[:sec.start()] + body + text[sec.end():]


def main():
    data = json.loads((ROOT / 'data/paris2024-medals.json').read_text(encoding='utf-8'))['medals']
    for file, rows in data.items():
        page = ROOT / f'{file}.html'
        orig = page.read_text(encoding='utf-8')
        new = apply(orig, rows)
        if new != orig:
            page.write_text(new, encoding='utf-8', newline='\n')
        found = {label_of(tr) for tr in TR.findall(new)}
        miss = [r['label'] for r in rows if r['label'] not in found]
        if miss:
            print(file, '표에 넣지 못한 행:', miss)
    print(len(data), '종목')


if __name__ == '__main__':
    main()
