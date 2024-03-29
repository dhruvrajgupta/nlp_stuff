import os
import spacy
from spacy.kb import InMemoryLookupKB
import json
import random
import pickle
import numpy as np
from numpy import dot
from numpy.linalg import norm
from typing import List

import csv
from pathlib import Path

output_dir = Path.cwd() / "my_output"
dis_kb = {}


def get_embeddings_from_string(text: str, nlp):
    # Converting the string to list of sentences of the string
    text = [sent.text for sent in nlp(text).sents]

    long_ass_text_doc = nlp.pipe(text)

    # Getting the number of rows of embeddings
    num_rows = 0
    for sentences_chunks in long_ass_text_doc:
        num_rows += sentences_chunks._.trf_data.tensors[-1].shape[0]

    long_ass_text_doc = nlp.pipe(text)
    long_ass_text_doc_embedding_stack = np.zeros((num_rows, 768))
    row = 0
    for sentences_chunks in long_ass_text_doc:
        # print(sentences_chunks)
        sentences_chunks_enc = sentences_chunks._.trf_data.tensors[-1]  # (x, 768)
        # print(sentences_chunks_enc.shape)
        size = sentences_chunks_enc.shape[0]
        long_ass_text_doc_embedding_stack[row: row + size] = sentences_chunks_enc
        row += size

    return long_ass_text_doc_embedding_stack.mean(axis=0)


def load_entities():
    entities_loc = Path.cwd() / "input" / "entities_expanded.csv"  # distributed alongside this notebook

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
            dis_kb[qid] = {"name": name, "desc": desc}
    return names, descriptions


def create_kb():
    nlp = spacy.load("en_core_web_trf")
    name_dict, desc_dict = load_entities()

    # for QID in name_dict.keys():
    #     print(f"{QID}, name={name_dict[QID]}, desc={desc_dict[QID]}")

    kb = InMemoryLookupKB(vocab=nlp.vocab, entity_vector_length=768)
    for qid, desc in desc_dict.items():
        kb.add_entity(entity=qid, entity_vector=get_embeddings_from_string(desc, nlp),
                      freq=342)  # 342 is an arbitrary value here

    for qid, name in name_dict.items():
        kb.add_alias(alias=name, entities=[qid], probabilities=[1])  # 100% prior probability P(entity|alias)

    qids = name_dict.keys()
    probs = [0.3 for qid in qids]
    kb.add_alias(alias="Emerson", entities=qids, probabilities=probs)  # sum([probs]) should be <= 1 !

    print(f"Entities in the KB: {kb.get_entity_strings()}")
    print(f"Aliases in the KB: {kb.get_alias_strings()}")

    # change the directory and file names to whatever you like
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    kb.to_disk(output_dir / "my_kb")
    nlp.to_disk(output_dir / "my_nlp")


def train_el():
    nlp = spacy.load(output_dir / "my_nlp")

    dataset = []
    json_loc = Path.cwd() / "input" / "emerson_annotated_text.jsonl"
    dataset = []
    with json_loc.open("r", encoding="utf8") as jsonfile:
        for line in jsonfile:
            example = json.loads(line)
            # print(line)
            text = example["text"]
            # print(text)
            if example["answer"] == "accept":
                QID = example["accept"][0]
                offset = (example["spans"][0]["start"], example["spans"][0]["end"])
                entity_label = example["spans"][0]["label"]
                entities = [(offset[0], offset[1], entity_label)]
                links_dict = {QID: 1.0}
            dataset.append((text, {"links": {offset: links_dict}, "entities": entities}))

    gold_ids = []
    for text, annot in dataset:
        for span, links_dict in annot["links"].items():
            for link, value in links_dict.items():
                if value:
                    gold_ids.append(link)

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

    # TRAIN_EXAMPLES = []
    # if "sentencizer" not in nlp.pipe_names:
    #     nlp.add_pipe("sentencizer")
    # sentencizer = nlp.get_pipe("sentencizer")
    # for text, annotation in train_dataset:
    #     example = Example.from_dict(nlp.make_doc(text), annotation)
    #     # Here annotation is the Gold Standard reference
    #     example.reference = sentencizer(example.reference)
    #     TRAIN_EXAMPLES.append(example)
    #
    # entity_linker = nlp.add_pipe("entity_linker", config={"incl_prior": False}, last=True)
    # entity_linker.initialize(get_examples=lambda: TRAIN_EXAMPLES, kb_loader=load_kb(output_dir / "my_kb"))
    #
    # with nlp.select_pipes(enable=["entity_linker"]):  # train only the entity_linker
    #     optimizer = nlp.resume_training()
    #     for itn in range(500):  # 500 iterations takes about a minute to train
    #         random.shuffle(TRAIN_EXAMPLES)
    #         batches = minibatch(TRAIN_EXAMPLES, size=compounding(4.0, 32.0, 1.001))  # increasing batch sizes
    #         losses = {}
    #         for batch in batches:
    #             nlp.update(
    #                 batch,
    #                 drop=0.2,  # prevent overfitting
    #                 losses=losses,
    #                 sgd=optimizer,
    #             )
    #         if itn % 50 == 0:
    #             print(itn, "Losses", losses)  # print the training loss
    # print(itn, "Losses", losses)
    #
    # nlp.to_disk(output_dir / "my_nlp_el")

    with open(output_dir / "test_set.pkl", "wb") as f:
        pickle.dump(test_dataset, f)


if __name__ == "__main__":
    # get_embeddings_from_string("This is a sentence. This is another sentence.", spacy.load("en_core_web_trf"))
    # create_kb()
    # train_el()
    nlp = spacy.load(output_dir / "my_nlp")
    kb = InMemoryLookupKB(vocab=nlp.vocab, entity_vector_length=0)
    kb.from_disk(output_dir / "my_kb")

    # text = "Tennis champion Emerson was expected to win Wimbledon."
    # doc = nlp(text)
    # for ent in doc.ents:
    #     print(ent.text, ent.label_, ent.kb_id_)

    with open(output_dir / "test_set.pkl", "rb") as f:
        test_dataset = pickle.load(f)

    # load_entities()
    # print(dis_kb)
    for text, true_annot in test_dataset:
        print(text)
        print(f"Gold annotation: {true_annot}")
        text_doc = nlp(text)
        text_embed = get_embeddings_from_string(text, nlp)
        for ent in text_doc.ents:
            if ent.text == "Emerson":
                # Get all candidates for Emerson
                candidates = kb.get_alias_candidates("Emerson")
                for candidate in candidates:
                    print(f"{candidate.entity_} - {candidate.alias_}")
                    similarity = np.dot(text_embed, np.array(candidate.entity_vector)) / (
                                norm(text_embed) * norm(np.array(candidate.entity_vector)))
                    print(f"Similarity : {similarity}")
                    print(text)
                    print()
        #         # print(f"Prediction: {ent.text}, {ent.label_}, {ent.kb_id_}")
            print()
