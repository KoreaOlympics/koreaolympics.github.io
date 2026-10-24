"""Open pages in headless Chromium, click into results, record XHR JSON and screenshots."""
import asyncio, json, pathlib, re
from playwright.async_api import async_playwright

OUT = pathlib.Path("probe/out/browser"); OUT.mkdir(parents=True, exist_ok=True)
PAGES = [
    ("ss-wc5", "https://isu-skating.com/en/speed-skating/events/eventdetail/isu-speed-skating-world-cup-5/?tab=results_1311", r"^(Men|Women|Ladies).*\d+ ?m"),
    ("ss-wc5-sched", "https://isu-skating.com/en/speed-skating/events/eventdetail/isu-speed-skating-world-cup-5/?tab=schedule_1311", None),
    ("fs-sa", "https://isu-skating.com/en/figure-skating/events/eventdetail/isu-gp-skate-america-2026/?tab=results_16006", r"^(Men|Women|Pairs|Ice Dance)"),
    ("fs-sa-sched", "https://isu-skating.com/en/figure-skating/events/eventdetail/isu-gp-skate-america-2026/?tab=schedule_16006", None),
    ("isulive", "https://live.isuresults.eu/home", None),
]
records, cur = [], [""]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await (await b.new_context(viewport={"width": 1400, "height": 2200}, locale="en-US")).new_page()
        async def on_resp(r):
            if r.request.resource_type in ("xhr", "fetch") and not re.search(r"_rsc=|google|cookiebot|cdn-cgi|menus|Localization", r.url):
                try: body = await r.text()
                except Exception: body = ""
                records.append({"page": cur[0], "url": r.url, "method": r.request.method, "post": r.request.post_data,
                                "status": r.status, "len": len(body), "body": body[:200000]})
        page.on("response", lambda r: asyncio.ensure_future(on_resp(r)))
        for name, url, clickre in PAGES:
            cur[0] = name
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(7000)
                await page.screenshot(path=str(OUT / f"{name}.png"))
                (OUT / f"{name}.html").write_text(await page.content())
                if clickre:
                    texts = await page.eval_on_selector_all("button, a, li, div[role=button], span",
                        "els => els.filter(e => e.children.length < 3).map(e => e.innerText.trim()).filter(t => t && t.length < 40)")
                    hits = list(dict.fromkeys(t for t in texts if re.search(clickre, t)))[:3]
                    (OUT / f"{name}.clickable.json").write_text(json.dumps(texts[:300], ensure_ascii=False))
                    for i, t in enumerate(hits):
                        try:
                            await page.get_by_text(t, exact=True).first.click(timeout=5000)
                            await page.wait_for_timeout(5000)
                            await page.screenshot(path=str(OUT / f"{name}-{i}.png"))
                        except Exception as e:
                            print(name, "click", t, e)
            except Exception as e:
                print(name, e)
        await asyncio.sleep(2); await b.close()
    (OUT / "xhr.json").write_text(json.dumps(records, ensure_ascii=False, indent=1))

asyncio.run(main())
