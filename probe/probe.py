"""Fetch candidate URLs and save raw responses for offline analysis."""
import hashlib, json, pathlib, re, sys, urllib.request

OUT = pathlib.Path("probe/out")
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", "Origin": "https://koreaolympics.github.io"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read() or b""
    except Exception as e:
        return 0, {}, repr(e).encode()

index = []
urls = [u.strip() for u in pathlib.Path(sys.argv[1]).read_text().splitlines() if u.strip() and not u.startswith("#")]
for url in urls:
    status, headers, body = fetch(url)
    name = hashlib.sha1(url.encode()).hexdigest()[:10]
    (OUT / f"{name}.body").write_bytes(body[:4_000_000])
    found = sorted(set(re.findall(rb"https?://[^\s\"'<>\\)]+(?:api|json|graphql|_next/data|wp-json)[^\s\"'<>\\)]*", body)))[:200]
    index.append({"url": url, "file": name, "status": status, "len": len(body),
                  "ctype": headers.get("Content-Type"), "cors": headers.get("Access-Control-Allow-Origin"),
                  "api_like": [f.decode("utf-8", "replace") for f in found]})
    print(status, len(body), url)
(OUT / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False))
