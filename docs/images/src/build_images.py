"""Regenerate all README figures from the HTML sources in this folder.

Usage:  python build_images.py
Requires: playwright + chromium  (pip install playwright && playwright install chromium)
Outputs 2x PNGs into the parent directory (docs/images/).
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

SRC = Path(__file__).resolve().parent
OUT = SRC.parent

SHOTS = [
    ("banner.html", "banner.png", 1280, 400),
    ("workflow-light.html", "research-workflow-light.png", 830, 480),
    ("workflow-dark.html", "research-workflow-dark.png", 830, 480),
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for html, png, w, h in SHOTS:
            page = browser.new_page(
                viewport={"width": w, "height": h},
                device_scale_factor=2,
            )
            page.goto((SRC / html).as_uri())
            try:
                page.wait_for_function(
                    "document.fonts.status === 'loaded'", timeout=10000
                )
            except Exception:
                pass  # offline: fall back to system fonts
            page.wait_for_timeout(200)
            page.locator("#shot").screenshot(path=str(OUT / png))
            page.close()
            print(f"built {png}")
        browser.close()


if __name__ == "__main__":
    main()
