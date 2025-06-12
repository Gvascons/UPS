# Solver Prompts - Mode 1 System Instructions
# Contains specialized prompts for each stage of solution generation
# Provides context-aware instructions for problem analysis, planning, synthesis, validation, and formatting
# Ensures consistent, high-quality output from LLM at each workflow step

from langchain_core.prompts import ChatPromptTemplate
from .config import OUTPUT_DIR, METADATA_DIR

# --- Planner Prompt ---
planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert problem solver. For the given objective, create a simple step-by-step plan to solve the problem completely.

INSTRUCTIONS:
- Break down the problem into clear, actionable steps
- Each step should be specific and achievable
- The final step should produce the complete solution to the problem
- Make sure each step has all the information needed from previous steps

Create a logical sequence of steps that will lead to solving the given problem completely.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

# --- Execute Step Prompt (Helper function/tool call) ---
def format_execute_step_prompt(state: dict) -> str:
    """Formats the prompt for the agent_node execution."""
    plan = state.get('plan', [])
    task = plan[0] if plan else "No task found"
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    past_steps_str = "\n".join(f"Step: {t}\nResult: {r}" for t, r in state.get('past_steps', []))

    return f"""CONTEXT:
Original User Request: {state.get('input', 'N/A')}

Full Plan:
{plan_str}

Working Directories:
- '{METADATA_DIR}/': For intermediate files, tracking, and step-by-step artifacts
- '{OUTPUT_DIR}/': For final deliverable files when explicitly required

Previously Executed Steps and Results:
{past_steps_str if past_steps_str else 'None'}

CURRENT TASK:
You are tasked with executing step {len(state.get('past_steps', [])) + 1}: "{task}"
Think step-by-step to achieve this task. Use the available tools when necessary.

INSTRUCTIONS FOR THIS TASK:
1. **File Loading:** If you need data/results from previous steps, look for file paths (like '{METADATA_DIR}/step1_research.txt') in the 'Previously Executed Steps' context. Generate code to LOAD from that specific path.

2. **File Saving:** If you generate important outputs (dataframes, models), generate code to SAVE them appropriately:
   - **Intermediate files** (research, analysis, temporary data): Save to '{METADATA_DIR}/' with descriptive names like:
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_research.txt' for research results
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_code.py' for code implementations  
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_data.csv' for data outputs
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_analysis.txt' for analysis results
   
   - **Final deliverables** (if the user explicitly requests output files): Save to '{OUTPUT_DIR}/' with meaningful names like:
     - '{OUTPUT_DIR}/solution.py' for final solution code
     - '{OUTPUT_DIR}/results.csv' for final data deliverables
     - '{OUTPUT_DIR}/report.txt' for final reports

3. **Reporting:** When you have the final result or confirmation for THIS task (after all necessary tool calls, if any), **explicitly mention the file paths**(e.g., '{OUTPUT_DIR}/final_data.csv') of any files you saved during this task so subsequent steps can find them.

Proceed with your thought process and necessary tool calls to accomplish "{task}"""

# --- Replanner Prompt ---
replanner_prompt_template = f"""Review the user's objective, the original plan, and the results of the steps executed so far. Decide the next course of action.

User Objective: {{input}}

Original Plan:
{{plan}}

Executed Steps and Results (may include file paths for saved artifacts):
{{past_steps}}

**Your Decision Process:**

1. **Check Completion:** Has the *entire* User Objective '{{input}}' been fully satisfied by the executed steps and results?

2. **If YES (Objective Fully Met):** 
   - Generate the final answer using the `Response` format
   - In the `response` field: Provide a clear summary of how the objective was accomplished and mention any final output files (e.g., '{OUTPUT_DIR}/solution.py', '{OUTPUT_DIR}/results.csv')
   - In the `content` field: Include the main solution, result, or output. If final deliverable files were created in '{OUTPUT_DIR}/', include the most important content or reference the file paths
   - Do NOT ask if you should proceed - the task is complete

3. **If NO (Objective NOT Fully Met):**
   - Generate an updated plan using the `Plan` format
   - This plan MUST contain only the **remaining specific steps** needed to achieve the objective
   - Do NOT include steps already completed successfully

**CRITICAL:** Only use the `Response` format when the entire task is completely finished and the objective is fully met. If there are still steps needed, you MUST output an updated `Plan`.

Respond using the appropriate action format (Response or Plan)."""

replanner_prompt = ChatPromptTemplate.from_template(replanner_prompt_template)
