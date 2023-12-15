from playwright.sync_api import sync_playwright, Page, Browser, Route

class NovelScraper:
    def __init__(self, novel_page_url, start_chapter, download_folder_location) -> None:
        self.novel_page_url = novel_page_url
        self.scraping_starting_chapter = scraping_starting_chapter
        self.download_folder_location = download_folder_location

    # 1. Playwright Utilities

    # 1.1 Start Playwright
    def _start_playwright(self) -> None:
        #TODO...log info
        self.playwright = sync_playwright().start()

    # 1.2 Launch Browser
    def _launch_browser(self) -> None:
        #TODO...log info
        self.browser = self.playwright.chromium.launch()

    # 1.3 Initialize the Page
    def _initialize_page(self) -> None:
        #TODO...log info
        context = self.browser.new_context()

        # Open a new page
        page = context.new_page()
        page.set_default_timeout(0)
        page.route("**/*", self._unload_unwanted_resources)  # Corrected method name

        self.page = page

    # 1.4 Unload Unwanted Resources from the Background
    def _unload_unwanted_resources(self, route: Route) -> None:
        # Resource types to be blocked, e.g., image, stylesheet
        BLOCK_RESOURCE_TYPES = [
            "beacon",
            "csp_report",
            "font",
            # "image",
            # "imageset",
            "media",
            "object",
            "texttrack",
            # "stylesheet",
        ]

        # Block popular 3rd-party resources like tracking and advertisements.
        BLOCK_RESOURCE_NAMES = [
            "service.supercounters.com",
            "analytics",
            "doubleclick",
            "exelator",
            "ads",
            "google",
            "google-analytics",
            "googletagmanager",
            "woafoame"
        ]

        if route.request.resource_type in BLOCK_RESOURCE_TYPES:
            #TODO... log info
            return route.abort()
        if any(key in route.request.url for key in BLOCK_RESOURCE_NAMES):
            #TODO ... log info
            return route.abort()

        return route.continue_()

    # 1.5 Close the Browser
    def _close_browser(self) -> None:
        #TODO...log info
        self.browser.close()

    # 1.6 Stop Playwright
    def _stop_playwright(self) -> None:
        # https://playwright.dev/python/docs/api/class-playwright#playwright-stop
        #TODO...log info
        self.playwright.stop()