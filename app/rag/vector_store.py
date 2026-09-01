from pathlib import Path

from langchain_chroma import Chroma

from app.rag.ingestion import (
    load_documents,
    add_metadata,
    split_documents,
)

from app.rag.embeddings import create_embedding_model


CHROMA_PATH = Path("chroma_db")
COLLECTION_NAME = "payment_knowledge"


def create_vector_store():

    documents = load_documents()
    documents = add_metadata(documents)
    chunks = split_documents(documents)

    embeddings = create_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_PATH),
    )

    return vector_store


if __name__ == "__main__":
    create_vector_store()