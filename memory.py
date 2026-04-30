import os
import logging
import warnings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "TradingAgents", ".env"))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"trust_remote_code": False},
    show_progress=False,
)

documents = []

def save_user_preference(text):
    global documents
    documents.append(Document(page_content=text))

def build_vector_db():
    if not documents:
        return None
    return FAISS.from_documents(documents, embeddings)

def retrieve_memory(vector_db, query):
    if vector_db is None:
        return []
    docs = vector_db.similarity_search(query)
    return [doc.page_content for doc in docs]
