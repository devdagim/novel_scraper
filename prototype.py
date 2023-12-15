class NovelScraper:
    def __init__(self, novel_page_url, scraping_starting_chapter, download_folder_location) -> None:
        pass
    # playwright utitls
    ## start_playwright
    def _start_playwright() -> pw:
        self.playwright = sync_playwright().start()

    # lanuch browser
    def _launch_browser() -> browser:
        self.browser = self.playwright.chromium.launch()

    # initialize the page
    def _initialize_page() -> page:
        context = self.browser.new_context()

        # Open a new page
        page = context.new_page()
        page.set_default_timeout(0)
        page.route("**/*", self._unload_unwanted_res)

    # unload unwanted resoucresce from the bg
    def _unload_unwanted_res():
        # resource type to be blocked. e.g. image, stylesheet
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
        
        # block popular 3rd party resources like tracking and advertisements.
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
            #....log her
            return route.abort()
        if any(key in route.request.url for key in BLOCK_RESOURCE_NAMES):
            #...log her
            return route.abort()

        return route.continue_()
    
    def _stop_playwright() -> None:
        #https://playwright.dev/python/docs/api/class-playwright#playwright-stop
        self.playwright.stop()