# import spacy
# from thinc.api import set_gpu_allocator, require_gpu
#
# # Use the GPU, with memory allocations directed via PyTorch.
# # This prevents out-of-memory errors that would otherwise occur from competing
# # memory pools.
# # set_gpu_allocator("pytorch")
# # require_gpu(0)
#
# nlp = spacy.load("en_core_web_trf")
# # for doc in nlp.pipe(["some text", "some other text"]):
# #     print(doc)
# #     tokvecs = doc._.trf_data.tensors[-1]
#
# text = nlp.pipe(["Australian tennis player"])
# for doc in text:
#     print(doc)
#     tokvecs = doc._.trf_data.tensors[-1]
#     print(tokvecs.shape)


# from spacy.pipeline import Sentencizer
import spacy

nlp = spacy.load("en_core_web_trf")
# sentencizer = Sentencizer()
doc = nlp("This is a sentence. This is another sentence.")
x = [sent for sent in doc.sents]
print(x)
