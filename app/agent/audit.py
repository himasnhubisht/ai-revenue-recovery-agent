import json
from datetime import datetime
from pathlib import Path


AUDIT_FILE = Path("data/audit_log.json")


def log_decision(result):

    action_result = result.get("action_result", {})

    entry = {
        "timestamp": datetime.now().isoformat(),

        "payment_id": result.get(
            "payment_id"
        ),
        "decision_reason": result.get(
            "decision_reason"
        ),
        "merchant_id": result.get(
            "merchant_id"
        ),

        "amount": result.get(
            "amount",
            0
        ),

        "failure_reason": result.get(
            "failure_reason"
        ),

        "attempt_count": result.get(
            "attempt_count",
            0
        ),

        "action": result.get(
            "action"
        ),

        "status": action_result.get(
            "status"
        ),

        "amount_recovered": action_result.get(
            "amount_recovered",
            0
        ),

        "message": action_result.get(
            "message"
        )
    }

    AUDIT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    existing_logs = []

    if AUDIT_FILE.exists():

        with open(
            AUDIT_FILE,
            "r"
        ) as file:

            try:
                existing_logs = json.load(file)

            except json.JSONDecodeError:
                existing_logs = []

    existing_logs.append(entry)

    with open(
        AUDIT_FILE,
        "w"
    ) as file:

        json.dump(
            existing_logs,
            file,
            indent=4
        )

    return entry