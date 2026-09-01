# EduPro Payment Retry Policy

Merchant ID: edupro

## Insufficient Funds

If a payment fails because of insufficient funds:

- Only one automatic retry is allowed.
- Wait at least 60 minutes before retrying.
- If the retry fails, do not retry again.
- Generate a payment link after the failed retry.

## Bank Timeout

If a payment fails because of a bank timeout:

- One retry is allowed after 20 minutes.
- If the retry fails, escalate the case.

## Card Declined

If a card payment is declined:

- One retry is allowed after 60 minutes.
- If the retry fails, generate a payment link.

## General Rule

Never exceed the maximum retry attempts defined above.