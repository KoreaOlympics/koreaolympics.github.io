"""한국 선수 한글 이름 (data/korean-names.json).

- 확인: 영문 위키백과 선수 문서의 {{Korean|hangul=…}}·native_name 등에서 한글을 읽는다 (find_hangul).
- 추정: 문서가 없으면 로마자 표기를 한글로 옮긴다 (guess). 추정 이름은 data/korean-names.json의 "guessed"에 두고
  화면에 점선 밑줄과 '로마자 표기에서 옮긴 이름' 설명을 붙인다. 확인되면 "names"로 옮긴다 (손으로 고쳐도 된다).

    python tools/korean_names.py "Kim Woo-jin" "Shin Minki"   # 추정 결과를 보여 준다
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/korean-names.json'

SURNAME = {
    'kim': '김', 'gim': '김', 'lee': '이', 'yi': '이', 'rhee': '이', 'ri': '이', 'park': '박', 'pak': '박', 'bak': '박',
    'choi': '최', 'choe': '최', 'jung': '정', 'jeong': '정', 'chung': '정', 'kang': '강', 'gang': '강', 'cho': '조', 'jo': '조',
    'yoon': '윤', 'yun': '윤', 'jang': '장', 'chang': '장', 'lim': '임', 'im': '임', 'han': '한', 'oh': '오', 'o': '오',
    'seo': '서', 'suh': '서', 'shin': '신', 'sin': '신', 'kwon': '권', 'gwon': '권', 'hwang': '황', 'ahn': '안', 'an': '안',
    'song': '송', 'jeon': '전', 'chun': '전', 'jun': '전', 'hong': '홍', 'yoo': '유', 'yu': '유', 'ryu': '류', 'ryoo': '류',
    'ko': '고', 'go': '고', 'koh': '고', 'moon': '문', 'mun': '문', 'yang': '양', 'son': '손', 'sohn': '손', 'bae': '배',
    'baek': '백', 'paik': '백', 'baik': '백', 'heo': '허', 'huh': '허', 'nam': '남', 'noh': '노', 'roh': '노', 'no': '노',
    'ha': '하', 'kwak': '곽', 'gwak': '곽', 'sung': '성', 'seong': '성', 'cha': '차', 'joo': '주', 'ju': '주', 'woo': '우',
    'min': '민', 'na': '나', 'ra': '라', 'jin': '진', 'ji': '지', 'eom': '엄', 'um': '엄', 'chae': '채', 'won': '원',
    'cheon': '천', 'bang': '방', 'gong': '공', 'kong': '공', 'hyun': '현', 'hyeon': '현', 'ham': '함', 'byeon': '변',
    'byun': '변', 'yeom': '염', 'yeo': '여', 'choo': '추', 'chu': '추', 'do': '도', 'so': '소', 'seok': '석', 'seon': '선',
    'sun': '선', 'seol': '설', 'ma': '마', 'gil': '길', 'kil': '길', 'yeon': '연', 'wi': '위', 'pyo': '표', 'myung': '명',
    'myeong': '명', 'ki': '기', 'gi': '기', 'ban': '반', 'wang': '왕', 'geum': '금', 'ok': '옥', 'yook': '육', 'yuk': '육',
    'maeng': '맹', 'je': '제', 'mo': '모', 'tak': '탁', 'guk': '국', 'bong': '봉', 'sa': '사', 'bu': '부', 'pyeon': '편',
    'hwangbo': '황보', 'namgung': '남궁', 'jegal': '제갈', 'seonu': '선우', 'dokgo': '독고', 'sagong': '사공',
    'jee': '지', 'shim': '심', 'sim': '심', 'nah': '나', 'lyu': '류', 'yim': '임', 'gu': '구', 'koo': '구', 'ku': '구',
    'kye': '계', 'gye': '계', 'hur': '허', 'joung': '정', 'youn': '윤', 'jeung': '정', 'chae-': '채', 'jeoung': '정', 'cheong': '정', 'eum': '음', 'bin': '빈', 'tae': '태', 'yeum': '염',
}
SYL = {  # 이름에 흔한 관용 표기 (규칙으로는 틀리기 쉬운 것)
    'gun': '건', 'geon': '건', 'kun': '건', 'hyun': '현', 'joon': '준', 'jun': '준', 'young': '영', 'yong': '용', 'sung': '성',
    'soo': '수', 'woo': '우', 'hee': '희', 'kyu': '규', 'kyung': '경', 'kyeong': '경', 'kyoung': '경', 'yoon': '윤',
    'yun': '윤', 'eun': '은', 'chul': '철', 'cheol': '철', 'suk': '석', 'sook': '숙', 'hoon': '훈', 'hun': '훈', 'jae': '재',
    'ji': '지', 'jee': '지', 'min': '민', 'jin': '진', 'ho': '호', 'won': '원', 'ki': '기', 'gi': '기', 'gyu': '규',
    'hyuk': '혁', 'hyeok': '혁', 'chan': '찬', 'seok': '석', 'jung': '정', 'jeong': '정', 'chang': '창', 'tae': '태',
    'moon': '문', 'koo': '구', 'goo': '구', 'joo': '주', 'ju': '주', 'yeon': '연', 'yeun': '연', 'seon': '선', 'sun': '선',
    'hye': '혜', 'hyo': '효', 'ha': '하', 'na': '나', 'ra': '라', 'rin': '린', 'in': '인', 'il': '일', 'bin': '빈', 'bo': '보',
    'ram': '람', 'reum': '름', 'ye': '예', 'yu': '유', 'yoo': '유', 'u': '우', 'wook': '욱', 'uk': '욱', 'wan': '완',
    'hwan': '환', 'kwang': '광', 'gwang': '광', 'dong': '동', 'do': '도', 'sang': '상', 'seung': '승', 'so': '소', 'song': '송',
    'si': '시', 'shi': '시', 'seo': '서', 'su': '수', 'ah': '아', 'a': '아', 'ae': '애', 'chae': '채', 'yeong': '영',
    'kook': '국', 'guk': '국', 'nam': '남', 'mi': '미', 'myung': '명', 'myeong': '명', 'jun-': '준', 'hyung': '형',
    'hyeong': '형', 'heon': '헌', 'beom': '범', 'bum': '범', 'pil': '필', 'sik': '식', 'shik': '식', 'oh': '오', 'o': '오',
    'eon': '언', 'gyeong': '경', 'jong': '종', 'chong': '종', 'chun': '춘', 'cheon': '천', 'geun': '근', 'keun': '근',
    'kyeom': '겸', 'gyeom': '겸', 'rok': '록', 'rak': '락', 'ri': '리', 'lee': '이', 'hak': '학', 'han': '한', 'hyeop': '협',
    'yeop': '엽', 'yup': '엽', 'chi': '치', 'ui': '의', 'eui': '의', 'saem': '샘', 'seul': '슬', 'byeol': '별', 'byul': '별',
    'bom': '봄', 'gyeol': '결', 'kyeol': '결', 'roo': '루', 'ru': '루', 'woong': '웅', 'ung': '웅', 'joong': '중',
    'jung-': '정', 'taek': '택', 'deok': '덕', 'duk': '덕', 'je': '제', 'gyun': '균', 'kyun': '균', 'jik': '직', 'hwi': '휘',
    'hui': '희', 'eul': '을', 'ok': '옥', 'ryun': '륜', 'ryeong': '령', 'ryung': '령', 'yi': '이', 'ee': '이', 'seoung': '승', 'seong': '성', 'hyeon': '현', 'yeo': '여', 'i': '이', 'sel': '슬', 'seul': '슬', 'he': '혜', 'whi': '휘', 'hwee': '휘',
}
GIVEN = {'gae-un': '가은', 'ga-eun': '가은'}  # 붙임표 자리가 어긋난 관용 표기
INI = [('kk', 1), ('tt', 4), ('pp', 8), ('ss', 10), ('jj', 13), ('ch', 14), ('g', 0), ('k', 0), ('n', 2), ('d', 3),
       ('t', 16), ('r', 5), ('l', 5), ('m', 6), ('b', 7), ('p', 17), ('s', 9), ('j', 12), ('h', 18)]
VOW = [('yeo', 6), ('yae', 3), ('wae', 10), ('weo', 14), ('woo', 13), ('eo', 4), ('eu', 18), ('ui', 19), ('ae', 1),
       ('oe', 11), ('wa', 9), ('wo', 14), ('we', 15), ('wi', 16), ('ya', 2), ('yo', 12), ('yu', 17), ('ye', 7), ('oo', 13),
       ('ee', 20), ('a', 0), ('e', 5), ('i', 20), ('o', 8), ('u', 13)]
FIN = [('ng', 21), ('n', 4), ('m', 16), ('l', 8), ('k', 1), ('g', 1), ('p', 17), ('b', 17), ('t', 19)]
VOWEL_START = re.compile(r'[aeiouwy]')


def _syllables(s):
    """규칙 표기를 음절로 (자음 + 모음 + 받침). 실패하면 None."""
    out, i = [], 0
    while i < len(s):
        ini = next(((a, c) for a, c in INI if s.startswith(a, i) and VOWEL_START.match(s, i + len(a))), ('', 11))
        i += len(ini[0])
        v = next(((a, c) for a, c in VOW if s.startswith(a, i)), None)
        if not v:
            return None
        i += len(v[0])
        fin = 0
        for a, c in FIN:
            if s.startswith(a, i) and not VOWEL_START.match(s, i + len(a)) and not (a == 'ng' and False):
                # 받침 다음에 모음이 오면 그 자음은 다음 음절의 첫소리다
                fin, i = c, i + len(a)
                break
        out.append(chr(0xAC00 + (ini[1] * 21 + v[1]) * 28 + fin))
    return ''.join(out)


def _split(p):
    """붙여 쓴 이름(sungmin, seongwon)을 관용 음절표로 가장 적은 조각으로 나눈다. 안 되면 None."""
    best = {0: []}
    for i in range(len(p)):
        if i not in best:
            continue
        for j in range(i + 1, min(len(p), i + 6) + 1):
            k = p[i:j]
            if k in SYL and (j not in best or len(best[i]) + 1 < len(best[j])):
                best[j] = best[i] + [SYL[k]]
    return ''.join(best[len(p)]) if len(p) in best else None


def _part(p):
    p = p.lower()
    if p in SYL:
        return SYL[p]
    return _split(p) or _syllables(p)


def guess(name):
    """'Kim Woo-jin' → '김우진'. 한국식 이름 꼴이 아니면 None."""
    parts = name.replace('–', '-').split()
    if len(parts) != 2:
        return None
    sur = SURNAME.get(parts[0].lower())
    if not sur:
        return None
    if parts[1].lower() in GIVEN:
        return sur + GIVEN[parts[1].lower()]
    pieces = parts[1].split('-')
    given = [_part(x) for x in pieces]
    if any(g is None for g in given):
        return None
    g = ''.join(given)
    if len(pieces) == 1 and len(g) not in (1, 2):  # 붙여 쓴 이름이 음절로 잘 나뉘지 않음
        return None
    return sur + g


H = re.compile(r'[가-힣]')


def find_hangul(text):
    """영문 위키백과 선수 문서에서 한글 이름 (정보상자 → 첫 문단 순)."""
    pats = (r'\|\s*hangul\s*=\s*%?([가-힣 ]+)',
            r'native_name\s*=\s*(?:\{\{lang\|ko\|)?([가-힣 ]+)',
            r"'''[^'\n]+'''\s*\(\s*\{\{\s*(?:lang-ko|langx\s*\|\s*ko|lang\s*\|\s*ko|Korean)\s*\|\s*(?:hangul\s*=\s*)?([가-힣 ]+)",
            r'\{\{\s*Korean\s*\|[^}]*?hangul\s*=\s*([가-힣 ]+)')
    for pat in pats:
        m = re.search(pat, text, re.I)
        if m and 2 <= len(m.group(1).replace(' ', '')) <= 5:
            return m.group(1).replace(' ', '')
    return None


def load():
    d = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
    d.setdefault('names', {})
    d.setdefault('guessed', {})
    d.setdefault('checked', [])  # 문서를 읽어 봤으나 한글이 없던 이름 (다시 읽지 않는다)
    return d


def save(d):
    d['names'] = dict(sorted(d['names'].items()))
    d['guessed'] = dict(sorted((k, v) for k, v in d['guessed'].items() if k not in d['names']))
    d['checked'] = sorted(set(d['checked']) - set(d['names']))
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=0) + '\n', encoding='utf-8')


def resolve(names, targets, fetch, limit=40):
    """새 한국 선수 이름: 문서(targets[이름]→문서 제목)에서 한글을 찾고, 없으면 추정한다. 바뀌었으면 True."""
    d = load()
    changed = False
    n = 0
    for name in sorted(names):
        if name in d['names'] or (name in d['checked'] and name in d['guessed']):
            continue
        ko = None
        if name not in d['checked'] and n < limit:
            n += 1
            try:
                t = fetch(targets.get(name, name))
                if t.lstrip().lower().startswith('#redirect'):
                    t = fetch(re.search(r'\[\[([^\]|#]+)', t).group(1))
                if 'Korea' in t:
                    ko = find_hangul(t)
            except Exception:
                pass
            if ko:
                d['names'][name] = ko
            else:
                d['checked'].append(name)
            changed = True
        if not ko and name not in d['guessed']:
            g = guess(name)
            if g:
                d['guessed'][name] = g
                changed = True
    if changed:
        save(d)
    return changed


if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(a, '→', guess(a))
