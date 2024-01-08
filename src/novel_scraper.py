# Standard Library Imports
from time import sleep
from typing import Union,List,AnyStr
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse
import io
import logging
import re
import os
import sys


# Third-Party Library Imports
import pytesseract
from playwright.sync_api import sync_playwright, Route, Response
from PIL import Image
from fake_useragent import FakeUserAgent
from googletrans import Translator

# Local Imports
from src.scraper_expectation import (
    EmptyChapterListError,
    NovelNameError,
    NovelPageLoadError,
    TranslationError,
)



@dataclass
class ScraperItems:
    novel_name: str
    chapters_id: List[int]
    novel_folder_path: str


# ANSI escape codes for color
RED = "\033[91m"
RESET = "\033[0m"


class NovelScraper:
    CHAPTER_LIST_PAGE = [
        "https://sangtacviet.vip/index.php",
        "getchapterlist",
        "chapterlist",
    ]

    def __init__(self):
        self.scraper_items = ScraperItems(
            novel_name="", chapters_id=[], novel_folder_path=""
        )

    # Playwright Utilities

    def _start_playwright(self) -> None:
        """Starts the Playwright."""
        print(">>(info):","Starting playwright")
        self.playwright = sync_playwright().start()

    def _launch_browser(self) -> None:
        """Launches the headless chromium browser."""
        print(">>(info):","Launching headless chromium browser")
        self.browser = self.playwright.chromium.launch(
            headless=True, slow_mo=21
        )

    def _initialize_page(self) -> None:
        """Initializes a new page in the browser."""
        print(">>(info):","Initializing new page")
        user_agent = FakeUserAgent().random
        context = self.browser.new_context(user_agent=user_agent)
        self._add_lang_cookie(context)
        page = context.new_page()
        page.route("**/*", self._abort_unwanted_resources)
        self.page = page

    def _add_lang_cookie(self, context):
        """Adds language cookies to the context."""
        d = datetime.utcnow() + timedelta(days=365)
        expires = int(d.timestamp())
        context.add_cookies(
            [
                {
                    "name": "lang",
                    "value": "vi",
                    "domain": "sangtacviet.vip",
                    "path": "/",
                    "expires": expires,
                },
                {
                    "name": "foreignlang",
                    "value": "en",
                    "domain": "sangtacviet.vip",
                    "path": "/",
                    "expires": expires,
                },
            ]
        )

    def _abort_unwanted_resources(self, route: Route) -> None:
        """Aborts unwanted resources from the background."""
        BLOCK_RESOURCE_TYPES = [
            "beacon",
            "csp_report",
            "media",
            "object",
            "texttrack",
        ]
        BLOCK_RESOURCE_NAMES = [
            "service.supercounters.com",
            "analytics",
            "doubleclick",
            "exelator",
            "ads",
            "google",
            "google-analytics",
            "googletagmanager",
            "woafoame",
        ]

        if route.request.resource_type in BLOCK_RESOURCE_TYPES:
            return route.abort()
        if any(key in route.request.url for key in BLOCK_RESOURCE_NAMES):
            return route.abort()

        return route.continue_()

    def _close_browser(self) -> None:
        """Closes the browser."""
        print(">>(info):","Closing the browser")
        self.browser.close()

    def _stop_playwright(self) -> None:
        """Stops the Playwright."""
        print(">>(info):","Stopping Playwright")
        self.playwright.stop()

    # Novel Page Methods

    def _scrape_novel_page(
        self, novel_page_url: str, download_folder_path: str
    ):
        """Scrapes information from the novel page."""
        novel_page_url = self._validated_url(novel_page_url)


        self.page.on("response",self._get_chapter_list)
        print(">>(info):","loading novel page url:",novel_page_url)
        self.page.goto(novel_page_url,wait_until="load",timeout=24000)

        self._get_novel_name()
        novel_name = self.scraper_items.novel_name
        print(">>(info):","novel name extracted:",novel_name)
        if not novel_name:
            raise NovelNameError(
                "Novel name is null. Unable to extract the novel name"
            )

        novel_name_in_eng = self._translate(novel_name)
        print(">>(info):","novel name in eng:",novel_name_in_eng)
        if not novel_name_in_eng:
            raise TranslationError(
                f"Failed to translate novel name: {novel_name}. The translation result is empty."
            )

        print(">>(info): chapters_id:", self.scraper_items.chapters_id)
        if not self.scraper_items.chapters_id:
            raise EmptyChapterListError(
                "Failed to retrieve the chapter list. The list is empty."
            )

        download_path = self._validate_download_path(download_folder_path)
        novel_folder_path = self._create_novel_folder(
            download_path, novel_name_in_eng
        )

        print(">>(info): novel folder created:", novel_folder_path)
        self.scraper_items.novel_folder_path = novel_folder_path

    def _scrape_chapter_page(self, novel_page_url: str, starting_chapter: str):
        """Scrapes content from each chapter page."""
        chapter_id_list = self.scraper_items.chapters_id
        starting_chapter = self._validated_starting_chapter(starting_chapter)

        for chapter_num in range(starting_chapter, len(chapter_id_list)):
            print(">>(info): scraping chapter:", chapter_num+1)
            chapter_page = f"{novel_page_url}{chapter_id_list[chapter_num]}/"
            self.page.goto(chapter_page, wait_until="domcontentloaded")

            while True:
                self.page.locator("html").click()
                self.page.wait_for_load_state("networkidle")
                num_of_opened_pages = len(self.page.context.pages)
                if num_of_opened_pages > 1:
                    for i in range(1, num_of_opened_pages):
                        self.page.context.pages[i].close()
                sleep(1)
                is_spinning = self.page.query_selector(".spinner-border")
                if not is_spinning:
                    break

            chapter_content_box = self.page.locator(
                "#content-container .contentbox"
            )

            self._remove_ads()
            print(">>(info): taking screenshot of chapter:", chapter_num+1)
            chapter_content_bytes = chapter_content_box.screenshot()
            chapter_content_txt = self._extract_chapter_content(
                chapter_content_bytes
            )

            self._save_chapter(chapter_num, str(chapter_content_txt))
            sleep(0.7)

    def scrap(
        self,
        novel_page_url: str,
        starting_chapter: int,
        download_folder_path: str,
    ):
        """Main scraping method."""
        try:
            self._start_playwright()
            self._launch_browser()
            self._initialize_page()
            self._scrape_novel_page(novel_page_url, download_folder_path)
            self._scrape_chapter_page(novel_page_url, starting_chapter)
            self._close_browser()

        except Exception as e:
            logging.critical(f"Error during scraping: {e}")
            raise e

        finally:
            self._stop_playwright()

    def _get_chapter_list(self, res: Response):
        """Extracts chapter list from the response."""
        if "sajax=getchapterlist" in res.url and res.status == 200:
            json_res = res.json()

            code = json_res.get("code")
            data = json_res.get("data")

            if code == 1 and data:
                chapters_un_data = json_res["data"]
                chapters_id = re.findall(r"1-/-(\d+)-/-", chapters_un_data)
                chapter_id_list = [
                    int(chapter_id) for chapter_id in chapters_id
                ]

                self.scraper_items.chapters_id = sorted(chapter_id_list)

    def _get_novel_name(self):
        """Extracts the novel name from the page."""
        novel_name = self.page.locator("h1#book_name2").text_content()
        print("test-------",novel_name.encode('cp1251').decode())
        self.scraper_items.novel_name = novel_name

    def _validated_url(self, novel_page_url: str) -> Union[str, None]:
        """Validates and formats the novel page URL."""
        url = novel_page_url

        while True:
            try:
                parse_result = urlparse(url)
                path_pattern = re.compile(r"/(\d+)/?$")
                is_valid_path = bool(
                    re.search(path_pattern, parse_result.path)
                )

                if (
                    (parse_result.scheme in ["http", "https"])
                    and (parse_result.netloc == "sangtacviet.vip")
                    and is_valid_path
                ):
                    if parse_result.path.endswith("/"):
                        return url
                    else:
                        return f"{url}/"
                else:
                    url = input("Please enter the correct novel page URL: ")

            except (TypeError, ValueError):
                url = input("Please enter the correct novel page URL: ")

    def _validated_starting_chapter(
        self, starting_chapter: int
    ) -> Union[int, None]:
        """Validates the starting chapter index."""
        while True:
            total_chapter = len(self.scraper_items.chapters_id)
            starting_chapter = starting_chapter - 1

            if all([starting_chapter < 0, starting_chapter > total_chapter]):
                print(
                    f"Error: The starting chapter must be in range between [1-{total_chapter}].\n"
                )
                starting_chapter = int(
                    input(
                        f"Please enter the correct one [1-{total_chapter}]: "
                    )
                )
                starting_chapter = starting_chapter - 1
            else:
                return starting_chapter

    def _remove_ads(self):
        """Removes ads from the page."""
        iframes = self.page.query_selector_all("iframe")
        print(">> iframes:", iframes)
        if iframes:
            print(">> iframes:", iframes)

            self.page.evaluate(
                """
                var iframes = document.querySelectorAll('iframe');
                iframes.forEach(function(iframe) {
                    iframe.style.display = 'none';
                });
            """
            )
            return "removed"

    def _validate_download_path(
        self, download_path: str = None
    ) -> Union[str, None]:
        """Validates and formats the download folder path."""
        download_path = str(download_path).strip()

        while True:
            is_dir = os.path.isdir(download_path)

            if is_dir:
                is_abs_path = os.path.isabs(download_path)

                if is_abs_path:
                    return download_path
                else:
                    return os.path.abspath(download_path)
            else:
                download_path = input(
                    "Please enter the correct Path of Download Folder: "
                )
                download_path = str(download_path).strip()

    def _create_novel_folder(self, download_path, novel_name) -> str:
        """Creates a folder for the novel."""
        novel_folder_name = novel_name.replace("/", "").replace("\\", "")
        novel_folder_path = os.path.join(download_path, novel_folder_name)

        if not os.path.exists(novel_folder_path):
            os.makedirs(novel_folder_path, exist_ok=True)

        return novel_folder_path

    def _translate(self, text: str) -> Union[str, None]:
        """Translates text to English."""
        translator = Translator()

        try:
            translations = translator.translate(text, src="vi", dest="en")
            translated_text = translations.text
            return translated_text
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return None

    def _extract_chapter_content(self, chapter_content_bytes):
        """Extracts chapter content from the screenshot."""
        image = Image.open(io.BytesIO(chapter_content_bytes))
        chapter_content_txt = pytesseract.image_to_string(image, lang="vie")

        return chapter_content_txt

    def _save_chapter(self, chapter_num: int, chapter_content: str) -> bool:
        """Saves the translated chapter content to a file."""
        novel_folder_path = self.scraper_items.novel_folder_path
        chapter_txt_path = os.path.join(
            novel_folder_path, f"{chapter_num+1}.txt"
        )

        chunk_size = len(chapter_content) // 3
        paragraphs = [
            chapter_content[i : i + chunk_size]
            for i in range(0, len(chapter_content), chunk_size)
        ]

        translated_chapter = ""
        for p in paragraphs:
            p = str(p).strip()
            if p:
                print(">>(info): paragraph of chapter:",chapter_num+1," before translate:",p)
                translation_result = self._translate(p)
                print(">>(info): paragraph of chapter:",chapter_num+1," after translate:",translation_result)

            if translation_result is not None:
                translated_chapter += translation_result + "\n"
            else:
                pass

        if not translated_chapter:
            logging.error(
                f"Unable to translate chapter {chapter_num} content; saved as it is."
            )

        try:
            with open(chapter_txt_path, "w", encoding="utf-8") as file:
                file.write(translated_chapter)
            print(">>(info): chapter:",chapter_num+1,"saved to:",chapter_txt_path)
        except Exception as e:
            logging.error(f"Error saving chapter {chapter_num} to file: {e}")
            return False
