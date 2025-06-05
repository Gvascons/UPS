# Solver Graph - Mode 1 LangGraph Workflow
# Defines the solution generation workflow structure and node connections
# Creates an iterative pipeline: START → Planner → Agent → Replanner → (loop back to agent or END)

from typing import Literal
from langgraph.graph import StateGraph, START, END
from .schemas import SolverState
from .nodes import planner_node, agent_node, replanner_node

def should_end(state: SolverState) -> Literal["agent", "__end__"]:
    """Determines whether the graph should continue or end."""
    if state.get("response"):
        return END
    elif not state.get("plan"):  # Check if plan is empty or None
        return END
    else:
        return "agent"  # Loop back to agent node

def create_solver():
    """Creates and compiles the Mode 1 Solution Generator."""
    
    # Define the graph state
    builder = StateGraph(SolverState)

    # Add nodes following AI/LLM conventions
    builder.add_node("planner", planner_node)
    builder.add_node("agent", agent_node)
    builder.add_node("replanner", replanner_node)

    # Define edges following reference pattern
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "agent")
    builder.add_edge("agent", "replanner")

    # Conditional edge from replanner (same as reference)
    builder.add_conditional_edges(
        "replanner",
        should_end,
        {
            "agent": "agent",  # Loop back to agent if plan continues
            END: END           # End if response is generated or plan is empty
        }
    )

    # Compile the graph
    graph = builder.compile()
    return graph
