import os
from typing import List, Optional, Union
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Default LLM model for query transformation
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_client() -> OpenAI:
    """Initialize and return an OpenAI client instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


def rewrite_query(
    query: str,
    merchant_id: Optional[str] = None,
    context: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    client: Optional[OpenAI] = None,
) -> str:
    """
    Rewrite a raw, ambiguous, or conversational user query into a concise,
    information-dense search query optimized for vector retrieval in payment recovery.

    Args:
        query: The raw input query or payment issue description.
        merchant_id: Optional merchant identifier for context-aware rewriting.
        context: Optional additional context (e.g. error code, transaction status).
        model: OpenAI model to use for query rewriting.
        client: Optional OpenAI client instance.

    Returns:
        A rewritten, retrieval-optimized query string.
    """
    client = client or get_openai_client()

    merchant_context = f"Merchant ID: {merchant_id}\n" if merchant_id else ""
    additional_context = f"Additional Context: {context}\n" if context else ""

    prompt = f"""You are an expert AI assistant specializing in revenue recovery and payment failure resolution.
Your task is to rewrite the input query into an optimized, keyword-rich search query suitable for semantic vector retrieval.

Domain focus: Payment error codes, retry policies, customer communication guidelines, escalation rules, and recovery workflows.

{merchant_context}{additional_context}Original Query:
{query}

Instructions:
1. Strip conversational filler and retain core semantic keywords.
2. Clarify implicit terms regarding payment failures, retry limits, grace periods, or notification channels.
3. Return ONLY the rewritten query text without quotes, explanation, or prefixes.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a specialized query transformation engine for payment recovery RAG."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        rewritten = response.choices[0].message.content.strip()
        return rewritten if rewritten else query
    except Exception as e:
        print(f"[QueryTransform] Warning: Error during query rewrite: {e}. Falling back to original query.")
        return query


def generate_multi_queries(
    query: str,
    num_queries: int = 3,
    merchant_id: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    client: Optional[OpenAI] = None,
) -> List[str]:
    """
    Generate multiple distinct search query perspectives/variations to overcome
    semantic search limitations and improve document recall.

    Args:
        query: The original user question or issue.
        num_queries: Number of distinct search query variations to generate.
        merchant_id: Optional merchant identifier.
        model: OpenAI model to use.
        client: Optional OpenAI client instance.

    Returns:
        List of generated query strings (including the original query).
    """
    client = client or get_openai_client()

    merchant_context = f"Merchant ID: {merchant_id}\n" if merchant_id else ""

    prompt = f"""You are an AI assistant specialized in revenue recovery and payment operations.
Generate {num_queries} distinct search queries from different angles (e.g., retry schedule, communication policy, error code resolution, customer escalation) to retrieve all relevant documentation from a knowledge base.

{merchant_context}Original Query:
{query}

Output Format:
Provide exactly {num_queries} queries, one per line, with no numbering, bullets, or extra commentary.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You generate distinct query variations for semantic search."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        lines = [
            line.strip()
            for line in response.choices[0].message.content.split("\n")
            if line.strip()
        ]
        # Clean numbering if any slipped in
        cleaned_queries = []
        for line in lines:
            cleaned = line.lstrip("0123456789.-) ")
            if cleaned and cleaned not in cleaned_queries:
                cleaned_queries.append(cleaned)

        # Ensure original query is included
        if query not in cleaned_queries:
            cleaned_queries.insert(0, query)

        return cleaned_queries[: num_queries + 1]
    except Exception as e:
        print(f"[QueryTransform] Warning: Error generating multi-queries: {e}. Returning original query.")
        return [query]


def generate_hyde_document(
    query: str,
    merchant_id: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    client: Optional[OpenAI] = None,
) -> str:
    """
    Hypothetical Document Embeddings (HyDE): Generate a hypothetical policy/documentation
    passage that would perfectly answer the query. Embedding this passage often matches
    actual target documentation better than embedding raw questions.

    Args:
        query: The question or recovery scenario.
        merchant_id: Optional merchant identifier.
        model: OpenAI model to use.
        client: Optional OpenAI client instance.

    Returns:
        Hypothetical document content string.
    """
    client = client or get_openai_client()

    merchant_context = f"Merchant: {merchant_id}\n" if merchant_id else ""

    prompt = f"""You are a payment system documentation author.
Write a short, authoritative documentation paragraph (3-5 sentences) that explains the standard policy, retry schedule, error code action, or communication rules that address the following query.

{merchant_context}Query:
{query}

Do not include titles, markdown headings, or commentary. Write only the factual passage.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You write authoritative payment policy excerpts."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[QueryTransform] Warning: Error generating HyDE document: {e}. Falling back to query.")
        return query


