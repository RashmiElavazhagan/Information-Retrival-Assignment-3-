import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['crawler_db']
collection = db['pages']

class Frontier:
    def __init__(self):
        self.urls = set()
        self.queue = []

    def addURL(self, url):
        if url not in self.urls:  
            self.urls.add(url)
            self.queue.append(url)

    def nextURL(self):
        return self.queue.pop(0)

    def done(self):
        return len(self.queue) == 0

    def clear(self):
        self.urls.clear()
        self.queue.clear()

def retrieveHTML(url):
    try:
        response = urllib.request.urlopen(url)
        if "text/html" in response.headers.get("Content-Type", ""):
            return response.read()
        return None
    except Exception as e:
        print(f"Error retrieving URL {url}: {e}")
        return None

def storePage(url, html):
    if html:
        collection.insert_one({"url": url, "html": html.decode('utf-8')})
        print(f"Stored: {url}")

def parseHTML(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        link = urljoin(base_url, href)  
        if "cpp.edu/sci/computer-science/" in link:  
            links.append(link)
    return links

def target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find("h1", class_="cpp-h1")
    return heading and heading.text.strip() == "Permanent Faculty"

def crawlerThread(frontier):
    while not frontier.done():
        url = frontier.nextURL()
        print(f"Visiting: {url}")
        html = retrieveHTML(url)

        if html is None:
            continue

        storePage(url, html)

        if target_page(html):
            print(f"Target page found: {url}")
            frontier.clear()
            break

        for link in parseHTML(html, url):
            frontier.addURL(link)

if __name__ == "__main__":
    start_url = "https://www.cpp.edu/sci/computer-science/"
    frontier = Frontier()
    frontier.addURL(start_url)
    crawlerThread(frontier)
