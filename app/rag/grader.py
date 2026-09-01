import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.documents import Document

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def grade_document(query: str, document) -> bool:

    prompt = f"""
You are a relevance grader for a payment recovery system.

Query:
{query}

Document:
{document.page_content}

Determine whether this document contains information
that is useful for answering the query.

Return ONLY:
YES
or
NO
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    result = response.output_text.strip().upper()

    return result == "YES"

if __name__ == "__main__":

  

    test_document = Document(
        page_content="""
        TechStore allows a maximum of 2 automatic retries
        for insufficient funds.
        Wait at least 30 minutes between retries.
        """,
        metadata={
            "merchant_id": "techstore"
        }
    )

    query = "How many times can TechStore retry an insufficient funds payment?"

    result = grade_document(
        query,
        test_document
    )

    print("Relevant:", result)    