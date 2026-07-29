"""
Playwright PDF worker function.
Must be in a top-level importable module so multiprocessing spawn can find it.
"""
import asyncio
import sys


def run(html: str, output_path: str, error_queue) -> None:
    """Runs inside a spawned Process — owns its own fresh event loop."""
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "12.7mm", "bottom": "12.7mm", "left": "12.7mm", "right": "12.7mm"},
            )
            browser.close()
        error_queue.put(None)  # None = success
    except Exception:
        import traceback
        error_queue.put(traceback.format_exc())
