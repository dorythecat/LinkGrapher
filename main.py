from urllib.request import urlopen
import re

url = "https://webscraper.io/test-sites/e-commerce/allinone" # URL to scrape

page = urlopen(url)
html = page.read().decode("utf-8")  # Read and decode the HTML content

direct_links = re.findall('https:*.+?(?=[?"])', html, re.IGNORECASE)  # Find all URLs in the HTML content
