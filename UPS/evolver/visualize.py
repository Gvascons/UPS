# Temporary script to visualize the evolver graph.
# To run from the project root (UPS/UPS/):
# python -m evolver.visualize

from .graph import create_evolver_graph
from .utils import save_graph_image

if __name__ == "__main__":
    print("Attempting to generate evolver graph visualization...")
    
    # Create the graph instance
    evolver_graph = create_evolver_graph()
    
    # Define the output path, which will be the project root.
    output_filename = "evolver_graph_visualization.png"
    
    # Save the graph image
    save_graph_image(evolver_graph, output_filename)
    
    print(f"\nGraph visualization should be saved as '{output_filename}' in your project's root directory.")
    print("If the file was not created, please check for errors above.")
    print("You might need to install graphviz on your system and the pygraphviz library:")
    print("pip install pygraphviz") 