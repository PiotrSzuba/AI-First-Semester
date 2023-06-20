import shutil
import requests
import pandas as pd
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class WorkerInfo:
    def __init__(self, name: str, dona_url: str) -> None:
        self.name = name
        self.dona_url = dona_url

    def to_dict(self):
        return {"name": self.name, "dona_url": self.dona_url}


def get_pages_html(url: str) -> BeautifulSoup:
    page = requests.get(url)
    html_content = page.content
    soup = BeautifulSoup(html_content, "html.parser")

    return soup


def get_base_url(url: str) -> str:
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    return base_url


def get_url(faculty: str, page_number: int) -> str:
    if faculty == "W01":
        return f"https://wa.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W02":
        return f"https://wbliw.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W03":
        return f"https://wch.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W04":
        return f"https://wit.pwr.edu.pl/wydzial/struktura-organizacyjna/pracownicy/page{page_number}.html"
    if faculty == "W05":
        return f"https://weny.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W06":
        return f"https://wggg.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W07":
        return f"https://wis.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W08":
        return f"https://wz.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W09":
        return f"https://wme.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W10":
        return f"https://wm.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W11":
        return f"https://wppt.pwr.edu.pl/pracownicy/page{page_number}.html"
    if faculty == "W12":
        return f"https://wefim.pwr.edu.pl/pracownicy/wizytowki-pracownikow/page{page_number}.html"
    if faculty == "W13":
        return f"https://wmat.pwr.edu.pl/pracownicy/page{page_number}.html" 

def get_dona_url(url: str, name):
    soup = get_pages_html(url)

    link_elements = [p.find("a") for p in soup.find_all("p") if p.find("a") is not None]
    urls = [link_element.get("href") for link_element in link_elements]
    urls = [url for url in urls if url != None]
    dona_url = [url for url in urls if "dona" in url and "lang=pol" in url]
    
    if len(dona_url) > 1:
        raise Exception("Multiple dona urls")

    if len(dona_url) == 0:
        dona_url = [url for url in urls if "dona" in url]
        return dona_url[0] if len(dona_url) != 0 else ""
    
    return dona_url[0]


def get_worker_info_from_box(box, base_url: str) -> WorkerInfo:
    link_element = box.find(class_="title")
    worker_name = link_element.get("title")
    dona_url = get_dona_url(base_url + link_element.get("href"), worker_name)

    print(f" Scraping: {base_url} - {worker_name} - {dona_url}".ljust(shutil.get_terminal_size().columns), end="\r")

    return WorkerInfo(worker_name, dona_url)


def get_workers_from_page(url: str, workers_info: List[WorkerInfo]) -> List[WorkerInfo]:
    base_url = get_base_url(url)
    
    soup = get_pages_html(url)

    next_page_link = soup.find(class_="next")

    worker_boxes = soup.find_all(class_="col-text text-content")
    worker_info_list = [get_worker_info_from_box(box, base_url) for box in worker_boxes]
    
    workers_info += [
        worker_info for worker_info in worker_info_list if worker_info.dona_url != ""
    ]
    
    if next_page_link is None:
        return workers_info

    new_url = next_page_link.get("href")
    return get_workers_from_page(base_url + new_url, workers_info)

# "W01", - no dona urls
faculties = ["W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12", "W13",]
for faculty in faculties:
    workers = get_workers_from_page(get_url(faculty, 1), [])
    df = pd.DataFrame([worker.to_dict() for worker in workers])
    
    df.to_csv(f"raw_data_cache/{faculty}_workers.csv", index=False)
