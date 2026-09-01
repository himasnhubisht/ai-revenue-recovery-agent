import json
import random
from pathlib import Path


MERCHANTS = ["fashionkart", "edupro", "techstore"]

FAILURE_REASONS = [
    "insufficient_funds",
    "card_declined",
    "bank_timeout",
    "network_error",
]


def generate_event(payment_number: int):
    merchant_id = random.choice(MERCHANTS)

    event = {
        "merchant_id": merchant_id,
        "payment_id": f"pay_{payment_number:04d}",
        "customer_id": f"cust_{random.randint(100, 999)}",
        "amount": random.choice([500, 1000, 2000, 5000, 8000, 12000, 25000]),
        "currency": "INR",
        "failure_reason": random.choice(FAILURE_REASONS),
        "attempt_count": random.randint(0, 2),
    }

    return event


def main():
    events = []

    for i in range(1, 101):
        events.append(generate_event(i))

    output_path = Path("data/payment_events.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as file:
        json.dump(events, file, indent=2)

    print(f"Generated {len(events)} payment events.")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()