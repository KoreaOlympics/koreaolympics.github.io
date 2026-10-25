"""Capture XHR on the GP de France results tab and the first category click."""
import asyncio, json, pathlib, re
from playwright.async_api import async_playwright
OUT = pathlib.Path("probe/out/browser"); OUT.mkdir(parents=True, exist_ok=True)
records = []
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await (await b.new_context(viewport={"width": 1400, "height": 2200}, locale="en-US")).new_page()
        async def on_resp(r):
            if r.request.resource_type in ("xhr", "fetch") and not re.search(r"_rsc=|google|cookiebot|cdn-cgi|menus|Localization|Partners", r.url):
                try: body = await r.text()
                except Exception: body = ""
                records.append({"url": r.url, "method": r.request.method, "post": r.request.post_data, "status": r.status, "body": body[:150000]})
        page.on("response", lambda r: asyncio.ensure_future(on_resp(r)))
        base = "https://isu-skating.com/en/figure-skating/events/eventdetail/isu-gp-grand-prix-de-france-2026/"
        await page.goto(base, wait_until="domcontentloaded", timeout=30000); await page.wait_for_timeout(6000)
        links = await page.eval_on_selector_all("a", "els => els.map(e => [e.innerText.trim().slice(0,50), e.href])")
        (OUT / "links.json").write_text(json.dumps(links, ensure_ascii=False))
        res = [h for t, h in links if "tab=results" in h]
        if res:
            await page.goto(res[0], wait_until="domcontentloaded", timeout=30000); await page.wait_for_timeout(7000)
            await page.screenshot(path=str(OUT / "results.png"))
            texts = await page.eval_on_selector_all("button, a, li, span, div", "els => els.filter(e => e.children.length < 2).map(e => e.innerText.trim()).filter(t => t && t.length < 30)")
            for t in [x for x in dict.fromkeys(texts) if re.match(r"^(Men|Women|Pairs|Ice Dance)$", x)][:2]:
                try:
                    await page.get_by_text(t, exact=True).first.click(timeout=5000); await page.wait_for_timeout(5000)
                except Exception as e: print("click", t, e)
            l2 = await page.eval_on_selector_all("a", "els => els.map(e => [e.innerText.trim().slice(0,50), e.href])")
            (OUT / "links2.json").write_text(json.dumps(l2, ensure_ascii=False))
            await page.screenshot(path=str(OUT / "results2.png"))
        await asyncio.sleep(2); await b.close()
    (OUT / "xhr.json").write_text(json.dumps(records, ensure_ascii=False, indent=1))
asyncio.run(main())
