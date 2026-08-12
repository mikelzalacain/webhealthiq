"""Shared Playwright Chromium launch (low-memory / Docker friendly)."""

from playwright.async_api import Browser, Playwright

CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-extensions",
    "--single-process",
    "--font-render-hinting=none",
]


async def launch_chromium(playwright: Playwright) -> Browser:
    return await playwright.chromium.launch(headless=True, args=CHROMIUM_ARGS)
