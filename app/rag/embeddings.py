from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from app.rag.ingestion import (
    load_documents,
    add_metadata,
    split_documents,
)


load_dotenv()


def create_embedding_model():
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    return embeddings


if __name__ == "__main__":

    print("Loading documents...")

    documents = load_documents()

    print("Adding metadata...")

    documents = add_metadata(documents)

    print("Splitting documents...")

    chunks = split_documents(documents)

    print(f"Total chunks: {len(chunks)}")

    print("Creating embedding model...")

    embeddings = create_embedding_model()

    print("Embedding first chunk...")

    vector = embeddings.embed_query(
        chunks[0].page_content
    )

    print("\nEmbedding created successfully!")
    print("Vector dimension:", len(vector))
    print("First 10 values:", vector[:10])