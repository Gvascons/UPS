# Solver Nodes - Mode 1 LangGraph Components
# Individual processing steps in the solution generation workflow
# Each node performs a specific task: analyze, plan, synthesize, validate, format
# Connected through LangGraph to form a systematic problem-solving pipeline

from typing import Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, ToolMessage
from .schemas import SolverState, Plan, Response, Act
from .prompts import planner_prompt, format_execute_step_prompt, replanner_prompt
from .tools import tools, tool_node
from .config import METADATA_DIR, OUTPUT_DIR
import os


async def planner_node(state: SolverState, config: RunnableConfig) -> dict:
    """
    Generates an initial plan for solving the given problem.
    
    Creates a structured approach by breaking down the problem into actionable steps
    that can be executed by the agent node using available tools.
    
    Args:
        state: Current solver state containing the problem description
        config: Runtime configuration containing LLM and other settings
        
    Returns:
        Dictionary with updated plan steps
    """
    llm = config["configurable"]["llm"]
    
    # Validate input
    if not state.get("input"):
        print("ERROR: No input provided in state")
        raise ValueError("No input provided in state - cannot generate plan")

    try:
        # Use structured output to get a proper Plan object
        planner = planner_prompt | llm.with_structured_output(Plan)
        plan_result = await planner.ainvoke({
            "messages": [HumanMessage(content=state["input"])]
        }, config=config)
        
        # Check if we got valid steps
        if not plan_result or not plan_result.steps:
            print("WARNING: Structured output returned empty plan, falling back")
            raise ValueError("Empty plan from structured output")
            
        return {"plan": plan_result.steps}
        
    except Exception as e:
        print(f"WARNING: Error using structured output for planner: {e}")
        
        # Fallback to raw output and manual parsing
        planner = planner_prompt | llm
        raw_result = await planner.ainvoke({
            "messages": [HumanMessage(content=state["input"])]
        }, config=config)

        # Parse numbered list from raw content
        content = raw_result.content if hasattr(raw_result, 'content') else str(raw_result)
        steps = []
        
        for line in content.split('\n'):
            line = line.strip()
            # Look for numbered list items like "1. ", "2. ", etc.
            if line and len(line) > 3 and line[0].isdigit() and '. ' in line[:5]:
                step_text = line.split('. ', 1)[1]
                if step_text:  # Only add non-empty steps
                    steps.append(step_text)

        if not steps:
            # If parsing failed, create a default single step
            steps = [f"Solve the problem: {state['input']}"]
            print("WARNING: Plan parsing failed, using default single step")
            
        return {"plan": steps}


