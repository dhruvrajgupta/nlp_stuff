import re
from urllib.request import urlopen
import urllib.parse
import json
from urllib.error import HTTPError

wikidata_info_url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}&languages=en" \
          "&props=labels|descriptions|sitelinks%2Furls&sitefilter=enwiki&format=json"

# id_from_page_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles={title}"

pageview_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/" \
               "all-agents/{title}/monthly/2022100100/2022103100"

wikipage_info_url = "https://en.wikipedia.org/w/api.php?action=query&prop=info|redirects|pageprops&titles={title}&format=json"


def convert_plain_text(html_text):
    # Drop footnote superscripts in brackets
    text = re.sub(r"\[.*?\]+", '', html_text)
    return text


def get_wiki_links(html_text):
    links_list = []
    # Returns a list of tuple
    # (text[in the wikipedia text], title[of the link], link)
    links = html_text.find_all('a', href=lambda href: href and href.startswith("/wiki/"))
    for l in links:
        links_list.append((l.text, l.get('title'), l.get('href')))

    return links_list


def extract_table_info(wikitable):
    table_data = []
    # Find all rows in the wikitable
    rows = wikitable.find_all("tr")

    # Extract the headers from the first row
    headers = [header.text.strip() for header in rows[0].find_all("th")]

    # Extract the data from each row
    data = []
    for row in rows[1:]:
        # Find all cells in the row
        cells = row.find_all("td")

        # Extract the text from each cell
        row_data = [cell.text.strip() for cell in cells]

        # Combine the header and row data into a dictionary
        row_dict = {}
        for i in range(len(headers)):
            row_dict[headers[i]] = row_data[i]

        # Add the row dictionary to the data list
        data.append(row_dict)

    # Print the data list
    for i, row in enumerate(data):
        text_data = ""
        for header in headers:
            text_data += f"{header}: {row[header]}\n"
        table_data.append((convert_plain_text(text_data), get_wiki_links(rows[i + 1])))

    return table_data


def extract_ul(element):
    li_list = []
    li = element.find_all('li')
    for item in li:
        text = convert_plain_text(item.text)
        links = get_wiki_links(item)
        li_list.append((text, links))

    return li_list


def all_sections(soup):
    section_dict = {}
    x = soup.next
    all_paras = x.find_next_siblings(['p', 'ul', 'table'])
    curr_section = "Summary"
    para_count = 0
    for x in soup.find_all('span', attrs={'mw-headline'}):
        section_content_list = []

        till = len(x.parent.find_previous_siblings(['p', 'ul', 'table']))

        for p in range(para_count, till):
            element = all_paras[p]
            if element.name == "table" and "wikitable" in element.attrs["class"]:
                for item in extract_table_info(element):
                    section_content_list.append(item)

            if element.name == "p" and element.text.strip() != "":
                text = convert_plain_text(element.text)
                links = get_wiki_links(element)
                section_content_list.append((text, links))

            if element.name == "ul":
                for item in extract_ul(element):
                    section_content_list.append(item)

        section_dict[curr_section] = section_content_list

        para_count = till
        curr_section = x.text

    return section_dict


def get_wikidata_entity_info(qid):
    qurl = wikidata_info_url.format(qid=qid)
    response = urlopen(qurl)
    data_json = json.loads(response.read())

    return data_json["entities"]


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


def get_page_views(wikipage_title):
    url = pageview_url.format(title=wikipage_title)
    response = urlopen(url)
    data_json = json.loads(response.read())

    views = data_json["items"][0]["views"]

    return views


def get_wikipages_info(wikipage_title):
    try:
        wikipage_title = urllib.parse.quote_plus(wikipage_title)
        url = wikipage_info_url.format(title=wikipage_title)
        response = urlopen(url)
        data_json = json.loads(response.read())

        page = list(data_json["query"]["pages"].keys())[0]
        page = data_json["query"]["pages"][page]
        page_id = page["pageid"]

        page_title = page["title"]

        page_is_redirect = page.get("redirects", None)
        if page_is_redirect is None:
            page_is_redirect = 0
        else:
            page_is_redirect = 1

        page_len = page["length"]

        wikidata_numeric_id = page["pageprops"]["wikibase_item"]
        views = get_page_views(wikipage_title)

        return {
            "page_id": page_id,
            "page_title": page_title,
            "page_is_redirect": page_is_redirect,
            "page_len": page_len,
            "wikidata_numeric_id": wikidata_numeric_id,
            "views": views
        }
    except HTTPError as e:
        return {
            "page_id": None,
            "page_title": wikipage_title,
            "page_is_redirect": None,
            "page_len": None,
            "wikidata_numeric_id": None,
            "views": None
        }
