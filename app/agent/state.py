from typing import TypedDict


class AgentState(TypedDict, total=False):

    merchant_id: str
    payment_id: str
    amount: float
    failure_reason: str
    attempt_count: int

    query: str

    retrieved_documents: list

    relevant: bool

    action: str

    action_result: dict

    final_response: str
    retrieval_error: bool
    grading_error: bool