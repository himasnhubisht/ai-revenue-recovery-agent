# TechStore Payment Retry Policy

Merchant ID: techstore

## Insufficient Funds

If a payment fails because of insufficient funds:

- A maximum of 2 automatic retries are allowed.
- Wait at least 30 minutes between retries.
- If both retries fail, generate a payment link.
- Do not retry after the maximum limit.

## Bank Timeout

If a payment fails because of a bank timeout:

- Retry once after 10 minutes.
- A second retry may be performed after 30 minutes.
- If both retries fail, escalate the payment.

## Card Declined

If a card is declined:

- One retry is allowed after 30 minutes.
- If the retry fails, generate a payment link.

## General Rule

Never exceed the maximum retry attempts.