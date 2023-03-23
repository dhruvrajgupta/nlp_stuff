import os
import spacy
from spacy.kb import InMemoryLookupKB

import csv
from pathlib import Path

def load_entities():
    entities_loc = Path.cwd() / "input" / "entities.csv"  # distributed alongside this notebook

    names = dict()
    descriptions = dict()
    with entities_loc.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=",")
        for row in csvreader:
            qid = row[0]
            name = row[1]
            desc = row[2]
            names[qid] = name
            descriptions[qid] = desc
    return names, descriptions


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_lg")
    text = "Tennis champion Emerson was expected to win Wimbledon."
    doc = nlp(text)
    name_dict, desc_dict = load_entities()

    kb = InMemoryLookupKB(vocab=nlp.vocab, entity_vector_length=300)
    for qid, desc in desc_dict.items():
        desc_doc = nlp(desc)
        desc_enc = desc_doc.vector
        kb.add_entity(entity=qid, entity_vector=desc_enc, freq=342)   # 342 is an arbitrary value here

    for qid, name in name_dict.items():
        kb.add_alias(alias=name, entities=[qid], probabilities=[1])   # 100% prior probability P(entity|alias)

    qids = name_dict.keys()
    probs = [0.3 for qid in qids]
    kb.add_alias(alias="Emerson", entities=qids, probabilities=probs)  # sum([probs]) should be <= 1 !

    print(f"Entities in the KB: {kb.get_entity_strings()}")
    print(f"Aliases in the KB: {kb.get_alias_strings()}")
    print(f"Candidates for 'Roy Stanley Emerson': {[c.entity_ for c in kb.get_candidates(nlp('Roy Stanley Emerson'))]}")
    print(f"Candidates for 'Emerson': {[c.entity_ for c in kb.get_candidates(nlp('Emerson'))]}")
    print(f"Candidates for 'Sofie': {[c.entity_ for c in kb.get_candidates(nlp('Sofie'))]}")

    # change the directory and file names to whatever you like
    output_dir = Path.cwd() / "my_output"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    kb.to_disk(output_dir / "my_kb")
    nlp.to_disk(output_dir / "my_nlp")