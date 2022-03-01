# Written by Damion Maser
# CS361
# Microservice for final project implementation
# Description: Takes in a wikipedia URL and returns the title of the page and the first paragraph of information

import requests
from bs4 import BeautifulSoup
import re

# Opens document to receive the URL of the website to scrape
try:
    g = open("./input.txt", 'r+')
    URL = g.read()
    page = requests.get(URL)
    g.close()

    # Starts the parsing process and the information we want to find
    soup = BeautifulSoup(page.content, "html.parser")
    header = soup.find(id="firstHeading")

    par = []
    for content in soup.find_all('p'):
        par.append(str(content.text))

    text = re.sub(r"\[.*?]+", '', str(par))
    text = text[:1500]
    text = text.rstrip("\n")

    # Process information. Strip the text of all the unneeded tags. Write to document.
    w = header.text.strip()
    f = open("tester.txt", "w", encoding="utf-8")
    f.write(w)
    f.write("\n\n")  # Spaces for visual clarity
    f.write(str(text))
    f.close()

except IOError:
    print("File not found.")
