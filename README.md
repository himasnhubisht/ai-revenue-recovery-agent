AI Revenue Recovery Agent 💰

An AI-powered payment recovery agent that detects failed payments, retrieves the relevant merchant recovery policy using RAG, makes a bounded recovery decision, executes the appropriate action, and records the result for revenue tracking and auditability.

Problem

Payment failures can cause merchants to lose revenue. Different failure reasons may require different recovery strategies, and merchants may have different retry limits and communication policies.

The goal of this project is to close the loop:

Payment failure → Diagnose → Decide → Recover → Track

What the agent does

When a failed-payment event is received, the system:

Receives the payment failure event through a FastAPI webhook.

Builds a query from the payment context when needed.

Retrieves relevant merchant/global policy documents using RAG.

Grades the retrieved knowledge for relevance.

Makes a bounded recovery decision based on the failure reason and retry count.

Executes the selected recovery tool:

retry

payment_link

escalate

Records the result in an audit log.

Updates revenue-recovery metrics shown in the Streamlit dashboard.

Example

For TechStore:

Failure: insufficient_funds
Attempt: 1
        ↓
Merchant policy retrieved
        ↓
Maximum retries = 2
        ↓
Agent decision: retry
        ↓
Retry tool executed
        ↓
Payment recovered

If the payment has already reached the retry limit:

Failure: insufficient_funds
Attempt: 2
        ↓
Retry limit reached
        ↓
Agent decision: payment_link
        ↓
Payment link generated
        ↓
Status: pending

For an unknown failure reason:

Unknown failure
        ↓
Agent cannot safely apply an automatic recovery policy
        ↓
Agent decision: escalate

Architecture

                    ┌─────────────────────┐
                    │   Payment Event      │
                    │    FastAPI Webhook   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │    Build Query      │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   RAG Retrieval     │
                    │ Merchant + Global   │
                    │     Knowledge       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │  Relevance Grader   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   Agent Decision    │
                    │ retry / link /      │
                    │     escalate        │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   Action Tool       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Audit + Metrics     │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    └─────────────────────┘

Agent workflow

The agent is implemented as a LangGraph state workflow:

START
  ↓
build_query
  ↓
retrieve_knowledge
  ↓
grade_knowledge
  ↓
 ┌───────────────┐
 │ relevant?     │
 └───────┬───────┘
     yes │ no
         │
         ↓
     decision
         ↓
   execute_action
         ↓
        END

If the retrieved knowledge is not relevant, the workflow stops instead of blindly executing a recovery action.

RAG

The knowledge base contains merchant-specific and global payment policies.

Example merchant knowledge:

data/
├── merchants/
│   └── techstore/
│       ├── retry_policy.md
│       └── communication_policy.md
└── global/
    └── payment_error_codes.md

The retrieval layer uses the payment context to find the policies relevant to the specific merchant and failure reason.

The LLM is used where reasoning adds value, including the relevance-grading step. The actual recovery actions are bounded by explicit business rules rather than allowing the model to perform arbitrary actions.

Recovery actions

Retry

Used when the merchant policy allows another automatic retry.

Payment link

Used when automatic retries are exhausted but the payment can still be recovered through customer action.

A generated link is treated as pending revenue, not immediately recovered revenue.

Escalation

Used when the system cannot safely perform an automatic recovery action, such as an unsupported/unknown failure or an exhausted retry path that requires manual review.

Revenue metrics

The dashboard tracks:

Total payments

Revenue at risk

Revenue recovered

Recovery rate

Successful retries

Payment links

Escalations

Payment recovery activity

Audit timestamps

Recovery rate:

Revenue Recovered
----------------- × 100
Revenue At Risk

Tech Stack

Python

FastAPI

LangGraph

LangChain

OpenAI API

RAG / vector retrieval

Streamlit

JSON/Markdown knowledge and audit data

Project Structure

AI_REVENUE_AGENT/
│
├── app/
│   ├── agent/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── graph.py
│   │   ├── tools.py
│   │   └── batch_runner.py
│   │
│   ├── rag/
│   │   ├── retriever.py
│   │   └── grader.py
│   │
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
├── requirements.txt
├── .env
└── README.md

Running locally

1. Create and activate the virtual environment

PowerShell:

.\venv\Scripts\Activate.ps1

2. Configure the OpenAI API key

Create a .env file:

OPENAI_API_KEY=your_api_key_here

Do not commit .env to GitHub.

3. Start FastAPI

python -m uvicorn app.main:app --reload

4. Start Streamlit

Open another terminal, activate the same virtual environment, then run:

python -m streamlit run frontend/app.py

The Streamlit application communicates with the FastAPI webhook and displays the agent's decision and recovery result.

Demo scenarios

Use these scenarios to demonstrate the bounded agent behavior:

Failure

Attempt

Expected action

insufficient_funds

1

retry

insufficient_funds

2

payment_link

unknown_error

2

escalate

bank_timeout

below limit

retry

Example API event

{
  "payment_id": "pay_test",
  "merchant_id": "techstore",
  "amount": 3000,
  "failure_reason": "insufficient_funds",
  "attempt_count": 1
}

The FastAPI webhook passes this event into the agent workflow.

Why this is an agent

This is not simply an API returning a fixed JSON response.

The workflow:

retrieves external knowledge,

evaluates whether that knowledge is relevant,

maintains state across multiple steps,

selects an action based on the payment context and policies,

invokes an action tool,

and records the outcome.

The important distinction is that the LLM does not have unrestricted control over payments. Recovery actions are bounded by explicit business rules and implemented as tools.

Safety and bounded recovery

The system is intentionally conservative:

It respects merchant retry limits.

It does not retry indefinitely.

Unknown cases are escalated.

A generated payment link is not counted as recovered revenue until payment succeeds.

Recovery activity is recorded for auditability.

Future improvements

Possible production extensions include:

Real payment-provider webhooks

Real payment-provider APIs

Customer notification systems

Persistent database storage

Background job scheduling for delayed retries

Authentication and authorization

More merchant policies

Monitoring and alerting

Production deployment

Demo outcome

The project demonstrates the complete recovery loop:

Detect revenue at risk → retrieve policy → make a bounded decision → execute recovery → measure recovered revenue.