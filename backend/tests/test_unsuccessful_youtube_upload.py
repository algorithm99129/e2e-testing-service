from playwright.async_api import async_playwright
import pytest

CONVERTER_URL = "https://video-converter.com/"
VIDEO_PATH = "https://www.youtube.com/watch?v=aWk2XZ_8lhA"


@pytest.mark.asyncio
async def test_unsuccessful_youtube_upload():
    async with async_playwright() as p:
        try:
            print("Navigating to the converter URL.")
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(CONVERTER_URL)

            print("Setting input file.")
            await page.set_input_files('input[type="file"]', VIDEO_PATH)

            print("Selecting output format.")
            await page.select_option("select#format", "avi")

            print("Waiting for error message.")
            await page.wait_for_selector("#error-message")

            print("Failed to upload (YouTube link). Upload from YouTube not allowed")
            await browser.close()
        except Exception as e:
            print("Failed to upload (YouTube link). " + str(e))
            raise e
