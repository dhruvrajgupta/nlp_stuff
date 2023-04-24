from urllib.request import urlopen
import json
from tqdm import tqdm
import wikipediaapi

url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}&languages=en&props=descriptions|sitelinks%2Furls&sitefilter=enwiki&format=json"
entities_qid_list = []
wiki = wikipediaapi.Wikipedia('en')
debug = False


def get_entity_info(qid):
    qurl = url.format(qid=qid)
    response = urlopen(qurl)
    data_json = json.loads(response.read())

    return json.dumps(data_json["entities"])


def entities_from_file():
    with open("test_unique_entities_list.txt", "rt") as f:
        for line in f:
            line = line.rstrip()
            entities_qid_list.append(line)

    return entities_qid_list


def write_meta_info_file():
    entities_qid_list = entities_from_file()
    with open("entity_meta_info.jsonl", "wt") as f:
        if debug:
            en_list = entities_qid_list[:100]
        else:
            en_list = entities_qid_list

        print("Writing entity meta info to file...")
        for i, qid in enumerate(tqdm(en_list)):
            f.write(get_entity_info(qid))
            f.write("\n")


def wiki_info_to_file(info_dict):
    with open(f"extracted_entities/{info_dict['wikidata_id']}.json", "wt") as f:
        f.write(json.dumps(info_dict))


def print_links(page):
    links = page.links
    for title in sorted(links.keys()):
        print("%s: %s" % (title, links[title]))


def write_wiki_info():
    no_urls_entities = []
    diff_urls_ents = []

    with open('entity_meta_info.jsonl', 'r') as json_file:
        json_list = list(json_file)

    print("Fetching info from wikipedia...")
    for json_str in tqdm(json_list):
        entity_dict = {}
        result = json.loads(json_str)
        entity_id = list(result.keys())[0]
        sitelinks = result[entity_id].get("sitelinks", None)
        if sitelinks is not None:
            if len(sitelinks) > 0:
                title = sitelinks["enwiki"]["title"]
                url = sitelinks["enwiki"]["url"]
                page = wiki.page(title)
                if page.exists():
                    # check whether the page is exact as the url
                    if page.fullurl != url:
                        entity_dict["page_url"] = page.fullurl
                        entity_dict["page_title"] = page.title
                        diff_urls_ents.append(entity_dict)
                        print(f"meta url - {url}")
                        print(f"page url - {page.fullurl}")

                    summary = page.summary
                    entity_dict["wikidata_id"] = entity_id
                    entity_dict["title"] = title
                    entity_dict["url"] = url
                    entity_dict["summary"] = summary
                    wiki_info_to_file(entity_dict)
                else:
                    print(f"Failed to fetch info - {title}")
            else:
                no_urls_entities.append(json_str)
        else:
            print("None sitelink - {entity_id}")

    write_no_urls_entities(no_urls_entities)
    with open(f"different_urls.jsonl", "wt") as f:
        for ent in diff_urls_ents:
            f.write(json.dumps(ent))
            f.write("\n")


def write_no_urls_entities(ents):
    with open("entities_with_no_url.jsonl", "wt") as f:
        for ent in ents:
            f.write(ent)


if __name__ == "__main__":
    # write_meta_info_file()
    write_wiki_info()
