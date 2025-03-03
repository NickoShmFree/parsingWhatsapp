import asyncio
from pprint import pprint

from app import WhatsAppScraper
from conf.logger import configure_logging


async def script_run() -> None:
    api = WhatsAppScraper()
    messages = await api.launch_browser()
    pprint(messages)


def main() -> None:
    configure_logging()
    asyncio.run(script_run())


if __name__ == "__main__":
    main()
