from config import Config

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_postgres import PGEngine, PGVectorStore

from app.services.embedding_service import embedding_model


# =========================================================
# LOCAL CHROMA
# =========================================================

vector_store = Chroma(
    persist_directory=Config.CHROMA_DB_PATH,
    embedding_function=embedding_model,
)


# =========================================================
# PRODUCTION PGVECTOR
# =========================================================

pg_vector_store = None


def get_pg_vector_store():

    global pg_vector_store

    if pg_vector_store is not None:
        return pg_vector_store


    connection_string = (
        Config.SQLALCHEMY_DATABASE_URI
        .replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )
    )


    pg_engine = PGEngine.from_connection_string(
        url=connection_string
    )


    pg_vector_store = PGVectorStore.create_sync(
        engine=pg_engine,
        table_name="vellichor_vectors",
        embedding_service=embedding_model,
    )


    return pg_vector_store


# =========================================================
# STORE CHUNKS
# =========================================================

def store_chunks(chunks, pdf_id, filename):

    documents = []


    for index, chunk in enumerate(chunks):

        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "pdf_id": pdf_id,
                    "filename": filename,
                    "chunk_index": index
                }
            )
        )


    # -----------------------------------------------------
    # LOCAL → CHROMA
    # -----------------------------------------------------

    if Config.ENVIRONMENT == "development":

        vector_store.add_documents(
            documents
        )

        return len(documents)


    # -----------------------------------------------------
    # PRODUCTION → PGVECTOR
    # -----------------------------------------------------

    production_store = get_pg_vector_store()

    production_store.add_documents(
        documents
    )

    return len(documents)


# =========================================================
# RETRIEVE CHUNKS
# =========================================================

def retrieve_chunks(query, pdf_id):

    # -----------------------------------------------------
    # LOCAL → CHROMA
    # -----------------------------------------------------

    if Config.ENVIRONMENT == "development":

        results = vector_store.similarity_search(
            query=query,
            k=4,
            filter={
                "pdf_id": pdf_id
            }
        )

        return results


    # -----------------------------------------------------
    # PRODUCTION → PGVECTOR
    # -----------------------------------------------------

    production_store = get_pg_vector_store()

    results = production_store.similarity_search(
        query=query,
        k=4,
        filter={
            "pdf_id": {
                "$eq": pdf_id
            }
        }
    )

    return results


# =========================================================
# DELETE PDF EMBEDDINGS
# =========================================================

def delete_pdf_embeddings(pdf_id):

    # -----------------------------------------------------
    # LOCAL → CHROMA
    # -----------------------------------------------------

    if Config.ENVIRONMENT == "development":

        vector_store.delete(
            where={
                "pdf_id": pdf_id
            }
        )

        return


    # -----------------------------------------------------
    # PRODUCTION → PGVECTOR
    # -----------------------------------------------------

    production_store = get_pg_vector_store()

    production_store.delete(
        filter={
            "pdf_id": {
                "$eq": pdf_id
            }
        }
    )