# Evolver Utilities
# Helper functions for the evolver module

def save_graph_image(graph, filename="evolver_graph.png"):
    """Saves a visualization of the evolver graph."""
    try:
        # Ensure you have the necessary extras: pip install pygraphviz
        graph_image = graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(graph_image)
        print(f"Evolver graph visualization saved to {filename}")
    except Exception as e:
        print(f"Could not save evolver graph visualization: {e}. Ensure pygraphviz and its dependencies are installed.") 