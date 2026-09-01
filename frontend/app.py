import json
from pathlib import Path

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/webhook/payment-failed"
AUDIT_FILE = Path("data/audit_log.json")


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Revenue Recovery Agent",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI Revenue Recovery Agent")
st.caption("AI-powered payment recovery for merchants")


# =========================================================
# LOAD AUDIT LOG
# =========================================================

def load_audit_logs():

    if not AUDIT_FILE.exists():
        return []

    with open(AUDIT_FILE, "r") as file:

        try:
            return json.load(file)

        except json.JSONDecodeError:
            return []


# =========================================================
# PROCESS PAYMENT
# =========================================================

st.sidebar.header("Simulate Payment Failure")


payment_id = st.sidebar.text_input(
    "Payment ID",
    "pay_demo_001"
)


merchant_id = st.sidebar.text_input(
    "Merchant ID",
    "techstore"
)


amount = st.sidebar.number_input(
    "Amount",
    min_value=1,
    value=3000
)


failure_reason = st.sidebar.selectbox(
    "Failure Reason",
    [
        "insufficient_funds",
        "card_declined",
        "bank_timeout",
        "unknown_error"
    ]
)


attempt_count = st.sidebar.number_input(
    "Attempt Count",
    min_value=0,
    value=1
)


# =========================================================
# SEND PAYMENT TO AGENT
# =========================================================

if st.sidebar.button("🚀 Process Payment"):

    payment = {

        "payment_id": payment_id,

        "merchant_id": merchant_id,

        "amount": amount,

        "failure_reason": failure_reason,

        "attempt_count": attempt_count

    }

    try:

        response = requests.post(
            API_URL,
            json=payment,
            timeout=120
        )


        if response.status_code == 200:

            result = response.json()


            # Show the actual outcome of the recovery action
            status = result.get("status", "unknown")

            if status == "success":
                st.success("Recovery action completed successfully!")
            elif status == "pending":
                st.warning("Recovery action is pending.")
            elif status == "escalated":
                st.warning("Payment has been escalated for manual review.")
            else:
                st.error("Recovery action failed.")


            # =================================================
            # AGENT DECISION
            # =================================================

            st.subheader("🤖 Agent Decision")


            col1, col2, col3 = st.columns(3)


            col1.metric(
                "Action",
                result.get(
                    "action",
                    "N/A"
                )
            )


            col2.metric(
                "Status",
                result.get(
                    "status",
                    "N/A"
                )
            )


            col3.metric(
                "Recovered",
                f"₹{result.get('amount_recovered', 0):,.0f}"
            )


            # =================================================
            # DECISION REASON
            # =================================================

            decision_reason = result.get(
                "decision_reason"
            )


            if decision_reason:

                st.subheader(
                    "🧠 Why did the agent choose this?"
                )

                st.info(
                    decision_reason
                )


            # =================================================
            # ACTION MESSAGE
            # =================================================

            message = result.get(
                "message"
            )


            if message:

                if result.get("status") == "success":

                    st.success(message)

                elif result.get("status") == "escalated":

                    st.warning(message)

                else:

                    st.info(message)


        else:

            st.error(
                f"API Error: {response.status_code}"
            )


    except requests.exceptions.RequestException as e:

        st.error(
            "Could not connect to FastAPI."
        )

        st.code(
            str(e)
        )


# =========================================================
# DASHBOARD
# =========================================================

logs = load_audit_logs()


if not logs:

    st.warning(
        "No payment events processed yet."
    )


else:

    # =====================================================
    # CALCULATE METRICS
    # =====================================================

    total_payments = len(logs)


    total_at_risk = sum(
        log.get("amount", 0)
        for log in logs
    )


    total_recovered = sum(
        log.get("amount_recovered", 0)
        for log in logs
    )


    recovery_rate = 0


    if total_at_risk > 0:

        recovery_rate = (
            total_recovered /
            total_at_risk
        ) * 100


    successful_retries = sum(
        1
        for log in logs

        if log.get("action") == "retry"
        and log.get("status") == "success"
    )


    failed_retries = sum(
        1
        for log in logs

        if log.get("action") == "retry"
        and log.get("status") == "failed"
    )


    payment_links = sum(
        1
        for log in logs

        if log.get("action") == "payment_link"
    )


    escalations = sum(
        1
        for log in logs

        if log.get("action") == "escalate"
    )


    # =====================================================
    # REVENUE OVERVIEW
    # =====================================================

    st.divider()

    st.subheader(
        "📊 Revenue Overview"
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Payments",
        total_payments
    )


    col2.metric(
        "Revenue At Risk",
        f"₹{total_at_risk:,.0f}"
    )


    col3.metric(
        "Revenue Recovered",
        f"₹{total_recovered:,.0f}"
    )


    col4.metric(
        "Recovery Rate",
        f"{recovery_rate:.2f}%"
    )


    # =====================================================
    # AGENT ACTIVITY
    # =====================================================

    st.divider()

    st.subheader(
        "🤖 Agent Activity"
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Successful Retries",
        successful_retries
    )


    col2.metric(
        "Failed Retries",
        failed_retries
    )


    col3.metric(
        "Payment Links",
        payment_links
    )


    col4.metric(
        "Escalations",
        escalations
    )


    # =====================================================
    # RECOVERY ACTION CHART
    # =====================================================

    st.divider()

    st.subheader(
        "📈 Recovery Actions"
    )


    action_counts = {

        "Retry": successful_retries,

        "Payment Link": payment_links,

        "Escalation": escalations

    }


    st.bar_chart(
        action_counts
    )


    # =====================================================
    # FILTERS
    # =====================================================

    st.divider()

    st.subheader(
        "🔎 Filter Payments"
    )


    filter_col1, filter_col2 = st.columns(2)


    with filter_col1:

        action_filter = st.selectbox(
            "Action",
            [
                "All",
                "retry",
                "payment_link",
                "escalate"
            ]
        )


    with filter_col2:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "success",
                "failed",
                "pending",
                "escalated"
            ]
        )


    filtered_logs = logs


    if action_filter != "All":

        filtered_logs = [
            log
            for log in filtered_logs
            if log.get("action") == action_filter
        ]


    if status_filter != "All":

        filtered_logs = [
            log
            for log in filtered_logs
            if log.get("status") == status_filter
        ]


    # =====================================================
    # PAYMENT TABLE
    # =====================================================

    st.divider()

    st.subheader(
        "📋 Payment Recovery Activity"
    )


    table_data = []


    for log in reversed(filtered_logs):

        table_data.append({

            "Payment ID":
                log.get(
                    "payment_id"
                ),

            "Merchant":
                log.get(
                    "merchant_id"
                ),

            "Amount":
                f"₹{log.get('amount', 0):,.0f}",

            "Failure":
                log.get(
                    "failure_reason"
                ),

            "Action":
                log.get(
                    "action"
                ),

            "Status":
                log.get(
                    "status"
                ),

            "Recovered":
                f"₹{log.get('amount_recovered', 0):,.0f}",

            "Time":
                log.get(
                    "timestamp"
                )

        })


    if table_data:

        st.dataframe(
            table_data,
            use_container_width=True
        )

    else:

        st.info(
            "No payments match the selected filters."
        )