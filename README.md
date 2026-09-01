# 💰 AI Revenue Recovery Agent

An AI-powered revenue recovery agent that detects failed payments, retrieves relevant merchant recovery policies using RAG, selects a bounded recovery action, executes the action, and records the outcome for audit and revenue tracking.

---

## 🎯 Problem

Revenue can be lost when:

- Payments fail
- Customers abandon checkout
- Subscription payments fail
- Recovery attempts are not handled systematically

The goal of this project is to automate the payment recovery workflow while keeping recovery actions bounded and auditable.

---

## 🤖 What the Agent Does

The system follows this workflow:

Payment Failure
        ↓
Build Query
        ↓
Retrieve Merchant Knowledge using RAG
        ↓
Grade Retrieved Knowledge
        ↓
Bounded Decision
        ↓
Execute Recovery Action
        ↓
Audit Log
        ↓
Revenue Metrics

The agent can choose between:

- 🔄 Retry payment
- 🔗 Generate payment link
- 🚨 Escalate the payment

---

## 🧠 RAG Pipeline

Merchant recovery policies are stored as documents and embedded into a vector database.

For a payment failure:

1. A query is created from the payment context.
2. Relevant merchant-specific knowledge is retrieved.
3. Retrieved documents are checked for relevance.
4. The agent proceeds only when relevant knowledge is available.

This allows recovery decisions to be grounded in merchant-specific policies.

---

## 🔄 Recovery Decision Logic

| Failure Reason | Condition | Action |
|---|---|---|
| Insufficient funds | Attempts < 2 | Retry |
| Insufficient funds | Attempts ≥ 2 | Payment Link |
| Card declined | Attempts < 1 | Retry |
| Card declined | Attempts ≥ 1 | Payment Link |
| Bank timeout | Attempts < 2 | Retry |
| Bank timeout | Attempts ≥ 2 | Escalate |
| Unknown error | Any | Escalate |

The agent does not have unrestricted control over payment operations.

---

## 🛠️ Tech Stack

- Python
- LangGraph
- RAG
- ChromaDB
- FastAPI
- Streamlit
- Requests
- Pytest

---

## 📁 Project Structure

```text
AI_REVENUE_AGENT/
│
├── app/
│   ├── agent/
│   ├── rag/
│   └── ...
│
├── data/
│   ├── merchants/
│   ├── global/
│   ├── payments.json
│   └── audit_log.json
│
├── frontend/
│   └── app.py
│
├── scripts/
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
🚀 Running the Project
1. Clone the repository
git clone https://github.com/himasnhubisht/ai-revenue-recovery-agent.git
cd ai-revenue-recovery-agent
2. Create virtual environment

Windows PowerShell:

python -m venv venv
.\venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a .env file in the project root:

OPENAI_API_KEY=your_api_key_here

Never commit your real API key to GitHub.

5. Start FastAPI
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000
6. Start Streamlit

Open another terminal:

.\venv\Scripts\Activate.ps1
python -m streamlit run frontend/app.py
🔌 Payment Webhook

The system exposes:

POST /webhook/payment-failed

Example request:

{
    "payment_id": "pay_test",
    "merchant_id": "techstore",
    "amount": 3000,
    "failure_reason": "insufficient_funds",
    "attempt_count": 1
}

The event is passed into the LangGraph agent.

The agent:

Builds the query.
Retrieves relevant merchant knowledge.
Grades the knowledge.
Determines the recovery action.
Executes the recovery tool.
Returns the result.
Records the event.

Example response:

{
    "payment_id": "pay_test",
    "merchant_id": "techstore",
    "failure_reason": "insufficient_funds",
    "action": "retry",
    "status": "success",
    "amount_recovered": 3000
}
🧩 Recovery Actions
🔄 Retry

Attempts to recover a failed payment when another retry is allowed by the recovery policy.

🔗 Payment Link

When automatic recovery reaches its allowed limit, the system generates a payment link as an alternative recovery path.

🚨 Escalation

If automatic recovery is not appropriate, the payment is escalated for further handling.

📊 Batch Revenue Recovery

The project can process multiple payment failures as a batch.

Run:

python -m app.agent.batch_runner

Example:

==============================
       RECOVERY REPORT
==============================

Total Payments: 10
Revenue At Risk: ₹53000
Revenue Recovered: ₹33300
Recovery Rate: 62.83 %

Successful Retries: 7
Failed Retries: 0
Payment Links: 2
Successful Link Payments: 0
Escalations: 1
🖥️ Streamlit Dashboard

The dashboard provides:

Payment failure simulation
Payment ID
Merchant ID
Payment amount
Failure reason
Attempt count
Agent action
Recovery status
Amount recovered
Decision reason
Revenue at risk
Revenue recovered
Recovery rate
Successful retries
Payment links
Escalations
Payment recovery activity

The frontend communicates with the FastAPI backend through the payment failure webhook.

🧾 Auditability

Processed payment events are recorded in:

data/audit_log.json

Audit records contain:

Payment ID
Merchant
Amount
Failure reason
Selected action
Action status
Amount recovered
Timestamp

This provides an audit trail for the recovery workflow.

🧪 Testing

Run:

pytest

The project includes tests for important application functionality.

🔐 Safety and Bounded Actions

This project uses simulated payment tools rather than real payment processing.

Available recovery actions are explicitly bounded to:

retry
payment_link
escalate

The system does not directly control real financial accounts.

In production, simulated tools could be replaced with payment provider APIs together with authentication, authorization, idempotency, monitoring, rate limiting, and compliance controls.

🏗️ Architecture
Payment Failure
       │
       ▼
FastAPI Webhook
       │
       ▼
LangGraph Agent
       │
       ▼
Build Query
       │
       ▼
RAG Retrieval
       │
       ▼
Knowledge Grading
       │
       ▼
Recovery Decision
    /    |    \
   ▼     ▼     ▼
 Retry  Payment  Escalate
        Link
    \    |    /
       ▼
   Audit Log
       │
       ▼
Revenue Metrics
       │
       ▼
Streamlit Dashboard
🔮 Future Improvements
Real payment provider integration
Persistent production database
Authentication and authorization
Scheduled recovery workflows
Customer notification systems
Advanced monitoring
Production deployment
Subscription payment recovery
Overdue invoice recovery
Human approval workflows
👨‍💻 Author

Himanshu Bisht

GitHub: https://github.com/himasnhubisht


### 5. Click **Commit changes**

**DONE. Stop there.** 😂

Don't add screenshots, don't modify Python, don't run commands.

After this, just tell me **`done`** and I'll give you **ONE next task only**.
