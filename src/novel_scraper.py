import sys

sys.stdout.reconfigure(encoding="utf-8")

# Standard Library Imports
from time import sleep
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse
import io
import re
import os


# Third-Party Library Imports
import pytesseract
from playwright.sync_api import sync_playwright, Route, Response, TimeoutError
from PIL import Image
from fake_useragent import FakeUserAgent
from googletrans import Translator

# Local Imports
from src.scraper_expectation import (
    EmptyChapterListError,
    NovelNameExtractingError,
    NovelPageLoadError,
    TranslationError,
    InvalidNovelPageUrl,
    InvalidDownloadPath,
    InvalidStartingChapter,
)


class NovelScraper:
    CHAPTER_LIST_PAGE = [
        "https://sangtacviet.vip/index.php",
        "getchapterlist",
        "chapterlist",
    ]

    def __init__(self):
        self.novel_name = None
        self.chapters_id = None
        self.novel_folder_path = None

    # Playwright Utilities

    def _start_playwright(self) -> None:
        """Starts the Playwright."""
        print(">>(info):", "Starting playwright")
        self.playwright = sync_playwright().start()

    def _launch_browser(self) -> None:
        """Launches the headless chromium browser."""
        print(">>(info):", "Launching headless chromium browser")
        self.browser = self.playwright.chromium.launch(headless=True, slow_mo=21)

    def _initialize_page(self) -> None:
        """Initializes a new page in the browser."""
        print(">>(info):", "Initializing new page")
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
        print(">>(info):", "Closing the browser")
        self.browser.close()

    def _stop_playwright(self) -> None:
        """Stops the Playwright."""
        print(">>(info):", "Stopping Playwright")
        self.playwright.stop()

    # Novel Page Methods

    def _scrape_novel_page(self, novel_page_url: str, download_folder_path: str):
        """Scrapes information from the novel page."""
        novel_page_url = self._validated_url(novel_page_url)
        if novel_page_url is None:
            raise InvalidNovelPageUrl

        self.page.on("response", self._get_chapter_list)
        print(">>(info):", "loading novel page url:", novel_page_url)

        try:
            page_res = self.page.goto(novel_page_url, wait_until="load", timeout=210000)
            if page_res.status != 200:
                raise NovelPageLoadError(
                    f"Error: unable to load the novel page,please check the url by opening on browser. got_to:{novel_page_url}"
                )
        except TimeoutError:
            raise NovelPageLoadError(
                "Error loading novel page. The loading time exceeded the timeout limit. Please try agin or check your internet connection."
            )

        novel_name = self._get_novel_name()
        print(">>(info):", "novel name extracted:", novel_name)
        if novel_name is None:
            raise NovelNameExtractingError

        novel_name_in_eng = self._translate(novel_name)
        print(">>(info):", "novel name in eng:", novel_name_in_eng)
        if not novel_name_in_eng:
            raise TranslationError(
                f"Error: Failed to translate the novel name: {novel_name}. The translation api response is empty."
            )

        print(">>(info): chapters_id:", self.chapters_id)
        if not self.chapters_id:
            raise EmptyChapterListError(
                "Failed to retrieve the chapter list. The list is empty."
            )

        download_path = self._validate_download_path(download_folder_path)
        if not download_path:
            raise InvalidDownloadPath

        novel_folder_path = self._create_novel_folder(download_path, novel_name_in_eng)

        print(">>(info): novel folder created:", novel_folder_path)
        self.novel_folder_path = novel_folder_path

    def _scrape_chapter_page(self, novel_page_url: str, starting_chapter: str):
        """Scrapes content from each chapter page."""
        chapter_id_list = self.chapters_id
        starting_chapter = self._validated_starting_chapter(starting_chapter)
        if starting_chapter is None:
            raise InvalidStartingChapter

        for chapter_num in range(starting_chapter, len(chapter_id_list)):
            print(">>(info): scraping chapter:", chapter_num + 1)
            print(
                ">>(info): remaining chapter:", len(chapter_id_list) - chapter_num - 1
            )
            chapter_page = f"{novel_page_url}{chapter_id_list[chapter_num]}/"
            self.page.goto(chapter_page, wait_until="load", timeout=210000)

            while True:
                self.page.locator("html").click(timeout=210000)
                self.page.wait_for_load_state("networkidle", timeout=210000)
                num_of_opened_pages = len(self.page.context.pages)
                if num_of_opened_pages > 1:
                    for i in range(1, num_of_opened_pages):
                        self.page.context.pages[i].close()
                sleep(1)
                is_spinning = self.page.query_selector(".spinner-border")
                if not is_spinning:
                    break

            chapter_content_box = self.page.locator("#content-container .contentbox")

            self._remove_ads()
            print(">>(info): taking the screenshot of chapter:", chapter_num + 1)
            chapter_content_bytes = chapter_content_box.screenshot(timeout=210000)
            chapter_content_txt = self._extract_chapter_content(chapter_content_bytes)

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
            self._scrape_chapter_page(novel_page_url, int(starting_chapter))
            self._close_browser()

        except Exception as e:
            print(">>(Error): Errors Occurred during scraping")
            print(">>(Error_Message):", e)

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
                chapter_id_list = [int(chapter_id) for chapter_id in chapters_id]

                self.chapters_id = sorted(chapter_id_list)

    def _get_novel_name(self) -> str:
        """Extracts the novel name from the page."""
        novel_name = self.page.locator("h1#book_name2").text_content(timeout=210000)

        return novel_name

    def _validated_url(self, novel_page_url: str) -> str:
        """Validates and formats the novel page URL."""
        url = novel_page_url

        parse_result = urlparse(url)
        path_pattern = re.compile(r"/(\d+)/?$")
        is_valid_path = bool(re.search(path_pattern, parse_result.path))

        if (
            (parse_result.scheme in ["http", "https"])
            and (parse_result.netloc == "sangtacviet.vip")
            and is_valid_path
        ):
            if parse_result.path.endswith("/"):
                return url
            else:
                return f"{url}/"
        return None

    def _validated_starting_chapter(self, starting_chapter: int) -> int:
        """Validates the starting chapter index."""
        total_chapter = len(self.chapters_id)
        starting_chapter = starting_chapter - 1

        if starting_chapter > -1 and starting_chapter <= total_chapter:
            return starting_chapter
        return None

    def _remove_ads(self):
        """Removes ads from the page."""
        iframes = self.page.query_selector_all("iframe")
        if iframes:
            self.page.evaluate(
                """
                var iframes = document.querySelectorAll('iframe');
                iframes.forEach(function(iframe) {
                    iframe.style.display = 'none';
                });
            """
            )
            return "removed"

    def _validate_download_path(self, download_path: str = None) -> str:
        """Validates and formats the download folder path."""
        download_path = str(download_path).strip()

        is_dir = os.path.isdir(download_path)
        if is_dir:
            is_abs_path = os.path.isabs(download_path)

            if is_abs_path:
                return download_path
            else:
                return os.path.abspath(download_path)
        return None

    def _create_novel_folder(self, download_path, novel_name) -> str:
        """Creates a folder for the novel."""
        # Replace invalid characters with underscores
        sanitized_novel_name = "".join(
            c if c.isalnum() or c in (" ", "-") else "_" for c in novel_name.strip()
        )

        novel_folder_path = os.path.join(download_path, sanitized_novel_name[:250])
        if not os.path.exists(novel_folder_path):
            os.makedirs(novel_folder_path, exist_ok=True)

        return novel_folder_path

    def _translate(self, text: str) -> str:
        """Translates text to English."""
        translator = Translator()

        for _ in range(7):
            try:
                translations = translator.translate(text, src="vi", dest="en")
                translated_text = translations.text
                return translated_text
            except Exception as e:
                print(f">>(warning): {_} retrying to translates: {text[:62]}")
            sleep(1)

        print(">>(warning): Exceeded maximum translation retries. Unable to translate.")
        return None

    def _extract_chapter_content(self, chapter_content_bytes):
        """Extracts chapter content from the screenshot."""
        image = Image.open(io.BytesIO(chapter_content_bytes))
        pytesseract.pytesseract.tesseract_cmd = (
            f"{os.getcwd()}/build/tesseract_ocr/tesseract.exe"
        )
        chapter_content = pytesseract.image_to_string(image, lang="vie")

        return chapter_content

    def _save_chapter(self, chapter_num: int, chapter_content: str) -> bool:
        """Saves the translated chapter content to a file."""
        print(
            ">>(info): chapter:",
            chapter_num + 1,
            " before translate:",
            chapter_content[:62],
            "....",
        )

        novel_folder_path = self.novel_folder_path
        chapter_txt_path = os.path.join(novel_folder_path, f"{chapter_num+1}.txt")

        chunk_size = len(chapter_content) // 3
        paragraphs = [
            chapter_content[i : i + chunk_size]
            for i in range(0, len(chapter_content), chunk_size)
        ]

        translated_chapter = ""
        for p in paragraphs:
            p = str(p).strip()
            if p:
                translation_result = self._translate(p)

            if translation_result is not None:
                translated_chapter += translation_result + "\n"
            else:
                pass

        if not translated_chapter:
            print(
                f"(waring): Unable to translate chapter {chapter_num} content; saved as it is."
            )
        else:
            print(
                ">>(info): chapter:",
                chapter_num + 1,
                " after translate:",
                translated_chapter[:62],
                "....",
            )

        try:
            with open(chapter_txt_path, "w", encoding="utf-8") as file:
                file.write(translated_chapter)
            print(">>(info): chapter:", chapter_num + 1, "saved to:", chapter_txt_path)
        except Exception as e:
            print(f"(waring): unable to save chapter {chapter_num} to file. Error: {e}")
