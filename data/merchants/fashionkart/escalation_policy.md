# FashionKart Escalation Policy

Merchant ID: fashionkart

## High Value Payments

Payments above INR 10,000 are considered high-value payments.

High-value payment failures should be escalated after the permitted recovery attempts are exhausted.

## Repeated Failures

If the maximum permitted recovery attempts have been exhausted:

- Stop automatic retries.
- Create an escalation case.
- Record the reason for escalation.

## System Errors

If the payment system returns an unknown or unsupported error:

- Do not guess the recovery action.
- Stop automatic recovery.
- Escalate the case for manual review.