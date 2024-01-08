from src.novel_scraper import NovelScraper



#saving a

novel_page_url = "https://sangtacviet.vip/truyen/sangtac/1/17488/"#input("novel page url: ")
starting_chapter = 1#input("starting chapter to scrap: ")
download_folder_path = "download"#input("Download Folder Path: ")

# try:
scraper = NovelScraper()
scraper.scrap(novel_page_url,int(starting_chapter),download_folder_path)
# except Exception as e:
#     print(">>(error): occurred during scraping:",e)