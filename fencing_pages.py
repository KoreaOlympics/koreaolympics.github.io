"""Preserve the merged fencing hub when the shared athlete generator runs."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def preserve_hub():
    text = (ROOT / 'olfencing-athletes.html').read_text(encoding='utf-8')
    return text if 'id="roster"' in text else None

def finish_generation(previous):
    if previous:
        generated = (ROOT / 'olfencing-athletes.html').read_text(encoding='utf-8')
        roster = re.search(r'<section id="g1">.*?</main>', generated, re.S)
        if not roster:
            raise ValueError('Fencing roster was not generated')
        content = roster.group(0).removesuffix('</main>')
        content = re.sub(r'id="([^"]+)"', r'id="roster-\1"', content)
        content = content.replace('문서 기준', '선수 자료 기준')
        previous = re.sub(r'(<section id="roster">.*?</section>).*?(?=<section id="summary">)', lambda m:m.group(1)+content, previous, count=1, flags=re.S)
        (ROOT / 'olfencing-athletes.html').write_text(previous, encoding='utf-8', newline='\n')
    home = (ROOT / 'olfencing.html').read_text(encoding='utf-8')
    rules = re.search(r'<section class="fencing-rules".*?</section>', home, re.S).group(0)
    targets = [('olfencing.html','전체 안내'),('olfencing-quota.html','단체전 쿼터'),('olfencing-team.html','단체'),('olfencing-individual.html','개인'),('olfencing-athletes.html','한국 선수 구성')]
    for path in ROOT.glob('olfencing*.html'):
        if path.name == 'olfencing-squad.html':
            continue
        text = path.read_text(encoding='utf-8')
        if './css/fencing.css' not in text:
            text = text.replace('</head>', '<link rel="stylesheet" href="./css/fencing.css"></head>')
        links = ''.join(f'<a href="./{href}"'+(' class="quota-tab"' if href=='olfencing-quota.html' else '')+(' aria-current="page"' if href==path.name else '')+f'>{label}</a>' for i,(href,label) in enumerate(targets))
        has_rules = 'class="fencing-rules"' in text
        text = re.sub(r'<nav class="golf-nav"[^>]*>.*?</nav>',lambda m:('' if has_rules else rules)+'<nav class="golf-nav" aria-label="펜싱 문서">'+links+'</nav>', text, count=1,flags=re.S)
        text = re.sub(r'<nav class="footer-nav"[^>]*>.*?</nav>',lambda m:'<nav class="footer-nav" aria-label="펜싱 문서">'+links+'</nav>',text,count=1,flags=re.S)
        path.write_text(text,encoding='utf-8',newline='\n')
