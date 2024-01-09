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
