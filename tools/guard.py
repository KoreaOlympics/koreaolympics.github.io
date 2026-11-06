"""내용 보호: 업로드·덮어쓰기로 사라진 섹션과 자동 블록을 되살린다.

    python tools/guard.py <기준 커밋>      # 기준 커밋과 지금 파일을 비교해 되살린다 (워크플로: 푸시 직전 커밋)
    python tools/guard.py <기준 커밋> --dry # 무엇을 되살릴지만 보여 준다

- 종목·세부종목 문서에서 기준 커밋에 있던 섹션이 없어지거나 내용이 30% 넘게 줄었으면 기준 커밋의 섹션으로 되돌린다.
- 자동 블록(한눈에 보기·출전 확정·예선 단계·문서 안내·파리 메달)은 data/ 자료에서 다시 만든다.
- 일부러 지운 경우에는 커밋 메시지에 [guard skip]을 넣으면 워크플로가 이 도구를 돌리지 않는다.
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from olympic import _TXT  # noqa: E402

SEC = re.compile(r'<section id="([a-z_0-9]+)"[^>]*>.*?</section>', re.S)
GENERATORS = ['tools/summary_svg.py', 'tools/qualified.py', 'tools/pathways.py', 'tools/sport_guide.py', 'tools/paris_medals.py', 'tools/summer_live.py']


def show(base, rel):
    r = subprocess.run(['git', 'show', f'{base}:{rel}'], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def older_sections(base, rel, n=40):
    """기준 커밋보다 앞선 판들의 섹션 텍스트 {섹션: {텍스트, ...}} — 옛 판으로 되돌아간 섹션을 알아보는 데 쓴다."""
    revs = subprocess.run(['git', 'log', '--format=%H', f'-n{n}', base, '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.split()[1:]
    out = {}
    for r in revs:
        t = show(r, rel) or ''
        for m in SEC.finditer(t):
            out.setdefault(m.group(1), set()).add(_TXT(m.group(0)))
    return out


def restore(old, new, older=None):
    """기준(old)에 있던 섹션 중 없어지거나 줄어들거나 옛 판으로 돌아간 것을 new에 되돌린다. (새 텍스트, 되돌린 섹션 목록)"""
    olds = {m.group(1): m.group(0) for m in SEC.finditer(old)}
    news = {m.group(1): m.group(0) for m in SEC.finditer(new)}
    older = older or {}
    fixed = []
    for sid, block in olds.items():
        before = _TXT(block)
        if len(before) <= 120 or sid in ('winter_live',):
            continue
        if sid in news:
            now = _TXT(news[sid])
            stale = now != before and now in older.get(sid, set())  # 옛 판을 다시 올렸다
            if len(now) >= len(before) * 0.7 and not stale:
                continue
            new = new.replace(news[sid], block, 1)
        else:  # 섹션이 통째로 없어졌다: 각주 앞(없으면 내비게이션 상자 앞)에 넣는다
            anchor = next((a for a in ('<section id="refs"', '<nav class="navbox"', '</main>') if a in new), None)
            if not anchor:
                continue
            new = new.replace(anchor, block + '\n' + anchor, 1)
        fixed.append(sid)
    return new, fixed


def main(argv):
    if not argv:
        sys.exit(__doc__)
    base, dry = argv[0], '--dry' in argv
    changed = subprocess.run(['git', 'diff', '--name-only', base, '--', '*.html'], cwd=ROOT, capture_output=True, text=True).stdout.split()
    total = 0
    for rel in changed:
        if not re.match(r'(ol|wi)[a-z]+(\.html|/[a-z0-9]+\.html)$', rel):
            continue  # 관리 대상(종목·세부종목 문서)만
        path = ROOT / rel
        old = show(base, rel)
        if old is None or not path.exists():
            continue
        new, fixed = restore(old, path.read_text(encoding='utf-8'), older_sections(base, rel))
        if fixed:
            total += len(fixed)
            print(f'{rel}: 되살림 {", ".join(fixed)}')
            if not dry:
                path.write_text(new, encoding='utf-8', newline='\n')
    if not dry:
        for g in GENERATORS:  # 자동 블록은 자료에서 다시 그린다 (바뀐 것이 없으면 파일도 그대로)
            subprocess.run([sys.executable, g], cwd=ROOT, check=True, capture_output=True)
    print(f'guard: 섹션 {total}개 되살림')


if __name__ == '__main__':
    main(sys.argv[1:])
