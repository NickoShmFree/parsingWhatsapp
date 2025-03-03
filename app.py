import asyncio
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from playwright.async_api import async_playwright

from conf import app_conf
from conf.logger import logger


if TYPE_CHECKING:
    from playwright.async_api._generated import Page


class WhatsAppScraper:
    def __init__(self) -> None:
        self.page: Optional["Page"] = None

    async def launch_browser(self):
        """Запускает браузер, открывает WhatsApp Web, запускает парсер"""
        async with async_playwright() as playwright:
            browser = await playwright.webkit.launch_persistent_context(
                headless=app_conf.pl.headless,
                user_data_dir=app_conf.pl.user_data_dir,
            )
            self.page = await browser.new_page()
            await self.page.goto("https://web.whatsapp.com/", timeout=120000)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(5)

            logger.info("Браузер успешно запущен и WhatsApp Web открыт.")

            await self.open_chat()
            messages = await self.scrape_messages()
        return messages

    async def open_chat(self):
        """Открывает чат в списке."""
        if not self.page:
            logger.error("Страница не инициализирована.")
            return

        try:
            await self.page.locator(
                'xpath=//*[@id="app"]/div/div[3]/div/header/div/div/div/div/span/div/div[1]/div[3]/button'
            ).click()
            await asyncio.sleep(3)

            await self.page.locator(
                'xpath=//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/div[1]/div[1]/span/span'
            ).click()
            await asyncio.sleep(3)

            logger.info("Чат успешно открыт.")
        except Exception as e:
            logger.error(f"Ошибка при открытии чата: {e}")

    async def scrape_messages(self) -> list[dict]:
        """Собирает данные из видимых сообщений чата."""
        if not self.page:
            logger.error("Страница не инициализирована.")
            return []

        messages = []
        posts = await self.page.locator("[class][role='row']").all()

        for post in posts:
            content_text, content = await self.__get_message_content(post)
            message_data = {
                "content": f"{content_text} {await self.__get_media_content(content)}",
                "media": await self.__get_media(post),
                "publication_timestamp": await self.__get_timestamp(post),
                "reactions_count": await self.__get_reactions_count(post),
            }
            messages.append(message_data)

        logger.info(f"Собрано {len(messages)} сообщений.")
        return messages

    async def __get_message_content(self, post):
        """Получает текст сообщения."""
        content = post.locator('[dir="ltr"]')
        return await content.text_content() or "", content

    async def __get_media_content(self, content) -> str:
        """Получает эмоджи в сообщении."""
        images = await content.locator("img").all()
        media_content = [
            await img.get_attribute("alt")
            for img in images
            if await img.get_attribute("alt")
        ]
        return "".join(media_content)

    async def __get_media(self, post) -> list[str]:
        """Получает ссылки на медиафайлы в сообщении."""
        images = await post.locator(
            "[class ='x15kfjtz x1c4vz4f x2lah0s xdl72j9 x127lhb5 x4afe7t xa3vuyk x10e4vud']"
        ).all()
        return [
            await img.get_attribute("src")
            for img in images
            if await img.get_attribute("src")
        ]

    async def __get_timestamp(self, post) -> Optional[int]:
        """Извлекает временную метку публикации сообщения."""
        try:
            date_text = await post.locator(
                "[class ='x9f619 xyqdw3p x10ogl3i xg8j3zb x1k2j06m x1n2onr6 x1vjfegm xmewjk2 copyable-text']"
            ).get_attribute("data-pre-plain-text")

            if not date_text:
                return None

            date_str = date_text.split("]")[0].strip("[]")
            time_part, date_part = date_str.split(", ")

            dt = datetime.strptime(f"{date_part} {time_part}", "%d.%m.%Y %H:%M")
            return int(dt.timestamp())
        except Exception as e:
            logger.warning(f"Не удалось извлечь дату сообщения: {e}")
            return None

    async def __get_reactions_count(self, post) -> Optional[int]:
        """Получает количество реакций на сообщение."""
        try:
            reactions_text = await post.locator("[class ='xd7y6wv']").get_attribute(
                "aria-label"
            )
            if reactions_text:
                return int(reactions_text.split("всего")[-1].replace("\xa0", ""))
        except Exception:
            pass
        return None
