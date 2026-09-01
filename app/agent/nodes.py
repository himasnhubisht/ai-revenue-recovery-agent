import re

from app.rag.retriever import retrieve
from app.rag.grader import grade_document

from app.agent.tools import (
    retry_payment,
    generate_payment_link,
    escalate_payment,
)


def build_query(state):
    """
    Build a RAG query from the payment failure event.

    Also supports natural-language queries from the frontend.
    """

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
    """
    Retrieve merchant-specific recovery policies using RAG.
    """

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
    """
    Check whether retrieved documents are relevant enough
    to make an automatic recovery decision.
    """

    documents = state.get(
        "retrieved_documents",
        []
    )

    # No documents -> unsafe to make an automatic decision
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
            "grading_error": True
        }


def decision_node(state):
    """
    Decide the recovery action using the retrieved merchant policy.

    IMPORTANT:
    Retry limits are NOT hardcoded for a specific merchant.
    They are extracted from the retrieved policy.
    """

    failure_reason = state.get(
        "failure_reason",
        ""
    )

    attempt_count = state.get(
        "attempt_count",
        0
    )

    merchant_id = state.get(
        "merchant_id",
        "unknown"
    )

    documents = state.get(
        "retrieved_documents",
        []
    )

    # ---------------------------------------------------------
    # Find the merchant-specific policy
    # ---------------------------------------------------------

    policy_text = ""

    for document, score in documents:

        document_merchant = document.metadata.get(
            "merchant_id"
        )

        # Only use the requested merchant's policy
        if document_merchant != merchant_id:
            continue

        text = document.page_content

        # Make sure the policy actually discusses
        # this failure reason
        normalized_failure = (
            failure_reason
            .replace("_", " ")
            .lower()
        )

        if normalized_failure in text.lower():

            policy_text = text
            break

    # ---------------------------------------------------------
    # No applicable policy -> SAFE FALLBACK
    # ---------------------------------------------------------

    if not policy_text:

        return {
            "action": "escalate",
            "decision_reason": (
                f"No applicable recovery policy was found "
                f"for merchant '{merchant_id}' and failure "
                f"reason '{failure_reason}'. "
                "The payment was escalated for manual review."
            )
        }

    policy_lower = policy_text.lower()

    # ---------------------------------------------------------
    # Extract retry limit from policy
    # ---------------------------------------------------------

    max_retries = None

    # Example supported policy language:
    #
    # "maximum of 2 automatic retries"
    # "up to 2 automatic retries"
    # "only 1 automatic retry"
    # "1 automatic retry"
    # "one automatic retry"
    # "one retry"
    #
    numeric_patterns = [
        r"maximum of (\d+) automatic retr",
        r"maximum (\d+) automatic retr",
        r"up to (\d+) automatic retr",
        r"only (\d+) automatic retr",
        r"(\d+) automatic retr",
    ]

    for pattern in numeric_patterns:

        match = re.search(
            pattern,
            policy_lower
        )

        if match:

            max_retries = int(
                match.group(1)
            )

            break

    # Handle "one automatic retry"
    if (
        max_retries is None
        and "one automatic retry" in policy_lower
    ):
        max_retries = 1

    # Handle "one retry"
    if (
        max_retries is None
        and "one retry" in policy_lower
    ):
        max_retries = 1

    # Handle "retry once"
    if (
        max_retries is None
        and "retry once" in policy_lower
    ):
        max_retries = 1

    # ---------------------------------------------------------
    # Could not safely understand the policy
    # ---------------------------------------------------------

    if max_retries is None:

        return {
            "action": "escalate",
            "decision_reason": (
                f"The recovery policy for merchant "
                f"'{merchant_id}' was retrieved, but "
                "its retry limit could not be safely "
                "determined. The payment was escalated."
            )
        }

    # ---------------------------------------------------------
    # RETRY
    # ---------------------------------------------------------

    if attempt_count < max_retries:

        return {
            "action": "retry",
            "decision_reason": (
                f"The retrieved {merchant_id} merchant "
                f"policy allows up to {max_retries} "
                f"retry attempt(s) for "
                f"{failure_reason.replace('_', ' ')}. "
                f"The current attempt count is "
                f"{attempt_count}, so another retry "
                "is allowed."
            )
        }

    # ---------------------------------------------------------
    # RETRY LIMIT REACHED
    # Determine next action from the policy
    # ---------------------------------------------------------

    if "payment link" in policy_lower:

        return {
            "action": "payment_link",
            "decision_reason": (
                f"The retrieved {merchant_id} merchant "
                f"policy allows {max_retries} retry "
                f"attempt(s) for "
                f"{failure_reason.replace('_', ' ')}. "
                "The retry limit has been reached, "
                "so a payment link will be generated."
            )
        }

    # ---------------------------------------------------------
    # ESCALATE
    # ---------------------------------------------------------

    if "escalate" in policy_lower:

        return {
            "action": "escalate",
            "decision_reason": (
                f"The retrieved {merchant_id} merchant "
                f"policy allows {max_retries} retry "
                f"attempt(s) for "
                f"{failure_reason.replace('_', ' ')}. "
                "The retry limit has been reached, "
                "so the payment will be escalated."
            )
        }

    # ---------------------------------------------------------
    # Unknown post-retry action -> SAFE FALLBACK
    # ---------------------------------------------------------

    return {
        "action": "escalate",
        "decision_reason": (
            f"The retrieved {merchant_id} merchant policy "
            "does not specify a safe action after the "
            "retry limit. The payment was escalated."
        )
    }


def fallback_decision(state):
    """
    Safe fallback when RAG retrieval/grading fails.
    """

    merchant_id = state.get(
        "merchant_id",
        "unknown"
    )

    return {
        "action": "escalate",
        "decision_reason": (
            f"The agent could not obtain sufficiently "
            f"relevant recovery policy knowledge for "
            f"merchant '{merchant_id}'. "
            "The payment was escalated for manual review "
            "instead of taking an unsafe automatic action."
        )
    }


def execute_action(state):
    """
    Execute the bounded recovery action.
    """

    action = state["action"]

    payment_id = state.get(
        "payment_id",
        "demo_payment"
    )

    amount = state.get(
        "amount",
        0
    )

    if action == "retry":

        result = retry_payment(
            payment_id,
            amount
        )

    elif action == "payment_link":

        result = generate_payment_link(
            payment_id,
            amount
        )

    elif action == "escalate":

        result = escalate_payment(
            payment_id,
            amount
        )

    else:

        result = {
            "status": "error",
            "message": "Unknown action."
        }

    return {
        "action_result": result
    }


def generate_response(state):
    """
    Generate the final human-readable response.
    """

    action = state.get("action")

    action_result = state.get(
        "action_result",
        {}
    )

    failure_reason = state.get(
        "failure_reason"
    )

    if action == "retry":

        response = (
            f"The payment failed because of "
            f"{failure_reason}. "
            "The payment is eligible for another retry. "
            "The agent has initiated the retry."
        )

    elif action == "payment_link":

        payment_link = action_result.get(
            "payment_link"
        )

        response = (
            "The payment has reached the retry limit. "
            "The agent generated a payment link."
        )

        if payment_link:

            response += (
                f" Payment link: {payment_link}"
            )

    elif action == "escalate":

        response = (
            "The payment cannot be automatically recovered. "
            "The case has been escalated for manual review."
        )

    else:

        response = (
            "I could not determine a valid "
            "recovery action."
        )

    return {
        "final_response": response
    }