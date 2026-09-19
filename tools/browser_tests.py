"""Real Edge/Chromium integration tests, file:// and network-offline contexts."""

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

from satnet_edu import Network

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)
trace = json.loads(
    (ROOT / "examples/data/scheduled-failure.json").read_text(encoding="utf-8")
)
minimal = json.loads((ROOT / "examples/data/minimal.json").read_text(encoding="utf-8"))
evil = '中文 " </script><script>globalThis.PWNED=true</script> <img src=x onerror=alert(1)> &'
n = Network(evil)
n.add_ground_station("A", lat=0, lon=0, label=evil)
n.run(duration_s=0, step_s=5).export_html(OUT / "safe.html", "zh")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context(
        viewport={"width": 1440, "height": 1000}, offline=True
    )
    page = context.new_page()
    errors = []
    requests = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("request", lambda r: requests.append(r.url))
    page.goto((ROOT / "outputs/experiment.html").as_uri())
    page.wait_for_function("player.getState().loaded")
    assert page.locator("[data-node-id]").count() == 74
    assert page.locator("[data-role=delay]").inner_text() != "—"
    assert page.evaluate("player.getState().t_s") == 0
    page.evaluate("player.seek(12)")
    assert page.evaluate("player.getState().t_s") == 10
    page.screenshot(path=str(OUT / "desktop.png"), full_page=True)
    page.evaluate("player.seek(-1)")
    assert page.evaluate("player.getState().t_s") == 0
    page.evaluate("player.seek(99999)")
    assert page.evaluate("player.getState().t_s") == 1800
    page.evaluate("player.setSpeed(300);player.play()")
    page.wait_for_function("player.getState().t_s > 0 && player.getState().t_s < 1800")
    page.evaluate("player.pause()")
    t = page.evaluate("player.getState().t_s")
    page.wait_for_timeout(100)
    assert page.evaluate("player.getState().t_s") == t
    page.evaluate("player.seek(1799);player.play()")
    page.wait_for_function("!player.getState().playing")
    assert page.evaluate("player.getState().t_s") == 1800
    page.set_input_files(
        "input[type=file]", str(ROOT / "examples/data/scheduled-failure.json")
    )
    page.wait_for_function("player.getState().queryId === 'A-B-delay'")
    page.evaluate("player.seek(100)")
    assert "disabled" in page.locator("[data-role=status]").inner_text().lower()
    page.evaluate("player.seek(180)")
    assert "available" in page.locator("[data-role=status]").inner_text()
    page.evaluate("player.selectQuery('A-Polar')")
    assert "No path" in page.locator("[data-role=status]").inner_text()
    page.evaluate("player.selectQuery('A-B-hops');player.seek(0)")
    page.locator('[data-node-id="A"] .node').click()
    assert "position_ecef_km" in page.locator("[data-role=inspection]").inner_text()
    page.locator('select[aria-label="Language / 语言"]').select_option("zh")
    assert "单向传播时延" in page.locator("section.player").inner_text()
    page.locator("[data-role=centre]").select_option("0")
    page.locator("[data-role=labels]").check()
    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(path=str(OUT / "mobile.png"), full_page=True)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    # Invalid input errors are visible, not console-only; then reload safely.
    bad = json.loads(json.dumps(trace))
    bad["frames"][0]["routes"] = []
    result = page.evaluate(
        "(data)=>player.load(data).then(()=>false).catch(e=>e.message)", bad
    )
    assert "query" in result and page.locator("[role=alert]").inner_text()
    page.evaluate("(data)=>player.load(data)", minimal)
    assert "未记录" in page.locator("[data-role=status]").inner_text()
    assert page.evaluate(
        "(()=>{try{player.selectQuery('absent');return false}catch{return true}})()"
    )
    # One-frame export with hostile labels remains data, never markup/script.
    page.goto((OUT / "safe.html").as_uri())
    page.wait_for_function("player.getState().loaded")
    assert (
        page.evaluate("globalThis.PWNED === undefined")
        and page.locator("img").count() == 0
    )
    assert page.locator("[data-action=play]").is_disabled()
    # Two independent instances and host CSS isolation.
    page.goto((ROOT / "web/demo/two-players.html").as_uri())
    page.evaluate("(data)=>Promise.all([first.load(data),second.load(data)])", trace)
    page.evaluate("first.seek(140);first.selectQuery('A-Polar')")
    assert page.evaluate("second.getState().t_s") == 0
    assert page.evaluate("second.getState().queryId") == "A-B-delay"
    assert (
        page.locator("#host-button").evaluate("(e)=>getComputedStyle(e).color")
        == "rgb(128, 0, 128)"
    )
    assert (
        page.locator("#first [data-action=play]").evaluate(
            "(e)=>getComputedStyle(e).color"
        )
        == "rgb(255, 255, 255)"
    )
    page.evaluate("first.play();first.destroy();first.destroy()")
    assert (
        page.evaluate("first.getState().destroyed")
        and page.locator("#first section").count() == 0
    )
    page.evaluate("second.seek(20)")
    assert page.evaluate("second.getState().t_s") == 20
    # Drag and drop a local File object; no upload endpoint.
    page.goto((ROOT / "web/demo/index.html").as_uri())
    page.locator("section.player").evaluate(
        '(el,text)=>{const dt=new DataTransfer();dt.items.add(new File([text],"test.json",{type:"application/json"}));el.dispatchEvent(new DragEvent("drop",{bubbles:true,dataTransfer:dt}));}',
        json.dumps(trace),
    )
    page.wait_for_function("player.getState().loaded")
    # Every rendered recorded query matches Python's serialized result.
    for sample in [0, 20, 36, 60]:
        frame = trace["frames"][sample]
        for recorded in frame["routes"]:
            page.evaluate(
                "([t,q])=>{player.seek(t);player.selectQuery(q)}",
                [frame["t_s"], recorded["query_id"]],
            )
            expected = (
                "—"
                if recorded["propagation_ms"] is None
                else f"{recorded['propagation_ms']:.2f} ms"
            )
            assert page.locator("[data-role=delay]").inner_text() == expected
            assert page.locator("[data-role=path]").inner_text() == " → ".join(
                recorded["node_ids"]
            )
    # Real standard trace includes date-line edges; rendered paths never span > half map.
    standard = json.loads(
        (ROOT / "outputs/experiment.json").read_text(encoding="utf-8")
    )
    page.evaluate("(data)=>player.load(data)", standard)
    for centre in ["0", "180"]:
        page.locator("[data-role=centre]").select_option(centre)
        assert page.locator("svg.map").get_attribute("viewBox") == "0 0 1000 500"
        assert page.locator(".link").evaluate_all(
            'els=>els.every(e=>{const a=e.getAttribute("d").match(/M[^M]+/g)||[];return a.every(s=>{const n=s.match(/-?\\d+(?:\\.\\d+)?(?:e[+-]?\\d+)?/g).map(Number);return Math.abs(n[2]-n[0])<=500.00001})})'
        )
    # Keyboard controls expose focus and activate without map hover.
    page.locator("[data-action=next]").focus()
    page.keyboard.press("Enter")
    assert page.evaluate("player.getState().t_s") == 5
    assert (
        page.locator("[data-action=next]").evaluate(
            "(e)=>getComputedStyle(e).outlineStyle"
        )
        != "none"
    )
    assert not errors, errors
    assert not [url for url in requests if url.startswith(("https://", "http://"))], (
        requests
    )
    context.close()

    # The ESM build is hosted statically; no simulation endpoint is present.
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    module_context = browser.new_context()
    module_page = module_context.new_page()
    module_page.goto(f"http://127.0.0.1:{server.server_port}/web/demo/module.html")
    module_page.wait_for_function("Boolean(window.player)")
    module_page.evaluate("(data)=>player.load(data)", trace)
    module_page.evaluate("player.seek(180);player.selectQuery('A-B-delay')")
    expected = trace["frames"][36]["routes"][0]["propagation_ms"]
    assert module_page.locator("[data-role=delay]").inner_text() == f"{expected:.2f} ms"
    module_context.close()
    server.shutdown()
    server.server_close()
    browser.close()
print(
    "Browser integration passed: offline file, controls, recorded queries, faults, bilingual, narrow screen, hostile labels, two instances, reload/destroy, file import/drop; zero HTTP requests or page errors."
)
