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
- Use web search when you need information, research, or examples (save findings to files)
- Use code execution when you need to process data, calculate, implement, or test solutions (save important outputs)
- Plan for data persistence - important results should be saved to files for later steps
- Later steps should build upon files and results from earlier steps
- The final step should produce the complete solution to the problem
- Do not add unnecessary steps - be efficient but thorough
- Make sure each step has all the information needed from previous steps

AVAILABLE TOOLS:
- execute_python_code: Run Python code for calculations, data processing, implementations, testing
- web_search: Search for information, documentation, examples, best practices

Create a logical sequence of steps that will lead to solving the given problem completely.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

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
   - Build upon the results from completed steps (check '{METADATA_DIR}/' for intermediate files)
   - Be specific about what tools to use and mention loading necessary files from previous steps

**CRITICAL:** Only use the `Response` format when the entire task is completely finished and the objective is fully met. If there are still steps needed, you MUST output an updated `Plan`.

**DIRECTORIES:**
- '{METADATA_DIR}/': For intermediate files, tracking, and step-by-step artifacts
- '{OUTPUT_DIR}/': For final deliverable files when explicitly required by the objective

**TOOLS AVAILABLE:**
- execute_python_code: For calculations, data processing, implementations, testing, analysis
- web_search: For research, finding information, documentation, examples

Respond using the appropriate action format (Response or Plan)."""

replanner_prompt = ChatPromptTemplate.from_template(replanner_prompt_template)

# --- Execute Step Prompt (Helper function) ---
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

AVAILABLE TOOLS:
1. **execute_python_code**: Run Python code for calculations, data processing, implementations, analysis, testing
   - Use this for: mathematical calculations, data analysis, algorithm implementation, code testing, file processing
   - Always include proper error handling and clear output/results in your code

2. **web_search**: Search for information, documentation, examples, best practices  
   - Use this for: research, finding documentation, getting examples, learning about techniques
   - Search for specific, relevant terms related to your current task

INSTRUCTIONS FOR THIS TASK:
1. **File Loading:** If you need data/results from previous steps, look for file paths (like '{METADATA_DIR}/step1_research.txt') in the 'Previously Executed Steps' context. Generate code to LOAD from that specific path.

2. **File Saving:** Save your work appropriately:
   - **Intermediate files** (research, analysis, temporary data): Save to '{METADATA_DIR}/' with descriptive names like:
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_research.txt' for research results
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_code.py' for code implementations  
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_data.csv' for data outputs
     - '{METADATA_DIR}/step{len(state.get('past_steps', [])) + 1}_analysis.txt' for analysis results
   
   - **Final deliverables** (if the user explicitly requests output files): Save to '{OUTPUT_DIR}/' with meaningful names like:
     - '{OUTPUT_DIR}/solution.py' for final solution code
     - '{OUTPUT_DIR}/results.csv' for final data deliverables
     - '{OUTPUT_DIR}/report.txt' for final reports

3. **Tool Selection:** Use the appropriate tools based on what the task requires:
   - Need information/research? → Use web_search, then save findings to '{METADATA_DIR}/'
   - Need to implement/calculate/process? → Use execute_python_code, include file I/O as needed

4. **Build on previous results** - refer to the "Previously Executed Steps" for context and load any necessary files from '{METADATA_DIR}/'

5. **Reporting:** When you complete this task, **explicitly mention the file paths** of any files you saved during this task so subsequent steps can find them.

Proceed with your thought process and necessary tool calls to accomplish "{task}"""
