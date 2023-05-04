from flair.data import Sentence
from flair.models import SequenceTagger
import os
import json
from pathlib import Path
from collections import Counter
import re

## Compare this with spacy

# sentence = Sentence("I love berlin and new york. I dont know about the rest.")
#
tagger = SequenceTagger.load("flair/ner-english")


#
# tagger.predict(sentence)
#
# for entity in sentence.get_spans('ner'):
#     print(entity)


def main():
    dir_path_extracted_entities = Path("extracted_entities")
    all_files = os.listdir(dir_path_extracted_entities)

    with open(f"different_urls.jsonl", "wt") as f:

        for file_name in all_files:
            with open(dir_path_extracted_entities / str(file_name), "rt") as file:
                wiki_info = json.loads(file.read())
                ner_list = []
                # if wiki_info["wikidata_url"] != wiki_info["wikipedia_url"]:
                #     f.write(json.dumps(wiki_info))
                #     f.write("\n")
                texts = wiki_info['texts']
                texts.append(wiki_info['summary'])
                print(wiki_info['wikipedia_title'])
                for text in texts:
                    sentence = Sentence(text)
                    tagger.predict(sentence)
                    for entity in sentence.get_spans('ner'):
                        if "." in entity.text:
                            x = entity.text.split(".")
                            for m in x:
                                ner_list.append(m)
                        else:
                            ner_list.append(entity.text)

                c = Counter(ner_list)
                print(max(c.items(), key=lambda x: x[1]))

def second():
    dir_path_extracted_entities = Path("extracted_entities")
    all_files = os.listdir(dir_path_extracted_entities)

    with open(f"different_urls.jsonl", "wt") as f:

        for file_name in all_files:
            with open(dir_path_extracted_entities / str(file_name), "rt") as file:
                wiki_info = json.loads(file.read())
                ner_list = []
                # if wiki_info["wikidata_url"] != wiki_info["wikipedia_url"]:
                #     f.write(json.dumps(wiki_info))
                #     f.write("\n")
                texts = wiki_info['texts']
                texts.append(wiki_info['summary'])
                title = wiki_info["wikipedia_title"].split(" ")
                title.append(re.sub("[\(\[].*?[\)\]]", "", wiki_info["wikipedia_title"]).strip())
                print(title)
                print(wiki_info['wikipedia_title'])
                for text in texts:
                    sentence = Sentence(text)
                    tagger.predict(sentence)
                    for entity in sentence.get_spans('ner'):
                        if "." in entity.text:
                            x = entity.text.split(".")
                            for m in x:
                                if m in title:
                                    ner_list.append(m)
                        else:
                            if entity.text in title:
                                ner_list.append(entity.text)

                c = Counter(ner_list)
                # print(max(c.items(), key=lambda x: x[1]))
                print(c.most_common())

if __name__ == "__main__":
    # main()
    second()
