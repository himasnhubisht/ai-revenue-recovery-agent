from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.nodes import (
    build_query,
    retrieve_knowledge,
    grade_knowledge,
    decision_node,
    fallback_decision,
    execute_action,
    generate_response,
)

def route_after_grading(state):

    if state["relevant"]:
        return "relevant"

    return "not_relevant"


# Create graph
graph_builder = StateGraph(AgentState)


# Nodes
graph_builder.add_node("build_query", build_query)
graph_builder.add_node("retrieve_knowledge", retrieve_knowledge)
graph_builder.add_node("grade_knowledge", grade_knowledge)
graph_builder.add_node("decision", decision_node)
graph_builder.add_node(
    "fallback_decision",
    fallback_decision
)
graph_builder.add_node("execute_action", execute_action)
graph_builder.add_node("generate_response", generate_response)


# Main flow
graph_builder.add_edge(START, "build_query")

graph_builder.add_edge(
    "build_query",
    "retrieve_knowledge"
)

graph_builder.add_edge(
    "retrieve_knowledge",
    "grade_knowledge"
)


# Decide whether retrieved knowledge is useful
graph_builder.add_conditional_edges(
    "grade_knowledge",
    route_after_grading,
    {
        "relevant": "decision",
        "not_relevant": "fallback_decision",
    }
)

# Agent decision → tool → response
graph_builder.add_edge(
    "decision",
    "execute_action"
)

graph_builder.add_edge(
    "execute_action",
    "generate_response"
)

graph_builder.add_edge(
    "generate_response",
    END
)
graph_builder.add_edge(
    "fallback_decision",
    "execute_action"
)


# Compile graph
graph = graph_builder.compile()


# Test
if __name__ == "__main__":

    result = graph.invoke({

        "merchant_id": "techstore",

        "payment_id": "pay_123",

        "amount": 2000,

        "failure_reason": "unknown_error",

        "attempt_count": 2,

    })

    print(result)