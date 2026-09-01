from pathlib import Path

from app.rag.reranker import rerank
from app.rag.query_transform import (
    rewrite_query,
    generate_multi_queries
)

from langchain_chroma import Chroma
from app.rag.embeddings import create_embedding_model
from app.rag.grader import grade_document

CHROMA_PATH = Path("chroma_db")
COLLECTION_NAME = "payment_knowledge"


def get_vector_store():

    embeddings = create_embedding_model()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PATH),
    )

    return vector_store


def retrieve(query: str, merchant_id: str, k: int = 3):

    vector_store = get_vector_store()

    # -----------------------------------
    # 1. QUERY TRANSFORMATION
    # -----------------------------------

    rewritten_query = rewrite_query(
        query,
        merchant_id=merchant_id
    )

    multi_queries = generate_multi_queries(
        query,
        num_queries=3,
        merchant_id=merchant_id
    )

    # Combine original + rewritten + generated queries
    queries = [query]

    queries.append(rewritten_query)

    queries.extend(multi_queries)

    # Remove duplicates
    queries = list(dict.fromkeys(queries))


    # -----------------------------------
    # 2. RETRIEVE CANDIDATES
    # -----------------------------------

    all_candidates = []

    for search_query in queries:

        candidates = vector_store.similarity_search(
            search_query,
            k=10,
            filter={
                "$or": [
                    {"merchant_id": merchant_id},
                    {"merchant_id": "global"}
                ]
            }
        )

        all_candidates.extend(candidates)


    # -----------------------------------
    # 3. REMOVE DUPLICATE DOCUMENTS
    # -----------------------------------

    unique_candidates = {}

    for document in all_candidates:

        source = document.metadata.get("source")

        if source not in unique_candidates:
            unique_candidates[source] = document


    candidates = list(unique_candidates.values())


    # -----------------------------------
    # 4. RERANK
    # -----------------------------------

    results = rerank(
        query,
        candidates,
        top_k=k
    )


    graded_results = []

    for document, score in results:

        is_relevant = grade_document(
            query,
            document
        )

        if is_relevant:
            graded_results.append(
                (document, score)
            )

    return graded_results


# -----------------------------------
# TEST
# -----------------------------------

if __name__ == "__main__":

    results = retrieve(
        "What should we do when a payment fails because of insufficient funds?",
        "techstore"
    )

    for document, score in results:

        print("Score:", score)

        print(document.page_content)

        print(document.metadata)

        print("---")