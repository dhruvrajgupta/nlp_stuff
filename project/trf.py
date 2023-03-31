import spacy
from pathlib import Path
import numpy as np

nlp = spacy.load("en_core_web_trf")
inp_dir = Path.cwd() / "input"


def get_embeddings_from_string():
    with open(inp_dir / 'in.txt') as f:
        lines = f.readlines()
    long_ass_text_doc = nlp.pipe(lines)

    # Getting the number of rows of embeddings
    num_rows = 0
    for sentences_chunks in long_ass_text_doc:
        num_rows += sentences_chunks._.trf_data.tensors[-1].shape[0]

    long_ass_text_doc = nlp.pipe(lines)
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


# get_embeddings_from_string()
def emb_mean_try():
    import numpy as np
    vector_stack = []
    vector_stack.append(np.array([[1, 2], [7, 5]]))
    vector_stack.append(np.array([[11, 12]]))
    print(vector_stack)

    # # Getting number of rows
    rows = 0
    for x in vector_stack:
        rows += x.shape[0]
    print(rows)

    z = np.zeros((rows, 2))
    print(z)
    c = 0
    for x in vector_stack:
        size = x.shape[0]
        z[c: c + size] = x
        c += size
        print(z)


def similar_words_embedding():
    fin_text = get_embeddings_from_string()
    keywords_footbaler = ['soccer', 'offside', 'goal', 'player']


def main():
    similar_words_embedding()


if __name__ == "__main__":
    main()
