# FashionKart Communication Policy

Merchant ID: fashionkart

## Payment Link

A payment link may be generated when:

- The permitted retry attempts have been exhausted.
- The payment is eligible for customer recovery.

## Customer Notifications

The system may send a recovery notification after a failed recovery attempt.

The notification should:

- Clearly state that the payment was unsuccessful.
- Provide the next available payment option.
- Never expose internal system information.

## Restrictions

Do not send repeated notifications for the same failed payment within a short period.