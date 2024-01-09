from src.novel_scraper import NovelScraper

scraper = NovelScraper()

issue_novel_page_url = "https://sangtacviet.vip/truyen/faloo/1/1378270/"#input("novel page url: ")
starting_chapter = 1#input("starting chapter to scrap: ")
download_folder_path = "download"#input("Download Folder Path: ")


if __name__ == "__main__":
    scraper.scrap(issue_novel_page_url, starting_chapter, download_folder_path)
