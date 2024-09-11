from playwright.async_api import async_playwright
import pytest

CONVERTER_URL = "https://video-converter.com/"
VIDEO_PATH = "videos/test_video_2.mp4"


@pytest.mark.asyncio
async def test_unsuccessful_large_file_upload():
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

            print("Failed to upload (mp4 > 4GB). File size exceeds limit")
            await browser.close()
        except Exception as e:
            print("Failed to upload (mp4 > 4GB). " + str(e))
            raise e
