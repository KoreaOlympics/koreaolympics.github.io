"""개인중립선수(AIN)를 러시아·벨라루스로 나눠 적는다 (data/ain-athletes.json).

    python tools/ain.py          # 사이트 HTML·자료의 'AIN'을 확인된 선수만 'AIN·러시아'/'AIN·벨라루스'로 바꾼다 (여러 번 돌려도 같다)

확인이 안 되는 선수는 AIN 그대로 둔다.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KO = {'RUS': '러시아', 'BLR': '벨라루스'}
TOKEN = re.compile(r'(?<![A-Za-z0-9/._\-])AIN(?![A-Za-z0-9.\-_·])')


def load():
    return json.loads((ROOT / 'data/ain-athletes.json').read_text(encoding='utf-8'))['athletes']


def variants(name):
    """'Anton Aristarkhov' → 쓰이는 꼴들: 'Anton Aristarkhov', 'ARISTARKHOV Anton', 'Aristarkhov', 'ARISTARKHOV'."""
    given, sur = name.rsplit(' ', 1)
    return [name, f'{sur.upper()} {given}', f'{sur} {given}', sur.upper(), sur]


def country(names):
    """선수 이름 목록 → 'RUS'/'BLR' (모두 같은 나라로 확인될 때만), 아니면 None."""
    a = load()
    got = {a[n][0] for n in names if n in a}
    return got.pop() if len(got) == 1 and all(n in a for n in names) else None


def label(names):
    """표에 쓸 국가 이름: '중립(러시아)' 또는 None."""
    c = country(names)
    return f'중립({KO[c]})' if c else None


def tag_text(text):
    """HTML·자료 문자열 안의 AIN 중, 가까이(앞뒤 120자) 확인된 선수 이름이 있고 그 사이에 다른 국가 코드가 없는 것만 바꾼다."""
    a = load()
    pats = [(re.compile(r'(?<![A-Za-z])' + re.escape(v) + r'(?![a-z])'), n) for n in a for v in variants(n)]
    out, last = [], 0
    for m in TOKEN.finditer(text):
        best = None
        for pat, n in pats:
            for mm in pat.finditer(text, max(0, m.start() - 120), min(len(text), m.end() + 120)):
                gap = text[mm.end():m.start()] if mm.end() <= m.start() else text[m.end():mm.start()]
                if re.search(r'(?<![A-Za-z])[A-Z]{3}(?![A-Za-z])|</tr>|</li>|<br', re.sub(r'<[^>]*>', ' ', gap)) or len(gap) > 120:
                    continue
                d = len(gap)
                if best is None or d < best[0]:
                    best = (d, n)
        out.append(text[last:m.end()])
        if best:
            out.append('·' + KO[a[best[1]][0]])
        last = m.end()
    out.append(text[last:])
    return ''.join(out)


def main():
    n = 0
    files = [p for p in ROOT.glob('**/*.html') if '.git' not in p.parts] + [ROOT / f for f in ('data/paris2024-medals.json',)]
    for p in files:
        t = p.read_text(encoding='utf-8')
        if 'AIN' not in t:
            continue
        t2 = tag_text(t)
        if t2 != t:
            p.write_text(t2, encoding='utf-8', newline='\n')
            n += 1
            print(p.relative_to(ROOT))
    print(f'{n}개 파일')


if __name__ == '__main__':
    main()
