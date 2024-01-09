# Novel Scraper Documentation

First of All Thank you for choosing Me for this project! 
This documentation will guide you through the installation process and provide instructions on how to run the scraper effectively on your Windows operating system.

## Installation

### 1. Copy the `novel_scraper` folder to your desired location:

copy the `novel_scraper` folder to your chosen directory. For example:
```bash
cp novel_scraper C:\\Documents\
```
### 2. Open the `novel_scraper` folder with a text editor.

### 3. Create a virtual environment (venv) in the `novel_scraper` folder:

Run the following commands in the command prompt:

```bash
python -m venv venv
```

Activate the virtual environment:
```bash
venv\Scripts\activate
```

### 4. Install required Python packages for the project:

Inside the activated virtual environment, run:
```bash
pip install -r requirements.txt
```

on the last, install the Playwright browser automation framework dependency:
```bash
playwright install
```


## Running Guide
Run the scraper script

To start scraping, run the following command:
```bash
python main.py
```

Input the following parameters when prompted:

`novel_page_url`: The URL of the novel page you want to scrape.<br>
`starting_chapter`: The starting chapter number for scraping. If it's the first time, set it to 1. If there was a previous failure, set it to the last successfully scraped chapter.<br>
`download_folder_path`: Enter the download folder path. If it's the first time, use "download". If there was a previous failure, specify the folder path within the "download" directory where the failed scraping occurred.<br>
For example, if you want to continue scraping from where it left off due to a network error:

`novel_page_url`: [URL]<br>
`starting_chapter`: [last successfully scraped chapter] or 1<br>
`download_folder_path`: "download/novel_page_folder" or "download"<br>
<br><br>
Feel free to contact me if you have any questions or issues. Happy scraping!
