# FashionKart Payment Retry Policy

Merchant ID: fashionkart

## Insufficient Funds

If a payment fails because of insufficient funds:

- A retry is allowed.
- Wait at least 30 minutes before retrying.
- Maximum total retry attempts: 2.
- If the second retry fails, do not retry again.
- After the retry limit is reached, generate a payment link.

## Bank Timeout

If a payment fails because of a bank timeout:

- Retry once after 10 minutes.
- A second retry is allowed after 30 minutes.
- Maximum total retry attempts: 2.
- If both retries fail, escalate the case.

## Card Declined

If a payment is declined by the card issuer:

- Do not repeatedly retry immediately.
- Allow one retry after 30 minutes.
- If the retry fails, generate a payment link.

## General Rule

Never exceed the maximum retry attempts defined above.