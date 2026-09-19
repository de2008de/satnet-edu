from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page()
    page.goto(Path("web/demo/minimal.html").resolve().as_uri())
    page.set_input_files("input[type=file]", "examples/data/minimal.json")
    page.wait_for_function("document.querySelectorAll('circle').length === 6")
    page.locator("input[type=range]").fill("2")
    assert page.locator("output").inner_text() == "60 s"
    browser.close()
print("M1 file:// import and seek passed; no Python simulation/server running")
