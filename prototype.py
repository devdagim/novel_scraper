from playwright.sync_api import sync_playwright, Page, Browser, Route
from dataclasses import dataclass

@dataclass
class NovelData:
    chapters_id: list[int] = []


class NovelScraper:
    def __init__(self, novel_page_url, starting_chapter, download_folder_path) -> None:
        self.novel_page_url = novel_page_url
        self.start_chapter = starting_chapter
        self.download_folder_path = download_folder_path

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

    # 2. Novel Page Methods

    # 2.1 check if the user entered novel_page_url
    def _validate_url(self, url: str) -> ["str(foramted_url)", "Error"]:
        #TODO...check is its actual url
        #TODO...check is its url has domain of sangtacviet.vip
        #TODO...check is its url has end with int/num=e.g:/1788 or /1777/
        #TODO...valid=set the self.novel_page_url=url in foramt of ending with .../int/ not .../int
        #TODO...invalid=exit program,log..error
        pass

    def _is_valid_starting_chapter(self) -> [bool, "Error"]:
        #TODO...check if starting_chapter is num and <len(chap_id)
        #TODO...num=>true
        #TODO...!num=>while not _is_valid...(): ask for chap num and save to self.starting_chapter=starting_chapter
        pass

    def _validate_folder_path(self, path) -> ["absolute_path", "error"]:
        #TODO...check if path valid=is it realy a path
        #TODO...!isPath=>error,ext
        #TODO...isPath=>check if it exsits

        #TODO...exsits=>absolute_path
        #TODO...!exsits=>error
        pass

    def scrape_novel_page(self) -> ["ext_chapters_id->dataclass.NovelData.chapters_id[]","error occured during scraping"]:
        #TODO...goto=novel_page_url,wight unitl load,chcek if status code=200
        #TODO...!200=error(unable to load the page ...inter error,url_is not corrate,..novel_is_not_found)
        #TODO...200=extract_novel_name=check if its not null
        #TODO...null=error(unable to load the page ...inter error,url_is not corrate,..novel_is_not_found)
        #TODO...!null=translat to eng
        #TODO...!eng=error(unable to translat the novel name,exit)
        #TODO...eng=create_folder(novel_name)
        #TODO...=create_folder(novel_name)
        #TODO...wigth_for chapters to be loaded
        #TODO...if loaded=ext_chapters_id->dataclass.NovelData.chapters_id[]
        #TODO...!loaded=unable to load the chaptes,exsit
        #TODO...null(chapters)=error(novel has no chapters,exit)
        pass

    def scrape_chapter_page(self) -> ["load each chapter and resturn xhr response to the requ","error"]:
        #TODO...if _is_valid_starting_chapter():
        #TODO...>> loop from starting_chapter-len(dataclass.NovelData.chapters_id[])
        #TODO...>> goto.chapter page
        #TODO...>> on_chapter_page_response()...........
        #TODO...>> logo the succc message of the saveed chap and its locaation
        pass

    def on_chapter_page_response():
        pass

    def start_scraping():
        #TODO...impliment the the privat methods here
        pass