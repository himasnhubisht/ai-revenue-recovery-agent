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
Build / Transform Query
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

This allows recovery decisions to be grounded in merchant-specific policies instead of relying only on hard-coded rules.

---

## 🔄 Recovery Decision Logic

Recovery actions are intentionally bounded.

Example:

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
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   ├── tools.py
│   │   └── batch_runner.py
│   │
│   ├── rag/
│   │   ├── retriever.py
│   │   ├── grader.py
│   │   └── ...
│   │
│   └── ...
│
├── data/
│   ├── payments.json
│   └── audit_log.json
│
├── frontend/
│   └── app.py
│
├── scripts/
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
