from fastapi import FastAPI
from app.agent.graph import graph
from app.agent.audit import log_decision

app = FastAPI(
    title="AI Revenue Recovery Agent"
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "AI Revenue Recovery Agent"
    }


@app.post("/webhook/payment-failed")
def payment_failed(payment: dict):

    result = graph.invoke(payment)

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