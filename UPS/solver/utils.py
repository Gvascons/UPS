# Solver Utilities
# Helper functions for the solver module

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