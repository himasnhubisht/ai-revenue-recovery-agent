import json

from app.agent.graph import graph

from app.agent.audit import log_decision
def load_payments():

    with open("data/payments.json", "r") as file:
        return json.load(file)


def run_batch():

    payments = load_payments()

    results = []

    for payment in payments:

        print(f"\nProcessing {payment['payment_id']}...")

        result = graph.invoke(payment)
        log_decision(result)

        results.append(result)

        action = result.get("action")
        action_result = result.get("action_result", {})

        print(f"Action: {action}")
        print(f"Status: {action_result.get('status')}")

        if action_result.get("amount_recovered", 0) > 0:
            print(
                f"Recovered: ₹{action_result['amount_recovered']}"
            )

    return results


def calculate_metrics(results):

    total_at_risk = 0
    total_recovered = 0

    successful_retries = 0
    failed_retries = 0

    payment_links = 0
    successful_payment_links = 0

    escalations = 0

    for result in results:

        amount = result.get("amount", 0)

        total_at_risk += amount

        action = result.get("action")

        action_result = result.get(
            "action_result",
            {}
        )

        status = action_result.get("status")

        amount_recovered = action_result.get(
            "amount_recovered",
            0
        )

        # -------------------------
        # RETRY
        # -------------------------

        if action == "retry":

            if status == "success":

                successful_retries += 1
                total_recovered += amount_recovered

            else:

                failed_retries += 1

        # -------------------------
        # PAYMENT LINK
        # -------------------------

        elif action == "payment_link":

            payment_links += 1

            if status == "success":

                successful_payment_links += 1
                total_recovered += amount_recovered

        # -------------------------
        # ESCALATION
        # -------------------------

        elif action == "escalate":

            escalations += 1

    # -------------------------
    # RECOVERY RATE
    # -------------------------

    if total_at_risk > 0:

        recovery_rate = (
            total_recovered / total_at_risk
        ) * 100

    else:

        recovery_rate = 0

    return {

        "total_payments": len(results),

        "total_at_risk": total_at_risk,

        "total_recovered": total_recovered,

        "recovery_rate": round(
            recovery_rate,
            2
        ),

        "successful_retries":
            successful_retries,

        "failed_retries":
            failed_retries,

        "payment_links":
            payment_links,

        "successful_payment_links":
            successful_payment_links,

        "escalations":
            escalations
    }


if __name__ == "__main__":

    results = run_batch()

    metrics = calculate_metrics(results)

    print("\n")
    print("==============================")
    print("       RECOVERY REPORT")
    print("==============================")

    print(
        "Total Payments:",
        metrics["total_payments"]
    )

    print(
        "Revenue At Risk: ₹",
        metrics["total_at_risk"]
    )

    print(
        "Revenue Recovered: ₹",
        metrics["total_recovered"]
    )

    print(
        "Recovery Rate:",
        metrics["recovery_rate"],
        "%"
    )

    print(
        "Successful Retries:",
        metrics["successful_retries"]
    )

    print(
        "Failed Retries:",
        metrics["failed_retries"]
    )

    print(
        "Payment Links:",
        metrics["payment_links"]
    )

    print(
        "Successful Link Payments:",
        metrics["successful_payment_links"]
    )

    print(
        "Escalations:",
        metrics["escalations"]
    )