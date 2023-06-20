import time

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
from scholarly import scholarly
from scholarly import ProxyGenerator, scholarly

base_url = "https://ai.pwr.edu.pl"
url = base_url + "/people/"

pg = ProxyGenerator()


def get_all_people():
    response = requests.get(url)

    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")
    people_table_data = soup.find_all(class_="people-person")
    return people_table_data


def get_person_info(person):
    title = person.find(class_="portrait-title")
    h2 = title.find("h2")
    a = h2.find("a")
    return a.text, base_url + a.get("href")


def get_people_infos(people_data):
    people_infos = []
    for i, x in enumerate(people_data):
        data_tuple = get_person_info(x)
        data_dict = {
            "id": i,
            "name": data_tuple[0],
            "url": data_tuple[1],
        }
        people_infos.append(data_dict)
    return people_infos


def get_persons_research(person_info, people_list):
    response = requests.get(person_info["url"])
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find(class_="article-widget content-widget-hr")
    ul = None
    try:
        ul = table.find("ul")
    except:
        return []

    rows = ul.find_all("li")

    csv = []

    for row in rows:
        link_elem = row.find("a")
        research_link = base_url + link_elem.get("href")
        coauthors = get_coauthors(research_link, person_info, people_list)

        if len(coauthors) == 0:
            continue
        print("\n")
        print(coauthors)
        print("\n")
        csv.extend(coauthors)

    return csv


def get_coauthors(url, person_info, people_list: list) -> list:
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, "html.parser")
    article = soup.find(class_="article-metadata")
    div = article.find("div")
    spans = div.find_all("span")

    csv_rows = []
    for span in spans:
        link_elem = span.find("a")
        name = link_elem.text

        for person in people_list:
            if person["name"] != name or name == person_info["name"]:
                continue
            csv_rows.append(
                {
                    "source": person_info["id"],
                    "target": person["id"],
                    "source_label": person_info["name"],
                    "target_label": person["name"],
                }
            )
    return csv_rows if len(csv_rows) > 1 else []


def get_links_with_names(people_data):
    links = []
    for x in people_data:
        if x == None:
            continue

        data_tuple = get_person_info(x)
        name = data_tuple[0]

        icon = x.find(class_="ai ai-google-scholar")
        parent = None
        try:
            parent = icon.parent
        except:
            continue
        link = parent.get("href")
        if "citations" not in link or "PERSON-ID" in link:
            continue
        links.append((link, name))
    return links


def get_research_from_pwr_ai(people_data):
    people_infos = get_people_infos(people_data)

    csv = []
    for person in people_infos:
        csv_person = get_persons_research(person, people_infos)
        csv.extend(csv_person)

    df = pd.DataFrame(csv)
    df.to_csv("output.csv", index=False)


def get_publications_filled(author_id) -> list[dict[str, str]]:
    author = scholarly.search_author_id(author_id)
    author = scholarly.fill(author)
    result = []
    for pub in tqdm(author["publications"]):
        result.append(scholarly.fill(pub))
    return result


def get_coauthors_scholarly(author_id):
    author = scholarly.search_author_id(author_id)
    author = scholarly.fill(author)

    coauthors = []

    for pub in author["publications"]:
        pub_filled = scholarly.fill(pub)
        publication_title = pub_filled["bib"].get("title", "")
        author_string = pub_filled["bib"].get("author", "")
        authors = [author_name.strip() for author_name in author_string.split(",")]
        # print(authors)

    return coauthors


def extract_author_id(url):
    query_start = url.find("?")
    if query_start == -1:
        return None

    query_string = url[query_start + 1 :]
    query_params = query_string.split("&")

    for param in query_params:
        key_value = param.split("=")
        if len(key_value) == 2 and key_value[0] == "user":
            return key_value[1]

    return None


def main():
    people_data = get_all_people()

    links_with_names = get_links_with_names(people_data)

    for link, name in links_with_names:
        author_id = extract_author_id(link)
        coauthors = get_coauthors_scholarly(author_id)
        print(coauthors)

    return
    get_research_from_pwr_ai(people_data)


def extract_raw_publications():
    people = get_all_people()
    links_with_names: list[tuple[str, str]] = get_links_with_names(people)

    pg.FreeProxies()
    scholarly.use_proxy(pg)

    data: list[dict] = []

    # (5) Kwasnicka - podlinkowany scholar kajdanowicza
    # (17) Michał Karol ma scholar ale brak prac
    for i, (link, name) in tqdm(enumerate(links_with_names)):
        if i <= 17:
            continue
        author_id = extract_author_id(link)
        pubs = get_publications_filled(author_id)
        data += pubs
        pub_df = pd.DataFrame(pubs).astype("str")
        pub_df.to_parquet(f"pubs_raw/{i}_{name}_pubs.parquet", index=False)

    df = pd.DataFrame(data).astype("str")
    df.to_parquet("publications.parquet", index=False)


if __name__ == "__main__":
    extract_raw_publications()
    # main()