def generate_step_back_query(
    query: str,
    model: str = DEFAULT_MODEL,
    client: Optional[OpenAI] = None,
) -> str:
    """
    Step-Back Prompting: Generate a higher-level, broader conceptual question
    to retrieve foundational principles or global payment policies.

    Args:
        query: Specific user question or payment scenario.
        model: OpenAI model to use.
        client: Optional OpenAI client instance.

    Returns:
        A broader, step-back query.
    """
    client = client or get_openai_client()

    prompt = f"""You are an expert in payment recovery and billing systems.
Given the specific scenario or question below, formulate a broader, higher-level step-back question that addresses the underlying policy, standard operating procedure, or fundamental concept.

Original Query:
{query}

Return ONLY the step-back question text.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You formulate step-back conceptual questions for information retrieval."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        step_back = response.choices[0].message.content.strip()
        return step_back if step_back else query
    except Exception as e:
        print(f"[QueryTransform] Warning: Error generating step-back query: {e}. Returning original query.")
        return query


def decompose_query(
    query: str,
    model: str = DEFAULT_MODEL,
    client: Optional[OpenAI] = None,
) -> List[str]:
    """
    Decompose a complex or multi-part recovery question into independent sub-queries.

    Args:
        query: Multi-part or complex question.
        model: OpenAI model to use.
        client: Optional OpenAI client instance.

    Returns:
        List of simpler sub-queries.
    """
    client = client or get_openai_client()

    prompt = f"""Break down the following complex payment recovery question into 2 to 3 simpler, independent sub-questions that can be individually searched in a knowledge base.

Complex Query:
{query}

Output Format:
Return only the sub-questions, one per line. No bullets or numbering.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You decompose complex questions into concise sub-questions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        lines = [
            line.strip().lstrip("0123456789.-) ")
            for line in response.choices[0].message.content.split("\n")
            if line.strip()
        ]
        return lines if lines else [query]
    except Exception as e:
        print(f"[QueryTransform] Warning: Error decomposing query: {e}. Returning original query.")
        return [query]


class QueryTransformer:
    """
    Stateful / configurable Query Transformer supporting multiple transformation strategies.
    """

    def __init__(self, model: str = DEFAULT_MODEL, client: Optional[OpenAI] = None):
        self.model = model
        self.client = client or get_openai_client()

    def rewrite(self, query: str, merchant_id: Optional[str] = None, context: Optional[str] = None) -> str:
        return rewrite_query(query, merchant_id=merchant_id, context=context, model=self.model, client=self.client)

    def multi_query(self, query: str, num_queries: int = 3, merchant_id: Optional[str] = None) -> List[str]:
        return generate_multi_queries(query, num_queries=num_queries, merchant_id=merchant_id, model=self.model, client=self.client)

    def hyde(self, query: str, merchant_id: Optional[str] = None) -> str:
        return generate_hyde_document(query, merchant_id=merchant_id, model=self.model, client=self.client)

    def step_back(self, query: str) -> str:
        return generate_step_back_query(query, model=self.model, client=self.client)

    def decompose(self, query: str) -> List[str]:
        return decompose_query(query, model=self.model, client=self.client)

    def transform(
        self,
        query: str,
        strategy: str = "rewrite",
        merchant_id: Optional[str] = None,
        context: Optional[str] = None,
        num_queries: int = 3,
    ) -> Union[str, List[str]]:
        """
        Apply a query transformation strategy:
        - 'rewrite': Rewrite into an optimized single search query (default).
        - 'multi_query': Generate multiple query variations.
        - 'hyde': Generate hypothetical answer passage.
        - 'step_back': Generate high-level conceptual question.
        - 'decompose': Split into sub-queries.
        - 'passthrough': Return original query unchanged.
        """
        if strategy == "rewrite":
            return self.rewrite(query, merchant_id=merchant_id, context=context)
        elif strategy == "multi_query":
            return self.multi_query(query, num_queries=num_queries, merchant_id=merchant_id)
        elif strategy == "hyde":
            return self.hyde(query, merchant_id=merchant_id)
        elif strategy == "step_back":
            return self.step_back(query)
        elif strategy == "decompose":
            return self.decompose(query)
        elif strategy == "passthrough":
            return query
        else:
            raise ValueError(f"Unknown query transformation strategy: '{strategy}'")


if __name__ == "__main__":
    sample_query = "What should we do when a payment fails because of insufficient funds?"
    sample_merchant = "techstore"

    print("==================================================")
    print("           Query Transformation Demo              ")
    print("==================================================")
    print(f"Original Query: {sample_query}")
    print(f"Merchant ID:    {sample_merchant}\n")

    transformer = QueryTransformer()

    print("1. Rewritten Query:")
    rewritten = transformer.rewrite(sample_query, merchant_id=sample_merchant)
    print(f"   -> {rewritten}\n")

    print("2. Multi-Query Expansion:")
    queries = transformer.multi_query(sample_query, num_queries=3, merchant_id=sample_merchant)
    for idx, q in enumerate(queries, 1):
        print(f"   [{idx}] {q}")
    print()

    print("3. Step-Back Query:")
    step_back = transformer.step_back(sample_query)
    print(f"   -> {step_back}\n")

    print("4. HyDE (Hypothetical Document):")
    hyde_doc = transformer.hyde(sample_query, merchant_id=sample_merchant)
    print(f"   -> {hyde_doc}\n")
