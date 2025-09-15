from agents import function_tool
from playwright.async_api import async_playwright
import asyncio

@function_tool
async def scrape_dynamic_website(url: str, wait: int = 5000) -> str:
    """
    Scrape the visible text content from website.
    Args:
        url (str): The URL of the website to scrape.
        wait (int): Time in ms to wait for the page to fully load (default 5000).
    Returns:
        str: Extracted text content from the page.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(wait)  # wait for JS to load
            content = await page.content()
            text = await page.inner_text("body")
            await browser.close()
            return text.strip()
    except Exception as e:
        return f"Error scraping {url}: {e}"

# run this inside the same async context where you call Runner.run
# async def main():
#     text = await scrape_dynamic_website("https://x.com/openai")
#     print("DIRECT CALL LENGTH:", len(text))
#     print("DIRECT CALL PREVIEW:", text[:400])

# if __name__ == "__main__":
#     asyncio.run(main())
