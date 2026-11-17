"""세부종목 문서 첫머리(intro)를 '경기 방식' 설명으로 맞춘다.

    python tools/event_intro.py          # 대상 종목의 세부종목 문서를 고친다 (여러 번 실행해도 같다)

intro는 "이 세부종목이 무엇인지, 몇 명이 어떻게 겨루는지"를 적는 자리다 (원칙 7장).
유도·양궁·펜싱·역도·레슬링 문서에는 이 자리에 선수 근황 메모가 들어가 있었다.
그 메모는 지우지 않고 '주목 선수' 섹션 첫머리의 "최근 동향"으로 옮긴다.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = lambda s: html.escape(str(s), quote=False)
INTRO = re.compile(r'(<section id="intro"[^>]*>\n?)(.*?)(</section>)', re.S)
MARK = '<h3>경기 방식</h3>'


def judo(e):
    if e['file'] == 'mixedteam':
        return ('남자 3체급(-73kg · -90kg · +90kg)과 여자 3체급(-57kg · -70kg · +70kg) 선수 6명이 한 팀을 이루는 혼성 단체전이다. '
                '여섯 경기 가운데 4승을 먼저 거둔 팀이 이긴다. 3-3으로 비기면 추첨으로 정한 체급의 선수가 골든스코어로 다시 겨뤄 승부를 가린다.')
    m = re.search(r'([+-])(\d+)kg', e['name'])
    cls = f'{m.group(2)}kg {"초과" if m.group(1) == "+" else "이하"}급'
    return (f'{e["name"][:2]} {cls} 개인전이다. 한 경기는 4분이며, 승부가 나지 않으면 시간 제한 없는 골든스코어로 이어진다. '
            '단판 토너먼트로 치르고, 8강에서 진 선수는 패자부활전을 거쳐 동메달 결정전에 나간다(동메달 2개). 국가당 1명이 출전한다.')


def archery(e):
    n = e['name']
    if '컴파운드' in n:
        return ('컴파운드 활로 50m 거리의 과녁을 쏘는 혼성 단체전으로, LA28에서 처음 열린다. 남녀 1명씩 한 팀을 이룬다. '
                '리커브와 달리 세트제가 아니라 4엔드 16발(선수당 2발씩)의 합계 점수로 승부를 가리고, 동점이면 슛오프를 한다.')
    base = '리커브 활로 70m 거리의 과녁(지름 122cm)을 쏜다. 72발 랭킹 라운드로 시드를 정한 뒤 단판 토너먼트를 치른다. '
    if '개인' in n:
        return base + '경기는 세트제다. 세트마다 3발씩 쏴 이기면 2점, 비기면 1점을 얻고 6점을 먼저 얻으면 이긴다. 5-5가 되면 한 발 슛오프로 가린다.'
    if '혼성' in n:
        return base + '남녀 1명씩 한 팀이다. 세트마다 4발(선수당 2발)을 쏴 이기면 2점, 비기면 1점을 얻고 5점을 먼저 얻으면 이긴다. 4-4가 되면 슛오프로 가린다.'
    return base + '3명이 한 팀이다. 세트마다 6발(선수당 2발)을 쏴 이기면 2점, 비기면 1점을 얻고 5점을 먼저 얻으면 이긴다. 4-4가 되면 슛오프로 가린다.'


WEAPON = {
    '에페': '에페는 온몸이 유효면이고 찌르기만 인정한다. 공격 우선권이 없어 동시에 찌르면 두 선수 모두 점수를 얻는다.',
    '플뢰레': '플뢰레는 몸통만 유효면이고 찌르기만 인정한다. 동시에 찌르면 공격 우선권을 가진 선수가 점수를 얻는다.',
    '사브르': '사브르는 허리 위 상체가 유효면이고 찌르기와 베기를 모두 인정한다. 동시에 맞으면 공격 우선권을 가진 선수가 점수를 얻는다.',
}


def fencing(e):
    w = next(k for k in WEAPON if k in e['name'])
    if '단체' in e['name']:
        return (f'{WEAPON[w]} 단체전은 3명(후보 1명)이 상대 3명과 번갈아 아홉 번 겨루는 릴레이 방식이다. '
                '점수를 이어받아 45점을 먼저 얻거나 아홉 번째 경기가 끝났을 때 앞선 팀이 이긴다.')
    rest = '8점에 이르면 한 번 쉰다' if w == '사브르' else '3분씩 3회전으로 치른다'
    return f'{WEAPON[w]} 개인전은 단판 토너먼트이며 15점을 먼저 얻는 선수가 이긴다({rest}).'


def weightlifting(e):
    return (f'{e["name"]}급이다. 인상과 용상을 각각 세 번씩 시도해, 두 종목 최고 기록을 더한 합계로 순위를 정한다. '
            '합계가 같으면 그 기록을 먼저 든 선수가 앞선다. 올림픽에서는 합계에만 메달이 걸린다.')


def wrestling(e):
    n = e['name']
    if '그레코로만' in n:
        style, gap = '그레코로만형은 허리 위 상체만 공격할 수 있고 다리를 쓰는 기술은 금지된다.', 8
    else:
        style, gap = '자유형은 다리를 포함해 온몸을 공격할 수 있다.', 10
    return (f'{style} 3분 2회전으로 치르고 점수가 많은 선수가 이긴다. 폴을 따내거나 {gap}점 차로 앞서면 그 자리에서 경기가 끝난다. '
            '단판 토너먼트이며, 결승에 오른 두 선수에게 진 선수들이 패자부활전을 치러 동메달 2개를 가린다.')


SPORTS = {'oljudo': judo, 'olarchery': archery, 'olfencing': fencing, 'olweightlifting': weightlifting, 'olwrestling': wrestling}


def _sports(reg):
    if isinstance(reg, dict):
        if 'file' in reg and 'events' in reg:
            yield reg
        for v in reg.values():
            yield from _sports(v)
    elif isinstance(reg, list):
        for v in reg:
            yield from _sports(v)


def apply(text, overview):
    m = INTRO.search(text)
    if not m or MARK in m.group(2):
        return text
    old = re.sub(r'<h3>개요</h3>', '', m.group(2)).strip()
    text = text[:m.start()] + m.group(1) + f'{MARK}\n<p>{E(overview)}</p>\n' + m.group(3) + text[m.end():]
    plain = re.sub(r'<[^>]+>', '', old).strip()
    if plain and '<!--' not in old:  # 예전 메모는 주목 선수 섹션으로 옮긴다
        note = f'<p class="note"><b>최근 동향</b> {old}</p>\n'
        text, n = re.subn(r'(<section id="athletes"[^>]*>\n<h2>[^<]*</h2>\n)', lambda a: a.group(1) + note, text, count=1)
        if not n:
            raise ValueError('주목 선수 섹션이 없어 메모를 옮길 수 없다')
    return text


def main():
    reg = json.loads((ROOT / 'data/olympic-structure.json').read_text(encoding='utf-8'))
    for s in _sports(reg):
        fn = SPORTS.get(s['file'])
        if not fn:
            continue
        changed = moved = 0
        for e in s['events']:
            path = ROOT / s['file'] / f'{e["file"]}.html'
            orig = path.read_text(encoding='utf-8')
            new = apply(orig, fn(e))
            if new != orig:
                path.write_text(new, encoding='utf-8', newline='\n')
                changed += 1
                moved += '<b>최근 동향</b>' in new and '<b>최근 동향</b>' not in orig
        print(f'{s["file"]}: {changed}개 문서 개요 교체, 메모 {moved}개 이동')


if __name__ == '__main__':
    main()
