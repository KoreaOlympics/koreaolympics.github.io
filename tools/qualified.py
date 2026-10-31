"""LA28 출전 확정 현황 (data/la28-qualified.json → 허브 첫머리 표, 국기는 assets/flags/<NOC>.svg).

    python tools/qualified.py <flag-icons 폴더>   # 국기 SVG를 복사하고 허브 표를 넣거나 갱신한다
    python tools/qualified.py                     # 허브 표만 갱신 (국기는 이미 있을 때)

국기는 flag-icons(MIT, https://github.com/lipis/flag-icons)의 4x3 SVG를 IOC 코드 이름으로 저장한다.
표는 '한눈에 보기' 그림 다음, 목차 앞에 <div class="qualified">로 들어가며 tools/olympic.py build도 같은 자리에 다시 넣는다.
"""
import html, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/la28-qualified.json'
FLAGS = ROOT / 'assets/flags'
E = lambda s: html.escape(str(s), quote=True)
BLOCK_RE = re.compile(r'<div class="qualified" id="la28-qualified">.*?</div><!-- /qualified -->\n?', re.S)


def load():
    return json.loads(DATA.read_text(encoding='utf-8'))


def nation(noc, nocs):
    name, iso = nocs.get(noc, [noc, ''])
    flag = (f'<img class="flag" src="assets/flags/{noc}.svg" alt="" width="20" height="15">'
            if iso and (FLAGS / f'{noc}.svg').exists() else '<span class="flag none"></span>')
    return f'<span class="nat">{flag}{E(name)}</span> <span class="noc">{E(noc)}</span>'


def block(file, data=None):
    """허브 하나의 출전 확정 표. 자료가 없으면 ''."""
    data = data or load()
    d = data.get(file)
    if not d:
        return ''
    out = [f'<div class="qualified" id="la28-qualified"><h2>LA28 출전 확정 <span class="asof">{E(data["asof"])} 기준</span></h2>']
    for g in d['groups']:
        if g['rows']:
            rows = ''.join(f'<tr><td>{nation(noc, data["NOCS"])}</td><td>{E(route)}</td><td>{E(note)}</td></tr>' for noc, route, note in g['rows'])
        else:
            rows = '<tr><td colspan="3" class="muted">아직 확정된 자리가 없다.</td></tr>'
        out.append(f'<div class="tw"><table class="wikitable narrow"><caption>{E(g["title"])}</caption>'
                   f'<thead><tr><th>국가</th><th>경로</th><th>비고</th></tr></thead><tbody>{rows}</tbody></table></div>')
    if d.get('note'):
        out.append(f'<p class="note">{E(d["note"])}</p>')
    if d.get('sources'):
        out.append('<p class="src">출처: ' + ' · '.join(f'<a href="{E(u)}">{E(t)}</a>' for t, u in d['sources']) + '</p>')
    out.append('</div><!-- /qualified -->')
    return '\n'.join(out)


def copy_flags(src, data):
    FLAGS.mkdir(parents=True, exist_ok=True)
    used = {noc for k, v in data.items() if isinstance(v, dict) and 'groups' in v for g in v['groups'] for noc, _, _ in g['rows']}
    for noc in sorted(used):
        iso = data['NOCS'].get(noc, ['', ''])[1]
        if iso:
            shutil.copyfile(Path(src) / 'flags/4x3' / f'{iso}.svg', FLAGS / f'{noc}.svg')
    shutil.copyfile(Path(src) / 'LICENSE', FLAGS / 'LICENSE')


def main(argv):
    data = load()
    if argv:
        copy_flags(argv[0], data)
    n = 0
    for page in sorted(ROOT.glob('ol*.html')):
        orig = page.read_text(encoding='utf-8')
        text = BLOCK_RE.sub('', orig)
        b = block(page.stem, data)
        if b:
            anchor = '<div class="pathways"' if '<div class="pathways"' in text else '<nav class="toc">'  # 출전 확정 → 예선 단계 → 목차
            if anchor not in text:
                print('목차 없음, 건너뜀:', page.name); continue
            text = text.replace(anchor, b + '\n' + anchor, 1)
            n += 1
        if text != orig:
            page.write_text(text, encoding='utf-8', newline='\n')
    print(f'{n}개 허브에 출전 확정 표')


if __name__ == '__main__':
    main(sys.argv[1:])
