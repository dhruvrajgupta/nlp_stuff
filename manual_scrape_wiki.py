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


# Extract the plain text content from paragraphs
# paras = []
# for paragraph in soup.find_all('p'):
#     paras.append(str(paragraph.text))

# Extract text from paragraph headers
# heads = []
# for head in soup.find_all('span', attrs={'mw-headline'}):
#     heads.append(str(head.text))

# Interleave paragraphs & headers
# text = [val for pair in zip(paras, heads) for val in pair]
# text = ' '.join(text)

# Drop footnote superscripts in brackets
# text = re.sub(r"\[.*?\]+", '', text)

# Replace '\n' (a new line) with '' and end the string at $1000.
# text = text.replace('\n', '')[:-11]
# print(text)

# for x in text:
#     print(x)

# for x in soup.find_all('span', attrs={'mw-headline'}):
#     print(x.text)
#     for p in x.parent.find_next_siblings('p', limit=1):
#         print(p)
#     print()

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


def get_summary(soup):
    texts_links_list = []
    x = None
    for s in soup.find('span', attrs={'mw-headline'}):
        x = s.parent

    all_p_before_first_heading = x.find_all_previous('p')
    for p in all_p_before_first_heading:
        if p.text.strip() is not "":
            text = convert_plain_text(p.text)
            links = get_wiki_links(p)

            texts_links_list.append((text, links))

    return texts_links_list


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
        table_data.append((text_data, get_wiki_links(rows[i + 1])))

    return table_data


def extract_section(start, end):
    contents = []
    for elem in start.next_siblings:
        if elem == end:
            break
        if elem.name == 'p' or elem.name == "li":
            contents.append(elem)
            print(elem)

    # print(contents)


def all_other_sections(soup):
    section_dict = {}
    para_count = 0
    print(soup)
    all_paras = soup.find_next_siblings(['p'])
    print(all_paras)
    # for i, a in enumerate(all_paras):
    #     print(f"{i} - {a}")
    # print(len(all_paras))
    curr_section = "Summary"
    start = soup.find(name="div", class_="shortdescription")
    for x in soup.find_all('span', attrs={'mw-headline'}):
        # extract_section(start, x)
        print(curr_section)
        print("------------------")
        till = x.parent.find_previous_siblings(['p','ul', 'table'])
        # for a in till:
        #     if a.name == "table":
        #         if "wikitable" in a.get("class"):
        #             print(a)
        #     else:
        #         print(a)
        curr_section = x.text
        # print(f"{para_count} to {till - 1}")
        # for p in range(para_count, till):
        #     element = all_paras[p]
        #     if element.name == "table" and "wikitable" in element.attrs["class"]:
        #         print(extract_table_info(element))
        #     # print(f"{p} - {all_paras[p].text}")
        #
        # curr_section = x.text
        # para_count = till
        # if para_count == 0:
        #     key = "summary"
        #     till = len(x.find_all_previous('p'))
        #     print(key)
        #     print("------------------------")
        #     print(f"{para_count} to {till-1}")
        #     for p in range(para_count, till):
        #         print(f"{p} - {all_paras[p].text}")

        # key = x.text
        #
        # print(x.text)
        # print("------------------------")
        # till = len(x.find_all_previous('p'))
        # print(f"{para_count} to {till-1}")
        # for p in range(para_count, till):
        #     print(str(p)+" - "+all_paras[p].text)
        # para_count += till
        # for p in x.parent.find_next_siblings('p'):
        #     print(p)
        # print()


def main():
    source = urlopen('https://en.wikipedia.org/wiki/Mukesh_Ambani').read()
    soup = BeautifulSoup(source, 'html.parser')
    soup = soup.find('div', {"class": "mw-parser-output"})
    target = soup.find('div', {"class": "reflist"})
    for e in target.find_all_next():
        e.clear()
    # summary = get_summary(soup)

    # For all other sections
    all_other_sections(soup)


if __name__ == "__main__":
    main()
