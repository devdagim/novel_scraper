class NovelPageLoadError(Exception):
   def __init__(self, message=None):
        self.message = "Error during loading the novel page. Please try again or \
            check the novel page URL by opening it in a web browser."
        super().__init__(message)

class NovelNameExtractingError(Exception):
    def __init__(self, message=None):
        self.message = "Error extracting novel name. Please double-check that the \
            HTML structure includes the selector (h1#book_name2) or try again later.."
        super().__init__(message)


class EmptyChapterListError(Exception):
    def __init__(self, message=None):
        self.message = "Error extracting chapter list. Unable to retrieve chapters or they might be unavailable. Please retry, or check if there are no chapters available."
        super().__init__(message)


class TranslationError(Exception):
    pass

class SavingFileError(Exception):
    pass