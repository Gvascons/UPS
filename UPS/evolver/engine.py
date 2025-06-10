# Evolver - Mode 2 Entry Point
# Superhuman Evolution system that improves solver solutions through systematic mutation
# Implements: Mutate → Evaluate → Select loop for achieving competition-winning performance
# Uses LangGraph workflow for iterative solution improvement

import asyncio
import os
import dotenv
import argparse

# Import necessary components from the evolver package
from .config import EVOLUTION_ROUNDS, ARCHIVE_DIR, GENERATIONS_DIR
from .schemas import EvolverState  
from .graph import create_evolver_graph

# Select LLM provider (for future use when nodes are implemented)
from langchain_anthropic import ChatAnthropic

# Add Langfuse imports
from langfuse.callback import CallbackHandler

# Load environment variables (optional, if API keys are needed)
dotenv.load_dotenv()

# --- Initial State ---
def create_initial_evolver_state(baseline_solution: str, human_baseline_score: float = 0.7) -> EvolverState:
    """Creates the initial state for the evolver graph."""
    return EvolverState(
        # Baseline and Progress
        baseline_solution=baseline_solution,
        current_best=baseline_solution,  # Start with baseline as current best
        current_generation=0,
        
        # Evolution Tracking  
        mutation_history=[],  # Will accumulate (type, result, score) tuples
        solution_archive=[],  # Will store all solutions with metadata
        performance_scores=[human_baseline_score],  # Start with baseline score
        
        # Learning & Memory
        successful_patterns={},  # Learn what mutations work
        failed_approaches={},  # Learn what to avoid
        breakthrough_moments=[],  # Track major improvements
        
        # Control & Completion
        human_baseline_score=human_baseline_score,
        superhuman_achieved=False,
        final_evolved_solution="",  # Will be set when evolution completes
        evolution_complete=False
    )

# --- Main Execution Loop ---
async def run_evolver_graph(initial_state: EvolverState, enable_tracing: bool = False):
    """Runs the evolver graph asynchronously with dummy implementation."""
    
    # Initialize the LLM (for future use when nodes are implemented)
    llm = ChatAnthropic(model="claude-3-7-sonnet-latest")

    # Check if Langfuse tracing should be enabled
    langfuse_handler = None
    if enable_tracing and "LANGFUSE_SECRET_KEY" in os.environ and "LANGFUSE_PUBLIC_KEY" in os.environ:
        print("Langfuse tracing enabled")
        langfuse_handler = CallbackHandler()
        
        config = {
            "configurable": {
                "llm": llm
            },
            "callbacks": [langfuse_handler],
            "recursion_limit": 100  # Lower for evolution workflow
        }
    else:
        if enable_tracing:
            print("Langfuse tracing requested but not available: Missing LANGFUSE_SECRET_KEY or LANGFUSE_PUBLIC_KEY")
        
        config = {
            "configurable": {
                "llm": llm
            },
            "recursion_limit": 100
        }

    # Create the evolver graph instance
    evolver_graph = create_evolver_graph()

    # Variable to store the final state
    final_state = None

    print("--- Starting Evolution Engine ---")
    print(f"🎯 Target: Superhuman performance (>{initial_state['human_baseline_score']:.2f})")
    print(f"📊 Baseline solution length: {len(initial_state['baseline_solution'])} characters")
    print(f"🔄 Max generations: {EVOLUTION_ROUNDS}")
    print("=====================================\n")

    async for step_output in evolver_graph.astream(
        initial_state,
        config=config,
        stream_mode="values"  # Get full state dict at each step
    ):
        # step_output contains the full EvolverState after a node runs
        print(f"\n--- Generation {step_output.get('current_generation', 0)} Step Completed ---")

        # Print current generation progress
        current_gen = step_output.get("current_generation", 0)
        print(f"📈 Generation: {current_gen}/{EVOLUTION_ROUNDS}")

        # Print performance progress
        scores = step_output.get("performance_scores", [])
        if len(scores) > 1:
            latest_score = scores[-1]
            improvement = latest_score - scores[0]
            print(f"🎯 Latest score: {latest_score:.3f} (Δ{improvement:+.3f})")
        
        # Print mutation history summary
        mutations = step_output.get("mutation_history", [])
        if mutations:
            print(f"🧬 Mutations attempted: {len(mutations)}")
            
        # Check for superhuman achievement
        superhuman = step_output.get("superhuman_achieved", False)
        if superhuman:
            print("🏆 SUPERHUMAN PERFORMANCE ACHIEVED!")
            
        # Check if evolution is complete
        evolution_complete = step_output.get("evolution_complete", False)
        if evolution_complete:
            final_solution = step_output.get("final_evolved_solution", "")
            print(f"✅ Evolution complete!")
            print(f"📝 Final solution length: {len(final_solution)} characters")
            print("--- Evolution Engine Finished ---")
        
        print("----------------------------\n")
        
        # Store the current state
        final_state = step_output

    print("--- Evolution Stream Ended ---")

    # Print the final evolution summary
    if final_state:
        print("\n=== EVOLUTION SUMMARY ===")
        
        generations = final_state.get("current_generation", 0)
        mutations = len(final_state.get("mutation_history", []))
        scores = final_state.get("performance_scores", [])
        superhuman = final_state.get("superhuman_achieved", False)
        
        print(f"Generations completed: {generations}")
        print(f"Total mutations attempted: {mutations}")
        
        if len(scores) >= 2:
            improvement = scores[-1] - scores[0]
            print(f"Performance improvement: {improvement:+.3f}")
            
        print(f"Superhuman achieved: {'✅ YES' if superhuman else '❌ NO'}")
        print(f"Human baseline: {final_state.get('human_baseline_score', 0):.3f}")
        
        if scores:
            print(f"Final score: {scores[-1]:.3f}")
            
        print("========================\n")
    else:
        print("\nEvolver did not produce a final state.")

    # Flush Langfuse if tracing was enabled
    if langfuse_handler:
        print("Flushing Langfuse traces...")
        langfuse_handler.flush()


