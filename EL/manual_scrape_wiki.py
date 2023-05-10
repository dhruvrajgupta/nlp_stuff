import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import wikipediaapi
from tqdm import tqdm
from utilities import get_entity_info, wikidata_id_of_wikipage
from pathlib import Path

wiki = wikipediaapi.Wikipedia('en')
debug = True
debug_count = 20
debug_entities_meta_count = 1000
data = Path("data")


# TODO separate wikidata info and wikipage info
def make_entity_dict(entity_id, page, wikidata_title, wikidata_url):
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


def write_wiki_info():
    pbar = None

    with open(data / 'entity_meta_info.jsonl', 'r') as json_file:
        json_list = list(json_file)

    print("Fetching info from wikipedia...")

    if debug:
        pbar = tqdm(total=debug_count)
    else:
        json_list = tqdm(json_list)
    c = 0

    for json_str in json_list:
        result = json.loads(json_str)
        entity_id = list(result.keys())[0]
        sitelinks = result[entity_id].get("sitelinks", None)
        if sitelinks is not None and len(sitelinks) > 0:

            if debug and c == debug_count:
                break

            wikidata_title = sitelinks["enwiki"]["title"]
            wikidata_url = sitelinks["enwiki"]["url"]
            page = wiki.page(wikidata_title)
            if page.exists():
                if pbar is not None and c <= debug_count:
                    c += 1
                    pbar.update(1)

                entity_dict = make_entity_dict(entity_id, page, wikidata_title, wikidata_url)
                print(json.dumps(entity_dict, indent=2))
                # wiki_info_to_file(entity_dict)
            else:
                if debug:
                    print(f"Failed to fetch info - {wikidata_title}")

    if pbar is not None:
        pbar.close()


"""
Writing to files methods
"""


def wiki_entity_page_info_to_file(entity_dict):
    with open(f"extracted_entities/{entity_dict['wikidata_id']}.json", "wt") as f:
        f.write(json.dumps(entity_dict))


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

    write_wiki_info()

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
