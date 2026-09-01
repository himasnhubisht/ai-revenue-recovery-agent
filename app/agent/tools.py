import random


def retry_payment(payment_id, amount=0):
    """
    Simulates a payment retry.

    In a real system this would call the payment gateway.
    Here we randomly simulate success/failure.
    """

    success = random.random() < 0.6

    if success:
        return {
            "status": "success",
            "action": "retry",
            "payment_id": payment_id,
            "amount_recovered": amount,
            "message": "Payment retry successful."
        }

    return {
        "status": "failed",
        "action": "retry",
        "payment_id": payment_id,
        "amount_recovered": 0,
        "message": "Payment retry failed."
    }


def generate_payment_link(payment_id, amount=0):

    # Simulate whether customer pays through the link
    paid = random.random() < 0.5

    if paid:
        return {
            "status": "success",
            "action": "payment_link",
            "payment_id": payment_id,
            "amount": amount,
            "amount_recovered": amount,
            "payment_link": f"https://pay.example.com/{payment_id}",
            "message": "Customer paid through payment link."
        }

    return {
        "status": "pending",
        "action": "payment_link",
        "payment_id": payment_id,
        "amount": amount,
        "amount_recovered": 0,
        "payment_link": f"https://pay.example.com/{payment_id}",
        "message": "Payment link generated. Customer has not paid yet."
    }


def escalate_payment(payment_id, amount=0):
    """
    Simulates escalation to a human/payment operations team.
    """

    return {
        "status": "escalated",
        "action": "escalate",
        "payment_id": payment_id,
        "amount_at_risk": amount,
        "message": "Payment escalated for manual review."
    }