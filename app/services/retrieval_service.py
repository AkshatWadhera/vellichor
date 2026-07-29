from config import Config
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.services.embedding_service import embedding_model



vector_store = Chroma(
    persist_directory=Config.CHROMA_DB_PATH,
    embedding_function=embedding_model,
)


def store_chunks(chunks, pdf_id, filename):
    documents = []

    for index, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "pdf_id":pdf_id,
                    "filename":filename,
                    "chunk_index":index
                }
            )
        )
        

    vector_store.add_documents(documents)

    return len(documents)