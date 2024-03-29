import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import wikipediaapi
from tqdm import tqdm
from utilities import get_wikidata_entity_info, wikidata_id_of_wikipage, get_page_views, get_wikipages_info
from utilities import get_wikidata_entity_info, wikidata_id_of_wikipage, get_page_views, get_wikipages_info
from pathlib import Path
import csv

wiki = wikipediaapi.Wikipedia('en')
debug = True
debug_count = 20
debug_entities_meta_count = 1000
data = Path("data")


# TODO separate wikidata info and wikipage info
def make_entity_dict(entity_id, page, wikidata_title, wikidata_url):
    """TODO Remove this"""
    page_wikidata_id = wikidata_id_of_wikipage(page.fullurl.split("/")[-1])
    entity_dict = {
        "wikidata_id": entity_id,
        "page_wikidata_id": page_wikidata_id,
        "wikidata_title": wikidata_title,
        "wikipedia_title": page.title,
        "wikidata_url": wikidata_url,
        "wikipedia_url": page.fullurl,
        # "summary": page.summary
    }
    # text = extract_text_from_sections(page, entity_dict)
    # entity_dict["texts"] = text

    # backlinks = page.backlinks
    # backlinks_urls = []
    # for k, v in backlinks.items():
    #     if ":" not in v.fullurl.split("/")[-1]:
    #         backlinks_urls.append(v.fullurl)
    # print(f"No of Backlinks: {len(backlinks_urls)}")
    # entity_dict["backlinks"] = backlinks_urls

    return entity_dict


def entities_from_file():
    entities_qid_list = []
    with open(data / "test_unique_entities_list.txt", "rt") as f:
        for line in f:
            line = line.rstrip()
            entities_qid_list.append(line)

    return entities_qid_list


def write_wikidata_item_info():
    entities = entities_from_file()

    print("Fetching and writing info for wikidata item...")
    with open(data / "wikidata_item.csv", mode="w") as csv_file:
        fieldnames = ["id", "en_label", "en_description", "enwiki_title"]
        csv_writer = csv.DictWriter(csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL,
                                    fieldnames=fieldnames)
        csv_writer.writeheader()

        for entitiy in tqdm(entities):
            info = get_wikidata_entity_info(entitiy)
            # print(json.dumps(info, indent=4))
            qid = list(info.keys())[0]
            id = qid[1:]

            labels = info[qid].get("labels")
            if labels is None or len(labels) == 0:
                label = None
            else:
                label = labels["en"]["value"]

            descriptions = info[qid].get("descriptions", None)
            if descriptions is None or len(descriptions) == 0:
                description = None
            else:
                description = descriptions["en"]["value"]

            sitelinks = info[qid].get("sitelinks", None)
            if sitelinks is None or len(sitelinks) == 0:
                wiki_title = None
            else:
                wiki_title = sitelinks["enwiki"]["title"]

            wikidata_info = {"id": id, "en_label": label, "en_description": description, "enwiki_title": wiki_title}
            csv_writer.writerow(wikidata_info)


"""
Writing to files methods
"""


def wiki_entity_page_info_to_file(entity_dict):
    with open(f"extracted_entities/{entity_dict['wikidata_id']}.json", "wt") as f:
        f.write(json.dumps(entity_dict))


def somefunciton():
    import pandas as pd
    from tabulate import tabulate
    entities = pd.read_csv(data / "wikidata_item.csv")
    # print(tabulate(entities.head(100), headers='keys', tablefmt='psql'))

    print("Fetching and writing info for wiki pages...")
    with open(data / "enwiki_page.csv", mode="w") as csv_file:
        fieldnames = ["page_id", "page_title", "page_is_redirect", "page_len", "wikidata_numeric_id", "views"]
        csv_writer = csv.DictWriter(csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL,
                                    fieldnames=fieldnames)

        csv_writer.writeheader()

        pbar = tqdm(total=entities.shape[0])

        for index, entity in entities.iterrows():
            pbar.update(1)
            if not isinstance(entity["enwiki_title"], float):
                title = entity["enwiki_title"].replace(" ", "_")
                wikipage_info = get_wikipages_info(title)

                csv_writer.writerow(wikipage_info)

        pbar.close()




def main():

    # Write Wikidata Information (id, en_label, en_description, enwiki_title)
    # Run this function to create wikidata_items.csv file
    # write_wikidata_item_info()

    somefunciton()

    # source = urlopen('https://en.wikipedia.org/wiki/Mukesh_Ambani').read()
    # soup = BeautifulSoup(source, 'html.parser')
    # soup = soup.find('div', {"class": "mw-parser-output"})
    # target = soup.find('div', {"class": "reflist"})
    # for e in target.find_all_next():
    #     e.clear()
    # # summary = get_summary(soup)
    #
    # # For all other sections
    # x = all_sections(soup)
    # import json
    # print(json.dumps(x, indent=2))


if __name__ == "__main__":
    main()
