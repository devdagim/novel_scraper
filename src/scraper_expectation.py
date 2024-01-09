class NovelPageLoadError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NovelNameExtractingError(Exception):
    def __init__(self, message=None):
        message = "Error extracting novel name. Please double-check that the \
            HTML structure includes the selector (h1#book_name2) or try again later.."
        super().__init__(message)


class EmptyChapterListError(Exception):
    def __init__(self, message=None):
        message = "Error extracting chapter list. Unable to retrieve chapters or they might be unavailable. Please retry, or check if there are no chapters available."
        super().__init__(message)


class TranslationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidNovelPageUrl(Exception):
    def __init__(self, message=None):
        message = "Invalid Novel Page URL. Please ensure the provided URL is correct and try again."
        super().__init__(message)


class InvalidDownloadPath(Exception):
    def __init__(self, message=None):
        message = "Invalid Novel Download Path. Please enter the correct Path of Download Folder."
        super().__init__(message)


class InvalidStartingChapter(Exception):
    def __init__(self, message=None):
        message = "Invalid Starting Chapter. Please enter the correct Starting of the Chapter that you want to scrape."
        super().__init__(message)
