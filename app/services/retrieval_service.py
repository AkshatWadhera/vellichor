import time
import json
import uuid

from flask import current_app
from config import Config

from langchain_core.documents import Document
from langchain_postgres import PGEngine, PGVectorStore
from sqlalchemy import text

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

        # -----------------------------------------------------
        # DIAGNOSTIC: inspect documents before PGVector
        # -----------------------------------------------------

        print(
            f"[06C-1] Documents prepared: {len(documents)}",
            flush=True
        )

        if documents:
            print(
                f"[06C-1] First document content length: "
                f"{len(documents[0].page_content)} characters",
                flush=True
            )

            print(
                f"[06C-1] First document metadata: "
                f"{documents[0].metadata}",
                flush=True
            )

        # -----------------------------------------------------
        # PRODUCTION INGESTION → BATCHED PGVECTOR INSERT
        # -----------------------------------------------------

        add_documents_start = time.perf_counter()

        print(
            "[06C-2] Starting batched PGVector ingestion",
            flush=True
        )

        try:

            texts = [document.page_content for document in documents]
            metadatas = [document.metadata for document in documents]

            # Generate embeddings once, outside the database operation.
            embedding_start = time.perf_counter()

            embeddings = embedding_model.embed_documents(texts)

            embedding_time = time.perf_counter() - embedding_start

            print(
                f"[06C-2A] Embeddings generated in "
                f"{embedding_time:.3f}s | Embeddings: {len(embeddings)}",
                flush=True
            )

            # PGVectorStore generates UUIDs when Document.id is not set.
            ids = [uuid.uuid4() for _ in documents]

            rows = [
                {
                    "langchain_id": document_id,
                    "content": content,
                    "embedding": str(
                        [float(dimension) for dimension in embedding]
                    ),
                    "extra": json.dumps(metadata),
                }
                for document_id, content, embedding, metadata
                in zip(ids, texts, embeddings, metadatas)
            ]

            insert_query = text("""
                INSERT INTO public.vellichor_vectors
                    (langchain_id, content, embedding, langchain_metadata)
                VALUES
                    (:langchain_id, :content, :embedding, :extra)
                ON CONFLICT (langchain_id)
                DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    langchain_metadata = EXCLUDED.langchain_metadata
            """)

            # Reuse the async engine/pool already created by PGVectorStore.
            async_store = production_store._PGVectorStore__vs

            print(
                f"[06C-2B] Starting single-transaction batch insert | "
                f"Rows: {len(rows)}",
                flush=True
            )

            db_start = time.perf_counter()

            async def batch_insert():
                async with async_store.engine.connect() as conn:
                    await conn.execute(insert_query, rows)
                    await conn.commit()

            production_store._engine._run_as_sync(
                batch_insert()
            )

            db_time = time.perf_counter() - db_start

            print(
                f"[06C-2C] Batch PGVector insert + commit completed in "
                f"{db_time:.3f}s | Rows: {len(rows)}",
                flush=True
            )

            total_vector_time = (
                time.perf_counter() - add_documents_start
            )

            print(
                f"[06C-3] Batched PGVector ingestion completed in "
                f"{total_vector_time:.3f}s",
                flush=True
            )

        except Exception as error:

            add_documents_time = time.perf_counter() - add_documents_start

            print(
                f"[06C-ERROR] Batched PGVector ingestion failed after "
                f"{add_documents_time:.3f}s",
                flush=True
            )

            print(
                f"[06C-ERROR] Exception type: {type(error).__name__}",
                flush=True
            )

            print(
                f"[06C-ERROR] Exception: {error}",
                flush=True
            )

            raise

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