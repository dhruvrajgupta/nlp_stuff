# from flair.data import Sentence
# from flair.models import SequenceTagger
# from collections import Counter
#
# tagger = SequenceTagger.load("flair/ner-english")
#
# text = "Mukesh Dhirubhai Ambani (born 19 April 1957) is an Indian billionaire heir to the fortune of " \
#        "Reliance Industries. He is the eldest son of Dhirubhai Ambani and is currently the chairman and managing director of " \
#        "Reliance Industries, a Fortune Global 500 company and India's most valuable company by market value. " \
#        "According to Bloomberg Billionaires Index, Ambani's net worth is estimated at $83.4 billion as of " \
#        "February 2023, making him the richest person in Asia and the 13th richest person in the world."
#
# sentence = Sentence(text)
# tagger.predict(sentence)
# for entity in sentence.get_spans('ner'):
#     print(entity)


from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


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


def extract_section(start, end):
    contents = []
    for elem in start.next_siblings:
        if elem == end:
            break
        if elem.name == 'p' or elem.name == "li":
            contents.append(elem)
            print(elem)


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


def main():
    source = urlopen('https://en.wikipedia.org/wiki/Mukesh_Ambani').read()
    soup = BeautifulSoup(source, 'html.parser')
    soup = soup.find('div', {"class": "mw-parser-output"})
    target = soup.find('div', {"class": "reflist"})
    for e in target.find_all_next():
        e.clear()
    # summary = get_summary(soup)

    # For all other sections
    x = all_sections(soup)
    import json
    print(json.dumps(x, indent=2))


if __name__ == "__main__":
    main()
