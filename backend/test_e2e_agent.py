import asyncio
import sys

from e2e_test_agent.e2e_test_agent import E2eTestingAgent
import logging

logging.basicConfig(level=logging.DEBUG)

if sys.platform == "win32":
    asyncio.set_event_loop(asyncio.ProactorEventLoop())


async def main():
    agent = E2eTestingAgent()
    await agent.ainvoke(
        "Navigate to https://video-converter.com/ then click open file button"
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
