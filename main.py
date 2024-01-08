from src.novel_scraper import NovelScraper
import logging

logging.basicConfig(level=logging.INFO)




#saving a

novel_page_url = input("novel page url: ")
starting_chapter = input("starting chapter to scrap: ")
download_folder_path = input("Download Folder Path: ")

# try:
scraper = NovelScraper()
scraper.scrap(novel_page_url,int(starting_chapter),download_folder_path)
# except Exception as e:
#     print(">>(error): occurred during scraping:",e)