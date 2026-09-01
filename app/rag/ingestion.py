from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_PATH = Path("data")


def load_documents():
    loader = DirectoryLoader(
        str(DATA_PATH),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    documents = loader.load()

    print(f"Loaded {len(documents)} documents.")

    return documents


def add_metadata(documents):
    for document in documents:

        source = Path(document.metadata["source"])

        parts = source.parts

        # Example:
        # data / merchants / fashionkart / retry_policy.md

        if "merchants" in parts:
            merchant_index = parts.index("merchants")

            merchant_id = parts[merchant_index + 1]

            document_type = source.stem

            document.metadata["merchant_id"] = merchant_id
            document.metadata["document_type"] = document_type

        else:
            # Global knowledge
            document.metadata["merchant_id"] = "global"
            document.metadata["document_type"] = source.stem

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    return chunks

if __name__ == "__main__":

    print("Starting ingestion...")

    documents = load_documents()

    documents = add_metadata(documents)

    chunks = split_documents(documents)

    print("\nExample chunks:\n")

    for chunk in chunks[:5]:
        print("--------------------------------")
        print(chunk.page_content[:200])
        print("\nMetadata:")
        print(chunk.metadata)