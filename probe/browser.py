"""Capture front-api calls for short track relays and figure pairs / ice dance."""
import asyncio, json, pathlib, re
from playwright.async_api import async_playwright
OUT = pathlib.Path("probe/out/browser"); OUT.mkdir(parents=True, exist_ok=True)
records = []
PAGES = [
    "https://isu-skating.com/en/short-track/events/eventdetail/isu-short-track-world-tour-1/?tab=results_16230&type=15994",
    "https://isu-skating.com/en/short-track/events/eventdetail/isu-short-track-world-tour-1/?tab=results_16230&type=15995",
    "https://isu-skating.com/en/figure-skating/events/eventdetail/isu-gp-grand-prix-de-france-2026/?tab=results_16027&type=15694",
    "https://isu-skating.com/en/figure-skating/events/eventdetail/isu-gp-grand-prix-de-france-2026/?tab=results_16027&type=15693",
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await (await b.new_context(viewport={"width": 1400, "height": 2200}, locale="en-US")).new_page()
        cur = [""]
        async def on_resp(r):
            if r.request.resource_type in ("xhr", "fetch") and "front-api" in r.url and not re.search(r"menus|Localization|Partners|featured", r.url):
                try: body = await r.text()
                except Exception: body = ""
                records.append({"page": cur[0], "url": r.url, "post": r.request.post_data, "status": r.status, "body": body[:100000]})
        page.on("response", lambda r: asyncio.ensure_future(on_resp(r)))
        for i, url in enumerate(PAGES):
            cur[0] = url
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000); await page.wait_for_timeout(7000)
                await page.screenshot(path=str(OUT / f"p{i}.png"))
                links = await page.eval_on_selector_all("a", "els => els.map(e => e.href).filter(h => h.includes('round='))")
                for h in list(dict.fromkeys(links))[:2]:
                    cur[0] = h
                    await page.goto(h, wait_until="domcontentloaded", timeout=30000); await page.wait_for_timeout(6000)
            except Exception as e:
                print(url, e)
        await b.close()
    (OUT / "xhr.json").write_text(json.dumps(records, ensure_ascii=False, indent=1))
asyncio.run(main())
