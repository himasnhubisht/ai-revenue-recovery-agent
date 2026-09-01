from app.rag.retriever import retrieve
from app.rag.grader import grade_document

from app.agent.tools import (
    retry_payment,
    generate_payment_link,
    escalate_payment,
)


def build_query(state):

    # If this is a natural-language chat query,
    # extract the failure reason from it.
    if state.get("query"):

        query = state["query"].lower()

        if "insufficient" in query or "insufficient_funds" in query:
            failure_reason = "insufficient_funds"

        elif "card declined" in query or "card_declined" in query:
            failure_reason = "card_declined"

        elif "bank timeout" in query or "bank_timeout" in query:
            failure_reason = "bank_timeout"

        else:
            failure_reason = state.get("failure_reason", "")

        return {
            **state,
            "failure_reason": failure_reason
        }

    # Structured /recover request
    query = (
        f"What should be done for a payment failure "
        f"caused by {state['failure_reason']} "
        f"for merchant {state['merchant_id']}?"
    )

    return {
        **state,
        "query": query
    }


def retrieve_knowledge(state):

    try:
        results = retrieve(
            state["query"],
            state["merchant_id"]
        )

        return {
            "retrieved_documents": results,
            "retrieval_error": False
        }

    except Exception as exc:

        print(f"RAG retrieval failed: {exc}")

        return {
            "retrieved_documents": [],
            "retrieval_error": True
        }

def grade_knowledge(state):

    documents = state.get(
        "retrieved_documents",
        []
    )

    # No documents means the agent cannot safely
    # make an automatic recovery decision.
    if not documents:
        return {
            "relevant": False,
            "grading_error": True
        }

    query = state["query"]

    try:

        for document, score in documents:

            if grade_document(query, document):
                return {
                    "relevant": True,
                    "grading_error": False
                }

        return {
            "relevant": False,
            "grading_error": False
        }

    except Exception as exc:

        print(f"Knowledge grading failed: {exc}")

        return {
            "relevant": False,
            "grading_error": True}

def decision_node(state):

    failure_reason = state["failure_reason"]
    attempt_count = state.get("attempt_count", 0)

    documents = state.get("retrieved_documents", [])

    # ---------------------------------------------------------
    # Find merchant policy from retrieved documents
    # ---------------------------------------------------------

    policy_text = ""

    for document, score in documents:

        text = document.page_content

        if failure_reason.replace("_", " ").lower() in text.lower():
            policy_text = text
            break

    # ---------------------------------------------------------
    # If RAG policy was not found, fail safely
    # ---------------------------------------------------------

    if not policy_text:

        return {
            "action": "escalate",
            "decision_reason": (
                "No relevant merchant recovery policy was "
                "retrieved. The payment was escalated for "
                "manual review."
            )
        }

    # ---------------------------------------------------------
    # Decision based on retrieved merchant policy
    # ---------------------------------------------------------

    if failure_reason == "insufficient_funds":

        if attempt_count < 2:

            return {
                "action": "retry",
                "decision_reason": (
                    "The retrieved TechStore policy allows "
                    "up to 2 automatic retries for insufficient "
                    "funds. The current attempt count is "
                    f"{attempt_count}, so another retry is allowed."
                )
            }

        return {
            "action": "payment_link",
            "decision_reason": (
                "The retrieved TechStore policy allows a maximum "
                "of 2 automatic retries for insufficient funds. "
                "The retry limit has been reached, so a payment "
                "link will be generated."
            )
        }

    elif failure_reason == "card_declined":

        if attempt_count < 1:

            return {
                "action": "retry",
                "decision_reason": (
                    "The retrieved merchant policy allows one "
                    "retry for a card decline. No retry has been "
                    "used yet, so the payment will be retried."
                )
            }

        return {
            "action": "payment_link",
            "decision_reason": (
                "The retrieved merchant policy allows one retry "
                "for a card decline. The retry limit has been "
                "reached, so a payment link will be generated."
            )
        }

    elif failure_reason == "bank_timeout":

        if attempt_count < 2:

            return {
                "action": "retry",
                "decision_reason": (
                    "The retrieved merchant policy allows up to "
                    "2 retries for a bank timeout. The current "
                    f"attempt count is {attempt_count}, so another "
                    "retry is allowed."
                )
            }

        return {
            "action": "escalate",
            "decision_reason": (
                "The retrieved merchant policy allows up to "
                "2 retries for a bank timeout. The retry limit "
                "has been reached, so the payment is escalated."
            )
        }

    else:

        return {
            "action": "escalate",
            "decision_reason": (
                f"The failure reason '{failure_reason}' is not "
                "covered by the retrieved recovery policy. "
                "The payment was escalated for safety."
            )
        }

def fallback_decision(state):

    return {
        "action": "escalate",
        "decision_reason": (
            "The agent could not obtain sufficiently relevant "
            "recovery policy knowledge. The payment was escalated "
            "for manual review instead of taking an unsafe action."
        )
    }

def execute_action(state):

    action = state["action"]

    payment_id = state.get("payment_id", "demo_payment")
    amount = state.get("amount", 0)

    if action == "retry":
        result = retry_payment(payment_id, amount)

    elif action == "payment_link":
        result = generate_payment_link(payment_id, amount)

    elif action == "escalate":
        result = escalate_payment(payment_id, amount)

    else:
        result = {
            "status": "error",
            "message": "Unknown action."
        }

    return {
        "action_result": result
    }


def generate_response(state):

    action = state.get("action")
    action_result = state.get("action_result", {})
    failure_reason = state.get("failure_reason")

    if action == "retry":

        response = (
            f"The payment failed because of {failure_reason}. "
            f"The payment is eligible for another retry. "
            f"The agent has initiated the retry."
        )

    elif action == "payment_link":

        payment_link = action_result.get("payment_link")

        response = (
            f"The payment has reached the retry limit. "
            f"The agent generated a payment link."
        )

        if payment_link:
            response += f" Payment link: {payment_link}"

    elif action == "escalate":

        response = (
            "The payment cannot be automatically recovered. "
            "The case has been escalated for manual review."
        )

    else:

        response = "I could not determine a valid recovery action."

    return {
        "final_response": response
    }