from playwright.async_api import async_playwright
import pytest

CONVERTER_URL = "https://video-converter.com/"
VIDEO_PATH = "videos/test_video_1.mp4"


@pytest.mark.asyncio
async def test_success_upload():
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

            print("Waiting for success message.")
            await page.wait_for_selector("#success-message")

            print("Success upload (mp4 < 4GB).")
            await browser.close()
        except Exception as e:
            print("Failed upload (mp4 < 4GB).")
            raise e
