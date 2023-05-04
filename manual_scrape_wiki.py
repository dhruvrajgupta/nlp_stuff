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


def main():
    source = urlopen('https://en.wikipedia.org/wiki/Mukesh_Ambani').read()
    soup = BeautifulSoup(source, 'html.parser')
    print(get_summary(soup))

if __name__ == "__main__":
    main()