"""One-off source probe run in GitHub Actions: saves raw federation pages so parsers can be written against real markup."""
import re, pathlib, sys
sys.path.insert(0, '.')
from tools.winter.net import request
OUT = pathlib.Path('probe-out'); OUT.mkdir(exist_ok=True)
HTML = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en'}
def get(name, url, **kw):
    try:
        t = request(url, **kw)
    except Exception as e:
        t = f'ERROR {type(e).__name__}: {e}'
    (OUT / name).write_text(t)
    print(name, len(t), url, flush=True)
    return t
def page_and_links(prefix, url, pat, limit=6):
    t = get(prefix + '.html', url, headers=HTML)
    host = 'https://' + url.split('/')[2]
    links = [l if l.startswith('http') else host + l for l in dict.fromkeys(re.findall(r'href="([^"]*(?:%s)[^"]*)"' % pat, t))]
    (OUT / (prefix + '-links.txt')).write_text('\n'.join(links))
    for i, l in enumerate(links[:limit]):
        get(f'{prefix}-{i}.html', l.replace('&amp;', '&'), headers=HTML)
    for i, js in enumerate(list(dict.fromkeys(re.findall(r'src="([^"]+\.js[^"]*)"', t)))[:12]):
        js = js if js.startswith('http') else ('https:' + js if js.startswith('//') else host + js)
        get(f'{prefix}-js{i}.js', js)
page_and_links('ibsf-rr', 'https://www.ibsf.org/en/races-and-results', r'race|result|event|season')
page_and_links('ibsf-live', 'https://www.ibsf.org/en/live', r'live|race|result')
for u in ('https://www.fil-luge.org/en/results', 'https://www.fil-luge.org/en', 'https://www.fil-luge.org/'):
    page_and_links('fil-' + re.sub(r'\W', '', u.split('.org')[1]) or 'fil-root', u, r'result|race|calendar|event', 4)
get('fil-api-try.json', 'https://www.fil-luge.org/api/results')
