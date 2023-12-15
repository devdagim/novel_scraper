import playwright.sync_api as pw
import os

class NovelScraper:
    def __init__(self, novel_url, output_folder):
        self.novel_url = novel_url
        self.output_folder = output_folder
        self.browser = None

    def initialize_browser(self):
        self.browser = pw.chromium.launch()

    def fetch_novel_page(self):
        if not self.browser:
            self.initialize_browser()

        page = self.browser.new_page()
        page.goto(self.novel_url)
        novel_page_content = page.content()
        page.close()

        return novel_page_content

    def scrape_chapters(self, novel_page_content):
        # Implement your chapter scraping logic here
        # For example, using BeautifulSoup or other parsing libraries
        # Extract chapter URLs, titles, and content

        # For demonstration purposes, let's assume you have a list of chapters
        chapters = [{'title': 'Chapter 1', 'content': '...'}, {'title': 'Chapter 2', 'content': '...'}]

        return chapters

    def store_data(self, chapters):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for index, chapter in enumerate(chapters, start=1):
            chapter_title = chapter['title']
            chapter_content = chapter['content']

            # Save each chapter as a text file in the output folder
            filename = f"{index}_{chapter_title}.txt"
            filepath = os.path.join(self.output_folder, filename)

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(chapter_content)

    def close_browser(self):
        if self.browser:
            self.browser.close()

# Example usage:
novel_url = "https://example.com/novel"
output_folder = "novel_output"
novel_scraper = NovelScraper(novel_url, output_folder)

try:
    novel_page_content = novel_scraper.fetch_novel_page()
    chapters = novel_scraper.scrape_chapters(novel_page_content)
    novel_scraper.store_data(chapters)

finally:
    novel_scraper.close_browser()




# method 2
import requests
from bs4 import BeautifulSoup
import os

def fetch_novel_page(novel_url):
    """
    Fetches the content of the novel page.

    Parameters:
    - novel_url (str): The URL of the novel page.

    Returns:
    - str: The content of the novel page.
    """
    response = requests.get(novel_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch novel page. Status code: {response.status_code}")

def scrape_chapters(novel_page_content):
    """
    Scrapes chapters from the novel page content.

    Parameters:
    - novel_page_content (str): The content of the novel page.

    Returns:
    - list: A list of dictionaries representing chapters.
    """
    # Implement your chapter scraping logic using BeautifulSoup or other parsing libraries
    # This is a placeholder example; modify it based on the structure of your novel page
    soup = BeautifulSoup(novel_page_content, 'html.parser')
    chapters = [{'title': 'Chapter 1', 'content': '...'}, {'title': 'Chapter 2', 'content': '...'}]

    return chapters

def store_data(chapters, output_folder):
    """
    Stores the scraped chapters as text files in the specified output folder.

    Parameters:
    - chapters (list): A list of dictionaries representing chapters.
    - output_folder (str): The folder where text files will be stored.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for index, chapter in enumerate(chapters, start=1):
        chapter_title = chapter['title']
        chapter_content = chapter['content']

        # Save each chapter as a text file in the output folder
        filename = f"{index}_{chapter_title}.txt"
        filepath = os.path.join(output_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(chapter_content)

# Example usage:
novel_url = "https://example.com/novel"
output_folder = "novel_output"

novel_page_content = fetch_novel_page(novel_url)
chapters = scrape_chapters(novel_page_content)
store_data(chapters, output_folder)
