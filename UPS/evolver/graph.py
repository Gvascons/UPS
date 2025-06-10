# Evolver Graph - Mode 2 LangGraph Workflow
# Defines the evolutionary workflow for achieving superhuman performance
# Creates an iterative pipeline: START → Mutator → Evaluator → Selector → (loop or END)
# Architecture is designed to be extensible for advanced strategies

from typing import Literal
from langgraph.graph import StateGraph, START, END
from .schemas import EvolverState
from .nodes import mutator_node, evaluator_node, selector_node
from .config import EVOLUTION_ROUNDS

def should_continue_evolution(state: EvolverState) -> Literal["mutator", "__end__"]:
    """
    Determines whether the evolution process should continue for another generation.
    
    Checks for two conditions to stop:
    1. The `evolution_complete` flag is explicitly set to True by a node.
    2. The maximum number of generations has been reached.
    """
    if state.get("evolution_complete", False):
        print("🛑 Evolution complete flag is set. Ending workflow.")
        return END
    
    if state.get("current_generation", 0) >= EVOLUTION_ROUNDS:
        print(f"🛑 Reached max generations ({EVOLUTION_ROUNDS}). Ending workflow.")
        return END
        
    print("✅ Conditions met to continue evolution. Looping to mutator.")
    return "mutator"

def create_evolver_graph():
    """
    Creates and compiles the Mode 2 Superhuman Evolution graph.
    
    The graph follows a systematic loop:
    1.  **Mutator**: Generates new solution candidates.
    2.  **Evaluator**: Scores the new candidates against performance criteria.
    3.  **Selector**: Updates the archive, identifies the new best solution, and decides if the process should end.
    """
    
    # Define the state machine for the evolution process
    builder = StateGraph(EvolverState)

    # Add the core nodes of the evolutionary pipeline
    builder.add_node("mutator", mutator_node)          # Generate new solutions
    builder.add_node("evaluator", evaluator_node)      # Score the solutions
    builder.add_node("selector", selector_node)        # Select the best and decide what's next

    # Define the workflow edges
    builder.add_edge(START, "mutator")
    builder.add_edge("mutator", "evaluator")
    builder.add_edge("evaluator", "selector")

    # The conditional edge creates the evolutionary loop
    builder.add_conditional_edges(
        "selector",
        should_continue_evolution,
        {
            "mutator": "mutator",  # Loop back for the next generation
            END: END               # End the evolution process
        }
    )

    # Compile the graph into a runnable workflow
    graph = builder.compile()
    print("✅ Evolver graph compiled successfully.")
    return graph 