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
