# EduPro Escalation Policy

Merchant ID: edupro

## High Value Payments

Payments above INR 20,000 are considered high-value payments.

High-value payment failures should be escalated after the permitted recovery attempts are exhausted.

## Repeated Failures

After the maximum retry attempts:

- Stop automatic recovery.
- Create an escalation case.
- Record the failure reason.

## Unknown Errors

If the failure reason is unknown:

- Do not automatically retry.
- Escalate for manual investigation.