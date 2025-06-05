# Solver - Mode 1 Entry Point
# Solution Generation system that creates working solutions from scratch
# Implements: Problem Analysis → Task Planning → Solution Synthesis → Validation → Output Formatting
# Uses LangGraph workflow for systematic solution development

import asyncio
import os
import dotenv
import argparse

# Import necessary components from the solver package
from .config import OUTPUT_DIR, METADATA_DIR
from .schemas import SolverState
from .graph import create_solver
from .utils import save_graph_image

# Select LLM provider
from langchain_anthropic import ChatAnthropic
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI

# Add Langfuse imports
from langfuse.callback import CallbackHandler

# Load environment variables (optional, if API keys are needed)
dotenv.load_dotenv()

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

# --- Main Execution Loop ---
async def run_graph(initial_state: SolverState, enable_tracing: bool = False, render_graph: bool = False):
    """Runs the solver graph asynchronously."""
    # Initialize the LLM (Choose one)
    # llm = ChatOpenAI(model="gpt-4o-mini")
    llm = ChatAnthropic(model="claude-3-7-sonnet-latest")
    # llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Check if Langfuse tracing should be enabled
    langfuse_handler = None
    if enable_tracing and "LANGFUSE_SECRET_KEY" in os.environ and "LANGFUSE_PUBLIC_KEY" in os.environ:
        print("Langfuse tracing enabled")
        langfuse_handler = CallbackHandler()
        
        # Configuration with tracing
        config = {
            "configurable": {
                "llm": llm
            },
            "callbacks": [langfuse_handler],
            "recursion_limit": 250  # Adjust as needed
        }
    else:
        if enable_tracing:
            print("Langfuse tracing requested but not available: Missing LANGFUSE_SECRET_KEY or LANGFUSE_PUBLIC_KEY")
        
        # Configuration without tracing
        config = {
            "configurable": {
                "llm": llm
            },
            "recursion_limit": 250  # Adjust as needed
        }

    # Create the graph instance inside the async function
    solver_graph = create_solver()

    # Save the graph to a file (optional)
    if render_graph:
        save_graph_image(solver_graph)
        print("Graph visualization saved to solver_graph.png")

    # Variable to store the final state
    final_state = None

    print("--- Starting Solver Execution ---")
    async for step_output in solver_graph.astream(
        initial_state,
        config=config,
        stream_mode="values"  # "values" gives the full state dict at each step
    ):
        # step_output contains the full SolverState dictionary after a node runs
        print("\n--- Solver Step Completed ---")

        # Print current plan
        current_plan = step_output.get("plan", [])
        print(f"Current Plan: {current_plan if current_plan else '[]'}")

        # Print the last executed step and its result, if any
        past_steps = step_output.get("past_steps", [])
        if past_steps:
            print(f"Last Action Result: {past_steps[-1]}")
        else:
            print("Last Action Result: None")

        # Print final response if it exists
        final_response = step_output.get("response")
        if final_response:
            print(f"Final Response: {final_response}")
            print("--- Solver Execution Finished ---")
        else:
            print("Final Response: None")

        print("----------------------------\n")
        # Add a small delay if needed for readability or rate limits
        # await asyncio.sleep(0.1)

        # Store the current state as the latest state
        final_state = step_output

    print("--- Solver Stream Ended ---")

    # Print the final state after the stream is finished
    if final_state:
        print("\n=== FINAL STATE ===")
        import pprint
        pprint.pprint(final_state)
        print("===================\n")
    else:
        print("\nSolver did not produce a final state.")

    # Flush Langfuse if tracing was enabled
    if langfuse_handler:
        print("Flushing Langfuse traces...")
        langfuse_handler.flush()


# --- Entry Point ---
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the UPS Mode 1 Solver")
    parser.add_argument(
        "--input_file",
        type=str,
        default="context.txt",
        help="Path to input file containing the user prompt"
    )
    # Add argument for enabling Langfuse tracing
    parser.add_argument(
        "--enable_tracing",
        action="store_true",
        help="Enable Langfuse tracing"
    )
    # Add argument for enabling graph rendering
    parser.add_argument(
        "--render",
        action="store_true",
        help="Enable graph visualization rendering"
    )
    args = parser.parse_args()
    
    # Ensure both directories exist (relative to CWD)
    os.makedirs(METADATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Ensured directories exist: ./{METADATA_DIR}/ and ./{OUTPUT_DIR}/")

    # --- Load User Input from File ---
    prompt_file_path = args.input_file  # Use the provided input file path
    user_prompt = None
    try:
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            user_prompt = f.read().strip()
        if not user_prompt:
            print(f"Error: {prompt_file_path} is empty.")
            exit(1)
        print(f"Loaded user prompt from ./{prompt_file_path}")
    except FileNotFoundError:
        print(f"Error: Prompt file not found at ./{prompt_file_path}")
        print("Please create a file named 'context.txt' in the directory where you run the script and place your prompt inside it.")
        exit(1)
    except Exception as e:
        print(f"Error reading prompt file ./{prompt_file_path}: {e}")
        exit(1)

    # --- Proceed if prompt was loaded successfully ---

    # Create the initial state
    initial_solver_state = create_initial_state(user_prompt)

    # Run the solver graph
    try:
        # Use asyncio.run() to execute the async function with tracing and rendering if enabled
        asyncio.run(run_graph(initial_solver_state, enable_tracing=args.enable_tracing, render_graph=args.render))

    except Exception as e:
        print(f"\nAn error occurred during solver execution: {e}")
        # Consider adding more detailed error logging or traceback here
        import traceback
        traceback.print_exc()
