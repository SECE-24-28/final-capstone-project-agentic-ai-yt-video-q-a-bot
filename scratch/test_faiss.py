import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Create a small FAISS index
texts = ["This is chunk 1 [0:10]", "This is chunk 2 [0:20]", "This is chunk 3 [0:30]"]
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_texts(texts, embeddings)

print("docstore keys:", db.docstore._dict.keys())
print("docstore values:", [d.page_content for d in db.docstore._dict.values()])
print("index_to_docstore_id type:", type(db.index_to_docstore_id))
print("index_to_docstore_id:", db.index_to_docstore_id)
# Retrieve docs in insertion order using index_to_docstore_id mapping
ordered_docs = [db.docstore.search(db.index_to_docstore_id[i]) for i in range(len(db.index_to_docstore_id))]
print("ordered_docs:", [d.page_content for d in ordered_docs])
