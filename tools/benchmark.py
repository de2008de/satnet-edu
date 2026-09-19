"""Real engines, full JSON; timings are observations, not service guarantees."""

import json
import platform
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from satnet_edu import Network, RouteQuery

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/benchmarks"
OUT.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_page(viewport={"width": 1440, "height": 1000})
    page.goto((ROOT / "web/demo/index.html").as_uri())
    for label, planes, slots, duration in [
        ("small", 2, 12, 300),
        ("standard", 6, 12, 1800),
        ("larger", 12, 12, 3600),
    ]:
        n = Network(label)
        n.add_constellation(
            planes=planes, sats_per_plane=slots, altitude_km=1000, inclination_deg=53
        )
        n.add_ground_station("A", lat=49.28, lon=-123.12)
        n.add_ground_station("B", lat=35.68, lon=139.69)
        before = time.perf_counter()
        run = n.run(
            duration_s=duration,
            step_s=5,
            record_routes=[
                RouteQuery("delay", "A", "B"),
                RouteQuery("hops", "A", "B", "hops"),
            ],
        )
        simulation = time.perf_counter() - before
        before = time.perf_counter()
        path = run.save(OUT / f"{label}.json")
        save = time.perf_counter() - before
        text = path.read_text(encoding="utf-8")
        browser_metrics = page.evaluate(
            """async text=>{const a=performance.now();const data=JSON.parse(text);const parse=performance.now()-a;const t=performance.now();await player.load(data);const load=performance.now()-t;const samples=[];for(let i=0;i<10;i++){const t=performance.now();player.seek(data.frames[Math.floor(i*(data.frames.length-1)/9)].t_s);samples.push(performance.now()-t);}return {parse_ms:parse,validate_clone_first_render_ms:load,mean_seek_render_ms:samples.reduce((a,b)=>a+b)/samples.length,js_heap_observed_bytes:performance.memory?.usedJSHeapSize??null};}""",
            text,
        )
        row = dict(
            scale=label,
            satellites=planes * slots,
            ground_stations=2,
            samples=duration // 5 + 1,
            simulation_s=simulation,
            validate_save_s=save,
            json_bytes=path.stat().st_size,
            **browser_metrics,
        )
        results.append(row)
        print(json.dumps(row), flush=True)
    b.close()
report = dict(
    environment=dict(
        python=platform.python_version(),
        platform=platform.platform(),
        browser="Edge/Chromium headless",
    ),
    results=results,
    peak_memory="Not measured. Browser heap is a coarse point observation, not peak memory; Python/native peak not measured.",
)
(ROOT / "docs/benchmark-results.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
