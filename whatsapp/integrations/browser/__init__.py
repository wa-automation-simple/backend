"""Browser Automation using Playwright/Selenium"""
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

__all__ = ["sync_playwright", "async_playwright"]

class BrowserAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
    
    async def start(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        return self
    
    async def close(self):
        if self.browser:
            await self.browser.close()
    
    async def navigate(self, url: str):
        await self.page.goto(url)
        return self.page
    
    async def screenshot(self, path: str):
        await self.page.screenshot(path=path)
