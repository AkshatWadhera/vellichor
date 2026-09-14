from flask import current_app
import os
import time

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

        hf_token = os.getenv("HF_TOKEN")

        if not hf_token:

            raise RuntimeError(
                "HF_TOKEN is not configured"
            )


        try:

            self.client = InferenceClient(
                provider="hf-inference",
                api_key=hf_token
            )

            self.model = Config.EMBEDDING_MODEL

        except Exception:

            current_app.logger.exception(
                "Failed to initialize Hugging Face embedding client"
            )

            raise


    def embed_documents(self, texts):

        try:

            current_app.logger.info(
                "[06A] Starting Hugging Face embedding request | Chunks: %s | Model: %s",
                len(texts),
                self.model
            )

            embedding_start = time.perf_counter()

            result = self.client.feature_extraction(
                texts,
                model=self.model
            )

            api_time = time.perf_counter() - embedding_start

            current_app.logger.info(
                "[06A] Hugging Face embedding request completed in %.3fs",
                api_time
            )

            conversion_start = time.perf_counter()

            embeddings = result.tolist()

            conversion_time = time.perf_counter() - conversion_start

            current_app.logger.info(
                "[06A] Embedding result conversion completed in %.3fs",
                conversion_time
            )

            current_app.logger.info(
                "[06A] Document embeddings generated successfully | Embeddings: %s",
                len(embeddings)
            )

            return embeddings

        except Exception:

            current_app.logger.exception(
                "Hugging Face document embedding request failed"
            )

            raise


    def embed_query(self, text):

        try:

            current_app.logger.info(
                "Generating embedding for user query"
            )

            result = self.client.feature_extraction(
                text,
                model=self.model
            )

            embedding = result.tolist()

            current_app.logger.info(
                "User query embedding generated successfully"
            )

            return embedding

        except Exception:

            current_app.logger.exception(
                "Hugging Face query embedding request failed"
            )

            raise


# =========================================================
# EMBEDDING MODEL SELECTION
# =========================================================

def create_embedding_model():

    # -----------------------------------------------------
    # PRODUCTION → HUGGING FACE API
    # -----------------------------------------------------

    if Config.ENVIRONMENT == "production":

        return HuggingFaceAPIEmbeddings()


    # -----------------------------------------------------
    # DEVELOPMENT → LOCAL HUGGING FACE MODEL
    # -----------------------------------------------------

    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL
    )


embedding_model = create_embedding_model()


# =========================================================
# EXTRACTING TEXT
# =========================================================

def extract_text(pdf_path):

    try:

        with fitz.open(pdf_path) as document:

            if document.is_encrypted:

                raise ValueError(
                    "PASSWORD_PROTECTED"
                )


            text = ""

            for page in document:

                text += page.get_text()


        current_app.logger.info(
            "PDF text extraction completed"
        )

        return text


    except ValueError:

        raise


    except Exception:

        current_app.logger.exception(
            "PDF text extraction failed"
        )

        raise


# =========================================================
# CHUNKING TEXT
# =========================================================

def chunk_text(text):

    try:

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

        current_app.logger.info(
            "PDF text chunking completed: %s chunks",
            len(chunks)
        )

        return chunks


    except Exception:
        
        current_app.logger.exception(
            "PDF text chunking failed"
        )

        raise