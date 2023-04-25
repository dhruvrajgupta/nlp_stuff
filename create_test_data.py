import sys
from urllib.request import urlopen
import json
from tqdm import tqdm
import wikipediaapi

url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={" \
      "qid}&languages=en&props=descriptions|sitelinks%2Furls&sitefilter=enwiki&format=json"
id_from_page_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles={title}"

wiki = wikipediaapi.Wikipedia('en')
debug = True
debug_count = 5
debug_entities_meta_count = 1000


def extract_text_from_sections(page, entity_dict):
    # extracted_texts = []
    if debug:
        print("\n")
        print(f"Wikidata Title:\t{entity_dict['wikidata_title']}")
        print(f"Wikipedia Title:\t{page.title}\n")
        # print(f"Texts containing {entity_dict['wikidata_title']}")
    sections = page.sections
    sections_text_list = get_section_text(sections, [])
    # for x in sections_text_list:
    #     if entity_dict['wikidata_title'] in x:
    #         if debug:
    #             print(x)
    #     extracted_texts.append(x)

    return sections_text_list


def get_section_text(sections, sections_text_list):
    for s in sections:
        if s.title not in ["Bibliography", "References", "External links"]:
            sections_text_list.append(f"{s.title}#{s.text}")
            get_section_text(s.sections, sections_text_list)

    return sections_text_list


def wikidata_id_of_wikipage(wikidata_title_normalized):
    """
    If the ids on the page and wikidata match many references will available for the entity
    != Akash Ambani, Mukesh Ambani

    :returns wikidata_id of the WikiPage
    """
    idurl = id_from_page_url.format(title=wikidata_title_normalized)
    response = urlopen(idurl)
    data_json = json.loads(response.read())

    pages_dict = data_json["query"]["pages"]
    pageid = list(pages_dict.keys())[-1]
    page_wikidata_id = pages_dict[pageid]["pageprops"]["wikibase_item"]

    return page_wikidata_id


def write_wiki_info():
    pbar = None
    no_urls_entities = []

    with open('entity_meta_info.jsonl', 'r') as json_file:
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
        if sitelinks is not None:
            if len(sitelinks) > 0:

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
                    wiki_info_to_file(entity_dict)
                else:
                    if debug:
                        print(f"Failed to fetch info - {wikidata_title}")
            else:
                no_urls_entities.append(json_str)
        else:
            if debug:
                print("None sitelink - {entity_id}")

    if pbar is not None:
        pbar.close()

    write_no_urls_entities(no_urls_entities)


def make_entity_dict(entity_id, page, wikidata_title, wikidata_url):
    page_wikidata_id = wikidata_id_of_wikipage(page.fullurl.split("/")[-1])
    entity_dict = {"wikidata_id": entity_id, "page_wikidata_id": page_wikidata_id, "wikidata_title": wikidata_title,
                   "wikipedia_title": page.title,
                   "wikidata_url": wikidata_url,
                   "wikipedia_url": page.fullurl, "summary": page.summary}
    text = extract_text_from_sections(page, entity_dict)
    entity_dict["texts"] = text

    return entity_dict



"""
URL Request methods
"""


def get_entity_info(qid):
    qurl = url.format(qid=qid)
    response = urlopen(qurl)
    data_json = json.loads(response.read())

    return json.dumps(data_json["entities"])


"""
Reading File methods
"""


def entities_from_file():
    entities_qid_list = []
    with open("test_unique_entities_list.txt", "rt") as f:
        for line in f:
            line = line.rstrip()
            entities_qid_list.append(line)

    return entities_qid_list


"""
Writing to Files methods
"""


def wiki_info_to_file(entity_dict):
    with open(f"extracted_entities/{entity_dict['wikidata_id']}.json", "wt") as f:
        f.write(json.dumps(entity_dict))


# TODO: Refactor this
def write_different_urls(diff_urls_ents):
    with open(f"different_urls.jsonl", "wt") as f:
        for ent in diff_urls_ents:
            f.write(json.dumps(ent))
            f.write("\n")


def write_meta_info_file():
    entities_qid_list = entities_from_file()
    with open("entity_meta_info.jsonl", "wt") as f:
        if debug:
            en_list = entities_qid_list[:debug_entities_meta_count]
        else:
            en_list = entities_qid_list

        print("Writing entity meta info to file...")
        for i, qid in enumerate(tqdm(en_list)):
            f.write(get_entity_info(qid))
            f.write("\n")


def write_no_urls_entities(ents):
    with open("entities_with_no_url.jsonl", "wt") as f:
        for ent in ents:
            f.write(ent)


if __name__ == "__main__":
    # write_meta_info_file()
    write_wiki_info()