async def agent_node(state: SolverState, config: RunnableConfig) -> dict:
    """
    Executes the first step of the current plan using available tools.
    
    Uses a ReAct pattern where the LLM can iteratively use tools to complete the task.
    The agent will continue until the step is complete or max iterations are reached.
    
    Args:
        state: Current solver state containing plan and past steps
        config: Runtime configuration containing LLM and other settings
        
    Returns:
        Dictionary with updated past_steps containing the execution result
    """
    llm = config["configurable"]["llm"]
    model_with_tools = llm.bind_tools(tools)

    plan = state.get("plan", [])
    if not plan:
        print("WARNING: Agent called with empty plan")
        return {"past_steps": [("Execution", "No plan to execute.")]}

    # Get the first task from the plan
    task = plan[0]
        
    # Format the task for execution
    task_formatted = format_execute_step_prompt(state)

    # Initialize messages for the ReAct loop
    messages = [HumanMessage(content=task_formatted)]

    # Limit ReAct iterations to prevent infinite loops
    max_iterations = 7
    result = f"Agent stopped after {max_iterations} iterations for task: {task}"

    try:
        for i in range(max_iterations):
            print(f"ReAct iteration {i+1} for task: {task}")
            
            response = await model_with_tools.ainvoke(messages, config=config)
            
            # Check if LLM returned a valid response
            if response is None:
                print(f"ERROR: LLM returned None for task: {task}")
                result = "LLM returned no response."
                break
            
            # Show the full LLM reasoning
            if hasattr(response, 'content') and response.content:
                if isinstance(response.content, str):
                    print(f"\nLLM Reasoning: {response.content}")
                elif isinstance(response.content, list):
                    print(f"\nLLM Reasoning (structured):")
                    for i, item in enumerate(response.content):
                        print(f"  Part {i+1}: {item}")
                else:
                    print(f"\nLLM Reasoning (raw): {response.content}")
            else:
                print("\nLLM Reasoning: [No reasoning provided - LLM sent only tool calls]")
            
            messages.append(response)

            # Check if LLM wants to use tools
            if not response.tool_calls:
                print(f"Task completed - no tool calls requested")
                result = response.content if response.content else "Task completed without explicit reasoning."
                break

            # Execute the requested tools
            tool_names = [tc.get('name', 'N/A') for tc in response.tool_calls]
            print(f"\nExecuting tools: {tool_names}")
            
            tool_invocation_result = await tool_node.ainvoke({"messages": [response]}, config=config)

            # Handle different tool_node output formats
            tool_messages = []
            if isinstance(tool_invocation_result, ToolMessage):
                tool_messages = [tool_invocation_result]
            elif isinstance(tool_invocation_result, list) and all(isinstance(m, ToolMessage) for m in tool_invocation_result):
                tool_messages = tool_invocation_result
            elif isinstance(tool_invocation_result, dict) and "messages" in tool_invocation_result:
                tool_messages = tool_invocation_result.get("messages", [])
            else:
                print(f"WARNING: Unexpected tool_node output format: {type(tool_invocation_result)}")
                tool_messages = []

            # Add tool results to conversation
            if not tool_messages:
                print(f"WARNING: Tool execution failed or returned no messages for task: {task}")
                # Create error message for missing tool results
                error_tool_call_id = response.tool_calls[0]['id'] if response.tool_calls else 'error_no_tool_call_id'
                error_msg = ToolMessage(
                    content="Tool execution failed or produced no output.", 
                    tool_call_id=error_tool_call_id
                )
                messages.append(error_msg)
            else:
                print("\nTool Results:")
                for idx, msg in enumerate(tool_messages, 1):
                    # Show success/failure status for code execution
                    if 'execute_python_code' in tool_names:
                        try:
                            import json
                            result_data = json.loads(msg.content)
                            if result_data.get('success'):
                                output = result_data.get('output', '').strip()
                                if output:
                                    print(f"  ✓ Code executed successfully:")
                                    print(f"    Output: {output}")
                                else:
                                    print(f"  ⚠ Code executed successfully but produced no output")
                                    print(f"    Hint: Add print() statements to see results")
                                    # Add a helpful message to the LLM
                                    enhanced_msg = ToolMessage(
                                        content=json.dumps({
                                            **result_data,
                                            "output": "Code executed successfully but produced no visible output. Consider adding print() statements to display results, variables, or return values so you can see what happened."
                                        }),
                                        tool_call_id=msg.tool_call_id
                                    )
                                    tool_messages[idx-1] = enhanced_msg
                            else:
                                print(f"  ✗ Code execution failed:")
                                if result_data.get('errors', {}).get('error'):
                                    print(f"    Error: {result_data['errors']['error']}")
                                if result_data.get('errors', {}).get('traceback'):
                                    print(f"    Traceback: {result_data['errors']['traceback']}")
                        except Exception as parse_error:
                            print(f"  Tool Result {idx} (raw): {msg.content}")
                            print(f"  Parse error: {parse_error}")
                    else:
                        print(f"  Tool Result {idx}: {msg.content}")
                messages.extend(tool_messages)
            
            print()  # Add spacing between iterations

    except Exception as e:
        print(f"ERROR: Error during agent execution for task '{task}': {e}\n")
        result = f"Error encountered during execution: {e}"

    # Return the execution result
    print(f"INFO: Agent completed task '{task}' with result (capped): {result[:100]}...\n")
    return {"past_steps": [(task, str(result))]}


async def replanner_node(state: SolverState, config: RunnableConfig) -> dict:
    """
    Evaluates progress and decides whether to continue with a new plan or provide final response.
    """
    num_completed = len(state.get('past_steps', []))
    if num_completed == 0:
        print("ERROR: Replanner called but no steps were executed by agent")
        return {
            "response": "Error: No execution results to evaluate",
            "content": "",
            "plan": []
        }
    
    print(f"Replanner evaluating progress ({num_completed} completed steps)")

    try:
        # Format the past steps and current plan for the LLM
        past_steps_formatted = "\n".join([
            f"Step: {step}\nResult: {result}" 
            for step, result in state.get('past_steps', [])
        ])
        
        current_plan_formatted = "\n".join([
            f"{i+1}. {step}" 
            for i, step in enumerate(state.get('plan', []))
        ])

        # Get LLM decision on next action
        llm = config["configurable"]["llm"]
        replanner_chain = replanner_prompt | llm.with_structured_output(Act)
        
        output = await replanner_chain.ainvoke({
            "input": state.get("input", ""),
            "plan": current_plan_formatted,
            "past_steps": past_steps_formatted
        }, config=config)

        if isinstance(output.action, Response):
            # Task is complete - return final response
            final_content = output.action.content if output.action.content is not None else ""
            print("✓ Task completed - generating final response")
            
            return {
                "response": output.action.response,
                "content": final_content,
                "plan": []  # Clear plan to signal completion
            }
        elif isinstance(output.action, Plan):
            # Continue with new/modified plan
            new_plan = output.action.steps
            print(f"→ Continuing with updated plan ({len(new_plan)} steps)")
            
            return {
                "plan": new_plan,
                "content": "",
                "response": None
            }
        else:
            # Unexpected action type - handle gracefully
            print(f"ERROR: Unexpected action type from replanner: {type(output.action)}")
            return {
                "plan": [], 
                "content": "",
                "response": "Error: Replanner returned unexpected action type"
            }

    except Exception as e:
        print(f"ERROR: Error during replanning: {e}")
        # End gracefully when replanner fails - don't try to be too smart
        return {
            "plan": [],
            "content": "",
            "response": f"Error during replanning: {e}"
        }
