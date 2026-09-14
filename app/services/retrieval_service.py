import time

from flask import current_app
from config import Config

from langchain_core.documents import Document
from langchain_postgres import PGEngine, PGVectorStore

from app.services.embedding_service import embedding_model


# =========================================================
# LOCAL CHROMA
# =========================================================

vector_store = None

if Config.ENVIRONMENT == "development":

    from langchain_chroma import Chroma

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


    try:

        connection_string = (
            Config.SQLALCHEMY_DATABASE_URI
            .replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )
        )


        print(
            "[06B] Initializing production PGVector store",
            flush=True
        )

        pg_init_start = time.perf_counter()

        engine_start = time.perf_counter()

        pg_engine = PGEngine.from_connection_string(
            url=connection_string
        )

        engine_time = time.perf_counter() - engine_start

        print(
            f"[06B] PGEngine created in {engine_time:.3f}s",
            flush=True
        )

        vector_store_start = time.perf_counter()

        pg_vector_store = PGVectorStore.create_sync(
            engine=pg_engine,
            table_name="vellichor_vectors",
            embedding_service=embedding_model,
        )

        vector_store_time = time.perf_counter() - vector_store_start

        print(
            f"[06B] PGVectorStore created in {vector_store_time:.3f}s",
            flush=True
        )

        pg_total_time = time.perf_counter() - pg_init_start

        print(
            f"[06B] PGVector store initialization completed in {pg_total_time:.3f}s",
            flush=True
        )


        return pg_vector_store


    except Exception:

        current_app.logger.exception(
            "Failed to initialize production PGVector store"
        )

        raise


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

        try:

            current_app.logger.info(
                "Storing %s document chunks in local Chroma",
                len(documents)
            )


            vector_store.add_documents(
                documents
            )


            current_app.logger.info(
                "Local Chroma storage completed successfully"
            )


            return len(documents)


        except Exception:

            current_app.logger.exception(
                "Failed to store document chunks in local Chroma"
            )

            raise


    # -----------------------------------------------------
    # PRODUCTION → PGVECTOR
    # -----------------------------------------------------

    try:

        current_app.logger.info(
            "Storing %s document chunks in production PGVector",
            len(documents)
        )


        print(
            "[06C] Getting production PGVector store",
            flush=True
        )

        store_init_start = time.perf_counter()

        production_store = get_pg_vector_store()

        store_init_time = time.perf_counter() - store_init_start

        print(
            f"[06C] PGVector store ready in {store_init_time:.3f}s",
            flush=True
        )

        print(
            f"[06C] Starting PGVector add_documents | Documents: {len(documents)}",
            flush=True
        )

        add_documents_start = time.perf_counter()

        production_store.add_documents(
            documents
        )

        add_documents_time = time.perf_counter() - add_documents_start

        print(
            f"[06C] PGVector add_documents completed in {add_documents_time:.3f}s",
            flush=True
        )

        current_app.logger.info(
            "Production PGVector storage completed successfully"
        )


        return len(documents)


    except Exception:

        current_app.logger.exception(
            "Failed to store document chunks in production PGVector"
        )

        raise


# =========================================================
# RETRIEVE CHUNKS
# =========================================================

def retrieve_chunks(query, pdf_id):

    # -----------------------------------------------------
    # LOCAL → CHROMA
    # -----------------------------------------------------

    if Config.ENVIRONMENT == "development":

        try:

            current_app.logger.info(
                "Retrieving document chunks from local Chroma"
            )


            results = vector_store.similarity_search(
                query=query,
                k=4,
                filter={
                    "pdf_id": pdf_id
                }
            )


            current_app.logger.info(
                "Local Chroma retrieval completed: %s results",
                len(results)
            )


            return results


        except Exception:

            current_app.logger.exception(
                "Failed to retrieve chunks from local Chroma"
            )

            raise


    # -----------------------------------------------------
    # PRODUCTION → PGVECTOR
    # -----------------------------------------------------

    try:

        current_app.logger.info(
            "Retrieving document chunks from production PGVector"
        )


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


        current_app.logger.info(
            "Production PGVector retrieval completed: %s results",
            len(results)
        )


        return results


    except Exception:

        current_app.logger.exception(
            "Failed to retrieve chunks from production PGVector"
        )

        raise


# =========================================================
# DELETE PDF EMBEDDINGS
# =========================================================

def delete_pdf_embeddings(pdf_id):

    # -----------------------------------------------------
    # LOCAL → CHROMA
    # -----------------------------------------------------

    if Config.ENVIRONMENT == "development":

        try:

            current_app.logger.info(
                "Deleting PDF embeddings from local Chroma"
            )


            vector_store.delete(
                where={
                    "pdf_id": pdf_id
                }
            )


            current_app.logger.info(
                "Local Chroma embeddings deleted successfully"
            )


            return


        except Exception:

            current_app.logger.exception(
                "Failed to delete PDF embeddings from local Chroma"
            )

            raise


    # -----------------------------------------------------
    # PRODUCTION → PGVECTOR
    # -----------------------------------------------------

    try:

        print(
            "DELETE TIMING: Starting PGVectorStore get/initialization",
            flush=True
        )

        init_start = time.perf_counter()

        production_store = get_pg_vector_store()

        init_time = time.perf_counter() - init_start

        print(
            f"DELETE TIMING: PGVectorStore get/initialization completed in {init_time:.3f}s",
            flush=True
        )

        print(
            "DELETE TIMING: Starting PGVector embedding delete operation",
            flush=True
        )

        delete_start = time.perf_counter()

        production_store.delete(
            filter={
                "pdf_id": {
                    "$eq": pdf_id
                }
            }
        )

        delete_time = time.perf_counter() - delete_start

        print(
            f"DELETE TIMING: PGVector embedding delete operation completed in {delete_time:.3f}s",
            flush=True
        )

        print(
            "Production PGVector embeddings deleted successfully",
            flush=True
        )

    except Exception:

        current_app.logger.exception(
            "Failed to delete PDF embeddings from production PGVector"
        )

        raise