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

    results = retrieve(
        state["query"],
        state["merchant_id"]
    )

    return {
        "retrieved_documents": results
    }


def grade_knowledge(state):

    query = state["query"]
    documents = state["retrieved_documents"]

    relevant = False

    for document, score in documents:

        if grade_document(query, document):
            relevant = True
            break

    return {
        "relevant": relevant
    }
   
         
def decision_node(state):

    failure_reason = state["failure_reason"]
    attempt_count = state.get("attempt_count", 0)

    if failure_reason == "insufficient_funds":

        if attempt_count < 2:
            action = "retry"

            decision_reason = (
                f"Insufficient funds caused the payment failure. "
                f"{attempt_count} retry attempt(s) have already been used. "
                f"TechStore allows up to 2 automatic retries, "
                f"so the agent will retry the payment."
            )

        else:
            action = "payment_link"

            decision_reason = (
                "The payment has already reached the maximum of "
                "2 automatic retries allowed by TechStore. "
                "The agent will stop retrying and generate a payment link."
            )

    elif failure_reason == "card_declined":

        if attempt_count < 1:
            action = "retry"

            decision_reason = (
                "The payment was declined by the card issuer. "
                "No retry has been used yet, so the agent will "
                "attempt a recovery retry."
            )

        else:
            action = "payment_link"

            decision_reason = (
                "The allowed retry attempt has already been used "
                "for this card decline. The agent will generate "
                "a payment link instead."
            )

    elif failure_reason == "bank_timeout":

        if attempt_count < 2:
            action = "retry"

            decision_reason = (
                f"The payment failed because of a bank timeout. "
                f"{attempt_count} retry attempt(s) have been used, "
                "so another retry is allowed."
            )

        else:
            action = "escalate"

            decision_reason = (
                "The maximum retry limit has been reached for "
                "this bank timeout. The agent will escalate the "
                "payment for further review."
            )

    else:

        action = "escalate"

        decision_reason = (
            f"The failure reason '{failure_reason}' is not covered "
            "by the configured recovery policies. The agent will "
            "escalate instead of taking an unsafe recovery action."
        )

    return {
        "action": action,
        "decision_reason": decision_reason
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