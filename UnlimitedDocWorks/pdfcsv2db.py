import os
import sqlite3
import pandas as pd

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# === CONFIG ===
csv_file = "archive/DataCoSupplyChainDataset.csv"
pdf_folder = "archive"
sqlite_file = "sqlite_store/supplychain.sqlite"
faiss_folder = "vector_store"

# === STEP 1: Load CSV into SQLite and save it ===

df = pd.read_csv(csv_file, encoding="windows-1252")
df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

os.makedirs("sqlite_store", exist_ok=True)
conn = sqlite3.connect(sqlite_file)

# Write DataFrame to SQLite
df.to_sql("shipping_data", conn, if_exists="replace", index=False)

# === STEP 2: Load & embed PDFs into FAISS ===

all_chunks = []
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

for file in os.listdir(pdf_folder):
    if file.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(pdf_folder, file))
        docs = loader.load()
        chunks = text_splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata["source"] = file
        all_chunks.extend(chunks)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MpNet-base-v2")
vector_store = FAISS.from_documents(all_chunks, embeddings)

# Save FAISS vector store
os.makedirs(faiss_folder, exist_ok=True)
vector_store.save_local(faiss_folder)
