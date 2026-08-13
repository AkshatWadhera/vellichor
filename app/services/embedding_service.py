import fitz
from flask import current_app
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from config import Config


embedding_model = HuggingFaceEmbeddings(
    model_name= Config.EMBEDDING_MODEL
)


#Extracting Text
def extract_text(pdf_path):

    with fitz.open(pdf_path) as document:

        text = ""

        for page in document:
            text += page.get_text()

    return text

#Chunking Text
def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        separators = [
            "\n\n",
            "\n",
            " ",
            ""
        ]
    )

    chunks = text_splitter.split_text(text)

    return chunks