# --- Entry Point ---
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the UPS Mode 2 Evolver")
    parser.add_argument(
        "--baseline_file",
        type=str,
        default="solver_output.txt",
        help="Path to file containing the baseline solution to evolve"
    )
    parser.add_argument(
        "--human_score",
        type=float,
        default=0.7,
        help="Human baseline performance score (0.0-1.0)"
    )
    parser.add_argument(
        "--enable_tracing",
        action="store_true",
        help="Enable Langfuse tracing"
    )
    args = parser.parse_args()
    
    # Ensure directories exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(GENERATIONS_DIR, exist_ok=True)
    print(f"Ensured directories exist: ./{ARCHIVE_DIR}/ and ./{GENERATIONS_DIR}/")

    # --- Load Baseline Solution from File ---
    baseline_file_path = args.baseline_file
    baseline_solution = None
    try:
        with open(baseline_file_path, "r", encoding="utf-8") as f:
            baseline_solution = f.read().strip()
        if not baseline_solution:
            print(f"Error: {baseline_file_path} is empty.")
            exit(1)
        print(f"Loaded baseline solution from ./{baseline_file_path}")
    except FileNotFoundError:
        # Create a dummy baseline for testing if file doesn't exist
        baseline_solution = """
# Dummy Baseline Solution for Testing
def solve_problem():
    # This is a basic solution that works but could be improved
    result = "Hello World"
    return result

# The solution addresses the problem but lacks optimization
print(solve_problem())
        """.strip()
        print(f"File {baseline_file_path} not found. Using dummy baseline solution for testing.")
        
    except Exception as e:
        print(f"Error reading baseline file ./{baseline_file_path}: {e}")
        exit(1)

    # --- Proceed with Evolution ---

    # Create the initial evolver state
    initial_evolver_state = create_initial_evolver_state(
        baseline_solution=baseline_solution,
        human_baseline_score=args.human_score
    )

    # Run the evolver graph
    try:
        print(f"🚀 Starting evolution with human baseline score: {args.human_score}")
        asyncio.run(run_evolver_graph(initial_evolver_state, enable_tracing=args.enable_tracing))

    except Exception as e:
        print(f"\nAn error occurred during evolution: {e}")
        import traceback
        traceback.print_exc() 