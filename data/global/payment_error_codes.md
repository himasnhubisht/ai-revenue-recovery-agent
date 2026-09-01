# Payment Error Reference

## insufficient_funds

The customer's available balance is insufficient to complete the payment.

Possible recovery actions depend on the merchant's configured policy.

## card_declined

The card issuer declined the payment.

Recovery actions depend on merchant policy and the reason for the decline.

## bank_timeout

The payment provider did not receive a timely response from the bank.

A retry may be possible depending on merchant policy.

## network_error

A temporary network-related failure occurred.

Recovery actions should follow the merchant's configured retry policy.

## unknown_error

The system cannot determine the exact cause of the payment failure.

The agent must not guess an action. The case should be escalated.