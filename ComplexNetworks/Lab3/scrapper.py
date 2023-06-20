import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://ai.pwr.edu.pl"
url = base_url + "/people/"


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
        print('\n')
        print(coauthors)
        print('\n')
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


def get_scholar_

def main():
    people_data = get_all_people()
    links = []
    for x in people_data:
        if x == None: continue
        icon = x.find(class_ = "ai ai-google-scholar")
        parent = None
        try:
            parent = icon.parent
        except:
            continue
        link = parent.get("href")
        if "citations" not in link or "PERSON-ID" in link: continue
        links.append(link)
        print(link)
    print(len(links))
    return
    people_infos = get_people_infos(people_data)

    csv = []
    for person in people_infos:
        csv_person = get_persons_research(person, people_infos)
        csv.extend(csv_person)

    df = pd.DataFrame(csv)
    df.to_csv("output.csv", index=False)


if __name__ == "__main__":
    main()
