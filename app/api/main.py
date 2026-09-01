from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.agent.graph import graph
from app.agent.tools import escalate_payment


app = FastAPI(
    title="AI Revenue Recovery Agent"
)


class PaymentFailureEvent(BaseModel):
    payment_id: str = Field(min_length=1)
    merchant_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    failure_reason: str = Field(min_length=1)
    attempt_count: int = Field(ge=0)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "AI Revenue Recovery Agent"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.post("/webhook/payment-failed")
def payment_failed(payment: PaymentFailureEvent):

    payment_data = payment.model_dump()

    try:
        result = graph.invoke(payment_data)

        action_result = result.get(
            "action_result",
            {}
        )

        return {
            "payment_id": result.get("payment_id"),
            "merchant_id": result.get("merchant_id"),
            "failure_reason": result.get("failure_reason"),
            "action": result.get("action"),
            "status": action_result.get("status"),
            "amount_recovered": action_result.get(
                "amount_recovered",
                0
            ),
            "decision_reason": result.get(
                "decision_reason",
                "No decision reason available."
            ),
            "message": action_result.get("message")
        }

    except Exception as exc:

        # Safe fallback:
        # Never take an unsafe automatic action if
        # the agent/RAG infrastructure fails.

        fallback = escalate_payment(
            payment.payment_id,
            payment.amount
        )

        return {
            "payment_id": payment.payment_id,
            "merchant_id": payment.merchant_id,
            "failure_reason": payment.failure_reason,
            "action": "escalate",
            "status": "escalated",
            "amount_recovered": 0,
            "decision_reason": (
                "Agent recovery intelligence failed. "
                "Payment was safely escalated for manual review."
            ),
            "message": fallback.get(
                "message",
                "Payment escalated for manual review."
            ),
            "error": "recovery_pipeline_failure"
        }