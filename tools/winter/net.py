"""HTTP helpers shared by the winter collectors (stdlib only)."""
import json, time, urllib.parse, urllib.request

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 KoreaOlympics/1.0'

def request(url, data=None, form=None, headers=None, tries=3, timeout=30):
    body = None
    h = {'User-Agent': UA, 'Accept': 'application/json, text/html;q=0.9'}
    if data is not None:
        body = json.dumps(data).encode(); h['Content-Type'] = 'application/json'
    elif form is not None:
        body = urllib.parse.urlencode(form).encode(); h['Content-Type'] = 'application/x-www-form-urlencoded'
    h.update(headers or {})
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers=h, method='POST' if body else 'GET')
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            if attempt == tries - 1: raise
            time.sleep(2 * (attempt + 1))

def get_json(url, **kw):
    return json.loads(request(url, **kw))
