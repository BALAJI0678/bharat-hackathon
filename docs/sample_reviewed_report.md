# Bharat Evidence Agent — Reviewed triage report

Case: Synthetic UPI scam triage — Bharat
Mode: synthetic_demo
Reviewer: Synthetic Demo Reviewer
Approved: 2026-10-01T04:49:29.552818+00:00
Run: 209bd429-d1fd-45f5-8f5e-96c01b10b19c

## Important limits
Rule-based triage, not forensic attribution, legal advice, or proof of wrongdoing.
Hashes establish an import snapshot only, not the authenticity of acquisition.

## Objective
Review potential UPI fraud indicators and correlate payments

## Summary
7 imported records; 3 review leads; 6 timestamped events. No conclusion of guilt or fraud is made.

## Findings
### F-1 · high · Review communication indicators
Evidence: SMS-001
Matched explicit rules: credential_request, payment_pressure, link. A match is a review lead, not proof of fraud.
{"body":"खाता बंद हो जाएगा। तुरंत केवाईसी अपडेट करें: https://demo-bank.invalid/verify — OTP भेजें।","from":"DEMO-KYC"}

### F-2 · high · Review communication indicators
Evidence: SMS-002
Matched explicit rules: credential_request, payment_pressure. A match is a review lead, not proof of fraud.
{"body":"Urgent: share OTP to verify account. Reply to helpdesk@demo-bank.invalid","from":"DEMO-KYC"}

### C-1 · medium · Payment within 30 minutes after a flagged communication
Evidence: SMS-001, SMS-002, PAY-001
Timestamp proximity only; sender identity, account ownership and causality are not established.
{"amount_inr":4500,"recipient":"demo-merchant@upi","reference":"SYNTHETIC-001","status":"success"}

## Timeline
- 2026-01-15T04:28:00+00:00 | CALLS | CALL-001 | {"duration_seconds":125,"from":"DEMO-CALLER"}
- 2026-01-15T04:30:00+00:00 | SMS | SMS-001 | {"body":"खाता बंद हो जाएगा। तुरंत केवाईसी अपडेट करें: https://demo-bank.invalid/verify — OTP भेजें।","from":"DEMO-KYC"}
- 2026-01-15T04:34:00+00:00 | SMS | SMS-002 | {"body":"Urgent: share OTP to verify account. Reply to helpdesk@demo-bank.invalid","from":"DEMO-KYC"}
- 2026-01-15T04:42:00+00:00 | UPI | PAY-001 | {"amount_inr":4500,"recipient":"demo-merchant@upi","reference":"SYNTHETIC-001","status":"success"}
- 2026-01-15T06:50:00+00:00 | SMS | SMS-003 | {"body":"Please bring groceries home today.","from":"DEMO-FAMILY"}
- 2026-01-15T08:00:00+00:00 | UPI | PAY-002 | {"amount_inr":150,"recipient":"demo-grocer@upi","reference":"SYNTHETIC-002"}

## Import manifest
SHA-256 (uploaded UTF-8 file bytes): c9ad0dccf363ea0ed76c7b2fc3c98f6e147c5817f8d873d707803e1bea2072fc
Records snapshot: fac1f4a5b2650ef63de8a86cb652e2e4b55e271427c7a2ecab956cb9a0a28457
Audit root: ba3179800c9a1bda2981d9ebfdc09b5a25c96b5139e9f968c3eb8010ac5815d9

## Warnings
NOTE-001: missing/invalid timezone-aware timestamp; excluded from timed correlations