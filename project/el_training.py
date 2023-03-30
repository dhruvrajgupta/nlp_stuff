import os
import spacy
from spacy.kb import InMemoryLookupKB
import json
import random
import pickle

import csv
from pathlib import Path

output_dir = Path.cwd() / "my_output"
dis_kb = {}
nlp = spacy.load("en_core_web_trf")


def get_embeddings_from_string(str: String):
    print(str)
    document = nlp("This is a sentence. This is another sentence.")
    sentences = [sentence.text for sentence in document.sents]
    desc_doc = nlp.pipe(sentences)

    desc_embeddings_stack = []
    desc_avg_enc = None
    for sentence in desc_doc:
        # print(doc)
        desc_enc = doc._.trf_data.tensors[-1]  # (1, 768)
        desc_embeddings_stack.append(desc_enc)
        desc_avg_enc = get_avg_vectors(desc_embeddings_stack)
    # print(vector_stack.shape)
    # vector_stack = []
    # vector_stack.append(np.array([[1,2]]))
    # vector_stack.append(np.array([[7,5]]))
    sum = 0
    count = 0
    for embedding in vector_stack:
        # print(embedding[0])
        sum += embedding[0]
        count += 1

    return sum / count


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
            dis_kb[qid] = {"name": name, "desc": desc}
    return names, descriptions


def create_kb():
    nlp = spacy.load("en_core_web_trf")
    # text = "Tennis champion Emerson was expected to win Wimbledon."
    # doc = nlp(text)
    name_dict, desc_dict = load_entities()

    # for QID in name_dict.keys():
    #     print(f"{QID}, name={name_dict[QID]}, desc={desc_dict[QID]}")

    kb = InMemoryLookupKB(vocab=nlp.vocab, entity_vector_length=768)
    for qid, desc in desc_dict.items():
        # Desc is very short,  long -> use sentencizer and average the tokens
        doc = nlp(desc)
        sentences = [sent.text for sent in doc.sents]
        desc_doc = nlp.pipe(sentences)
        desc_embeddings_stack = []
        desc_avg_enc = None
        for doc in desc_doc:
            # print(doc)
            desc_enc = doc._.trf_data.tensors[-1]  # (1, 768)
            desc_embeddings_stack.append(desc_enc)
            desc_avg_enc = get_avg_vectors(desc_embeddings_stack)

        kb.add_entity(entity=qid, entity_vector=desc_avg_enc, freq=342)  # 342 is an arbitrary value here

    for qid, name in name_dict.items():
        # print(qid)
        # print(name)
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
    # get_avg_vectors()
    create_kb()
    train_el()
    nlp = spacy.load(output_dir / "my_nlp")
    kb = InMemoryLookupKB(vocab=nlp.vocab, entity_vector_length=0)
    kb.from_disk(output_dir / "my_kb")
    # text = "Tennis champion Emerson was expected to win Wimbledon."
    # doc = nlp(text)
    # for ent in doc.ents:
    #     print(ent.text, ent.label_, ent.kb_id_)

    with open(output_dir / "test_set.pkl", "rb") as f:
        test_dataset = pickle.load(f)

    print(dis_kb)
    for text, true_annot in test_dataset:
        print(text)
        print(f"Gold annotation: {true_annot}")
        doc = nlp(text)  # to make this more efficient, you can use nlp.pipe() just once for all the texts
        text_vector = doc.vector
        print(text_vector)
        # for ent in doc.ents:
        #     if ent.text == "Emerson":
        #         # Get all candidates for Emerson
        #         candidates = kb.get_alias_candidates("Emerson")
        #         for candidate in candidates:
        #             print(f"{candidate.entity_} - {dis_kb[candidate.entity_]}")
        #         # print(f"Prediction: {ent.text}, {ent.label_}, {ent.kb_id_}")
        # print()
