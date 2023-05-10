import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import wikipediaapi
from tqdm import tqdm
from utilities import get_entity_info
from pathlib import Path

wiki = wikipediaapi.Wikipedia('en')
debug = True
debug_count = 20
debug_entities_meta_count = 1000
data = Path("data")


def entities_from_file():
    entities_qid_list = []
    with open(data / "test_unique_entities_list.txt", "rt") as f:
        for line in f:
            line = line.rstrip()
            entities_qid_list.append(line)

    return entities_qid_list


"""
Writing to files methods
"""


def write_wikidata_meta_info_file():
    """
    Get Wikipedia links from wikidata for the given entity from file
    """
    entities_qid_list = entities_from_file()
    with open(data / "entity_meta_info.jsonl", "wt") as f:
        if debug:
            en_list = entities_qid_list[:debug_entities_meta_count]
        else:
            en_list = entities_qid_list

        print("Writing entity meta info to file...")
        for i, qid in enumerate(tqdm(en_list)):
            f.write(get_entity_info(qid))
            f.write("\n")


def write_no_urls_entities():
    no_urls_entities = []
    with open(data / 'entity_meta_info.jsonl', 'r') as json_file:
        json_list = list(json_file)

    print("Writing to file entities having no sitelinks....")
    for json_str in tqdm(json_list):
        meta_str = json.loads(json_str)
        entity_id = list(meta_str.keys())[0]
        sitelinks = meta_str[entity_id].get("sitelinks", None)

        if sitelinks is None:
            no_urls_entities.append(json_str)
        else:
            if len(sitelinks) == 0:
                no_urls_entities.append(json_str)

    with open(data / "entities_with_no_url.jsonl", "wt") as f:
        for ent in no_urls_entities:
            f.write(ent)


def main():
    # Wikidata's entity page links, page titles and page sitelinks
    # write_wikidata_meta_info_file()

    # List of Wikidata entities not having sitelinks
    # write_no_urls_entities()

    pass

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
