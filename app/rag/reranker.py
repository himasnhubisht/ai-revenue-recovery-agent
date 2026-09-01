from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def rerank(query, documents, top_k=3):

    scored_documents = []

    for document in documents:

        prompt = f"""
You are a retrieval relevance grader.

Query:
{query}

Document:
{document.page_content}

Give a relevance score from 0 to 10.

10 = directly answers the query
7-9 = highly relevant
4-6 = somewhat relevant
1-3 = weakly relevant
0 = irrelevant

Return only the number.
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        score = float(response.output_text.strip())

        scored_documents.append(
            (document, score)
        )

    scored_documents.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return scored_documents[:top_k]