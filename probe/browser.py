"""Open pages in headless Chromium, click tabs, record JSON responses and screenshots."""
import asyncio, json, pathlib, re
from playwright.async_api import async_playwright

OUT = pathlib.Path("probe/out/browser"); OUT.mkdir(parents=True, exist_ok=True)
PAGES = [
    ("fs-skate-america", "https://isu-skating.com/figure-skating/events/eventdetail/isu-gp-skate-america-2026/"),
    ("ss-finished", "https://isu-skating.com/speed-skating/results/"),
    ("fis-event", "https://www.fis-ski.com/DB/general/event-details.html?sectorcode=SB&eventid=62743&seasoncode=2027"),
    ("curl-wmdqe", "https://livescores.worldcurling.org/wmdqe26"),
]
OLD = [
    ("st-schedule", "https://isu-skating.com/short-track/events/eventdetail/isu-short-track-world-tour-1/?tab=schedule_16230"),
    ("st-results", "https://isu-skating.com/short-track/events/eventdetail/isu-short-track-world-tour-1/?tab=results_16230"),
    ("st-resultsidx", "https://isu-skating.com/short-track/results/"),
    ("fs-events", "https://isu-skating.com/figure-skating/events/"),
]
records = []

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1400, "height": 2200}, locale="en-US")
        page = await ctx.new_page()
        async def on_resp(r):
            if r.request.resource_type in ("xhr", "fetch"):
                try: body = await r.text()
                except Exception: body = ""
                records.append({"page": cur[0], "url": r.url, "method": r.request.method, "post": r.request.post_data,
                                "status": r.status, "ctype": r.headers.get("content-type"), "len": len(body), "body": body[:300000]})
        cur = [""]
        page.on("response", lambda r: asyncio.ensure_future(on_resp(r)))
        for name, url in PAGES:
            cur[0] = name
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as e:
                print(name, "goto", e)
            await page.wait_for_timeout(4000)
            # click every element that looks like a results / schedule link inside the tab content
            await page.screenshot(path=str(OUT / f"{name}.png"), full_page=False)
            (OUT / f"{name}.html").write_text(await page.content())
            links = await page.eval_on_selector_all("a", "els => els.map(e => [e.innerText.trim().slice(0,60), e.href]).filter(x => x[1])")
            (OUT / f"{name}.links.json").write_text(json.dumps(links, ensure_ascii=False, indent=0))
            if name in ("fs-skate-america", "ss-finished", "fis-event", "curl-wmdqe"):
                cand = [l for l in links if re.search(r"tab=results|results\\.html|raceid=|/Draw|draw|Standings|standings", l[1], re.I)]
                (OUT / f"{name}.cand.json").write_text(json.dumps(cand[:80], ensure_ascii=False))
                for i, (t, href) in enumerate(cand[:2]):
                    try:
                        await page.goto(href, wait_until="networkidle", timeout=60000); await page.wait_for_timeout(4000)
                        await page.screenshot(path=str(OUT / f"{name}-c{i}.png"))
                        (OUT / f"{name}-c{i}.html").write_text(await page.content())
                        links2 = await page.eval_on_selector_all("a", "els => els.map(e => [e.innerText.trim().slice(0,60), e.href]).filter(x => x[1])")
                        (OUT / f"{name}-c{i}.links.json").write_text(json.dumps(links2, ensure_ascii=False))
                        # one level deeper: first round/result link
                        deeper = [l for l in links2 if re.search(r"round=|raceid=|type=", l[1])]
                        if deeper:
                            await page.goto(deeper[0][1], wait_until="networkidle", timeout=60000); await page.wait_for_timeout(4000)
                            await page.screenshot(path=str(OUT / f"{name}-c{i}-d.png"))
                            (OUT / f"{name}-c{i}-d.html").write_text(await page.content())
                    except Exception as e:
                        print(name, "cand", e)
            if name == "st-results":
                for txt in ["Men 500 m", "Women 500 m", "Men 1500 m"]:
                    try:
                        await page.get_by_text(txt).first.click(timeout=5000)
                        await page.wait_for_timeout(4000)
                        await page.screenshot(path=str(OUT / f"{name}-{txt.replace(' ','_')}.png"))
                    except Exception as e:
                        print("click", txt, e)
        await asyncio.sleep(2)
        await b.close()
    (OUT / "xhr.json").write_text(json.dumps(records, ensure_ascii=False, indent=1))
    for r in records: print(r["page"], r["status"], r["len"], r["method"], r["url"][:160])

asyncio.run(main())
