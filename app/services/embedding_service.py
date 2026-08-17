import os

import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from huggingface_hub import InferenceClient

from config import Config


# =========================================================
# PRODUCTION → HUGGING FACE API EMBEDDINGS
# =========================================================

class HuggingFaceAPIEmbeddings(Embeddings):

    def __init__(self):

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=os.getenv("HF_TOKEN")
        )

        self.model = Config.EMBEDDING_MODEL


    def embed_documents(self, texts):

        result = self.client.feature_extraction(
            texts,
            model=self.model
        )

        return result.tolist()


    def embed_query(self, text):

        result = self.client.feature_extraction(
            text,
            model=self.model
        )

        return result.tolist()


# =========================================================
# EMBEDDING MODEL SELECTION
# =========================================================

def create_embedding_model():

    # Production → Hugging Face API

    if Config.ENVIRONMENT == "production":

        return HuggingFaceAPIEmbeddings()


    # Development → Local Hugging Face model

    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL
    )


embedding_model = create_embedding_model()


# =========================================================
# EXTRACTING TEXT
# =========================================================

def extract_text(pdf_path):

    with fitz.open(pdf_path) as document:

        if document.is_encrypted:
            raise ValueError("PASSWORD_PROTECTED")

        text = ""

        for page in document:
            text += page.get_text()

    return text


# =========================================================
# CHUNKING TEXT
# =========================================================

def chunk_text(text):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            " ",
            ""
        ]
    )

    chunks = text_splitter.split_text(text)

    return chunks