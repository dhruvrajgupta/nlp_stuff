import os
import spacy
from spacy.kb import InMemoryLookupKB
import json
from collections import Counter
import random
from spacy.util import minibatch, compounding
from spacy.training import Example


import csv
from pathlib import Path

output_dir = Path.cwd() / "my_output"

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

def ckb(vocab):
    kb = InMemoryLookupKB(vocab=vocab, entity_vector_length=1)
    kb.from_disk(output_dir / "my_kb")
    return kb

def create_kb():
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
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    kb.to_disk(output_dir / "my_kb")
    nlp.to_disk(output_dir / "my_nlp")

def train_el():
    nlp = spacy.load(output_dir / "my_nlp")

    dataset = []
    json_loc = Path.cwd() / "input" / "emerson_annotated_text.jsonl"
    with json_loc.open("r", encoding="utf8") as jsonfile:
        for line in jsonfile:
            example = json.loads(line)
            text = example["text"]
            if example["answer"] == "accept":
                QID = example["accept"][0]
                offset = (example["spans"][0]["start"], example["spans"][0]["end"])
                links_dict = {QID: 1.0}
            dataset.append((text, {"links": {offset: links_dict}}))

    print(dataset[0])

    gold_ids = []
    for text, annot in dataset:
        for span, links_dict in annot["links"].items():
            for link, value in links_dict.items():
                if value:
                    gold_ids.append(link)

    print(Counter(gold_ids))

    train_dataset = []
    test_dataset = []
    for QID in ['Q312545', 'Q48226', 'Q215952']:
        indices = [i for i, j in enumerate(gold_ids) if j == QID]
        train_dataset.extend(dataset[index] for index in indices[0:8])  # first 8 in training
        test_dataset.extend(dataset[index] for index in indices[8:10])  # last 2 in test
        # print("*"*50)
        # print(indices)
        # print("*"*50)
        # print(train_dataset)
        # print("*"*50)
        # print(test_dataset)

    random.shuffle(train_dataset)
    random.shuffle(test_dataset)

    TRAIN_DOCS = []
    for text, annotation in train_dataset:
        doc = nlp(text)     # to make this more efficient, you can use nlp.pipe() just once for all the texts
        example = Example.from_dict(doc, annotation)
        # TRAIN_DOCS.append((doc, annotation))
        TRAIN_DOCS.append(example)

    # entity_linker = nlp.create_pipe("entity_linker", config={"incl_prior": False})
    # entity_linker.set_kb(ckb)
    entity_linker = nlp.add_pipe("entity_linker", config={"incl_prior": False}, last=True)
    entity_linker.set_kb(ckb)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    with nlp.disable_pipes(*other_pipes):   # train only the entity_linker
        optimizer = nlp.create_optimizer()
        for itn in range(500):   # 500 iterations takes about a minute to train
            random.shuffle(TRAIN_DOCS)
            batches = minibatch(TRAIN_DOCS, size=compounding(4.0, 32.0, 1.001))  # increasing batch sizes
            losses = {}
            for batch in batches:
                nlp.update(
                    batch,
                    drop=0.2,      # prevent overfitting
                    losses=losses,
                    sgd=optimizer,
                )
            if itn % 50 == 0:
                print(itn, "Losses", losses)   # print the training loss
    print(itn, "Losses", losses)

    nlp.to_disk(output_dir / "my_nlp_el")


if __name__ == "__main__":
    create_kb()
    train_el()