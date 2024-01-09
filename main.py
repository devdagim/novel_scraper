from src.novel_scraper import NovelScraper

scraper = NovelScraper()

novel_page_url = input("novel page url: ")
starting_chapter = input("starting chapter to scrap: ")
download_folder_path = input("Download Folder Path: ")


if __name__ == "__main__":
    scraper.scrap(novel_page_url, starting_chapter, download_folder_path)
