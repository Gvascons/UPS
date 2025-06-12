# Solver Utilities
# Helper functions for the solver module

from .schemas import SolverState

# --- Initial State ---
def create_initial_state(user_input: str) -> SolverState:
    """Creates the initial state for the solver graph."""
    return SolverState(
        input=user_input,  # User input
        plan=[],  # Initialize plan as empty list
        past_steps=[],  # Initialize past_steps as empty list
        response="",  # Initialize response as empty string
        content="",  # Initialize content as empty string
    )

def save_graph_image(graph, filename="solver_graph.png"):
    """Saves a visualization of the solver graph."""
    try:
        # Ensure you have the necessary extras: pip install pygraphviz
        graph_image = graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(graph_image)
        print(f"Solver graph visualization saved to {filename}")
    except Exception as e:
        print(f"Could not save solver graph visualization: {e}. Ensure pygraphviz and its dependencies are installed.") 