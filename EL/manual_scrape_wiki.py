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


def main():
    write_wikidata_meta_info_file()

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
