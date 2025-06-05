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
import logging

# Configure logging
logger = logging.getLogger(__name__)


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
        logger.error("No input provided in state")
        raise ValueError("No input provided in state - cannot generate plan")

    # Ensure directories exist for tracking and outputs
    os.makedirs(METADATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        # Use structured output to get a proper Plan object
        planner = planner_prompt | llm.with_structured_output(Plan)
        plan_result = await planner.ainvoke({
            "messages": [HumanMessage(content=state["input"])]
        }, config=config)
        
        # Check if we got valid steps
        if not plan_result or not plan_result.steps:
            logger.warning("Structured output returned empty plan, falling back")
            raise ValueError("Empty plan from structured output")
        
        logger.info(f"Generated plan with {len(plan_result.steps)} steps:")
        for i, step in enumerate(plan_result.steps, 1):
            logger.info(f"  {i}. {step}")
            
        return {"plan": plan_result.steps}
        
    except Exception as e:
        logger.warning(f"Error using structured output for planner: {e}")
        
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
            logger.warning("Plan parsing failed, using default single step")
        
        logger.info(f"Parsed {len(steps)} steps from raw output:")
        for i, step in enumerate(steps, 1):
            logger.info(f"  {i}. {step}")
            
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
        logger.warning("Agent called with empty plan")
        return {"past_steps": [("Execution", "No plan to execute.")]}

    # Get the first task from the plan
    task = plan[0]
    logger.info(f"Agent executing step: {task}")
    
    # Format the task for execution
    task_formatted = format_execute_step_prompt(state)

    # Initialize messages for the ReAct loop
    messages = [HumanMessage(content=task_formatted)]

    # Limit ReAct iterations to prevent infinite loops
    max_iterations = 7
    result = f"Agent stopped after {max_iterations} iterations for task: {task}"

    try:
        for i in range(max_iterations):
            logger.debug(f"ReAct iteration {i+1} for task: {task}")
            
            response = await model_with_tools.ainvoke(messages, config=config)
            
            # Check if LLM returned a valid response
            if response is None:
                logger.error(f"LLM returned None for task: {task}")
                result = "LLM returned no response."
                break

            logger.debug(f"LLM response: {response.content}")
            messages.append(response)

            # Check if LLM wants to use tools
            if not response.tool_calls:
                logger.info(f"Task completed - no tool calls in response: {task}")
                result = response.content  # Use final LLM response as result
                break

            # Execute the requested tools
            tool_names = [tc.get('name', 'N/A') for tc in response.tool_calls]
            logger.info(f"Executing tools: {tool_names}")
            
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
                logger.warning(f"Unexpected tool_node output format: {type(tool_invocation_result)}")
                tool_messages = []

            # Add tool results to conversation
            if not tool_messages:
                logger.warning(f"Tool execution failed or returned no messages for task: {task}")
                # Create error message for missing tool results
                error_tool_call_id = response.tool_calls[0]['id'] if response.tool_calls else 'error_no_tool_call_id'
                error_msg = ToolMessage(
                    content="Tool execution failed or produced no output.", 
                    tool_call_id=error_tool_call_id
                )
                messages.append(error_msg)
            else:
                logger.debug(f"Adding {len(tool_messages)} tool result(s) to conversation")
                messages.extend(tool_messages)

    except Exception as e:
        logger.error(f"Error during agent execution for task '{task}': {e}")
        result = f"Error encountered during execution: {e}"

    # Return the execution result
    logger.info(f"Agent completed task '{task}' with result (capped): {result[:100]}...")
    return {"past_steps": [(task, str(result))]}


async def replanner_node(state: SolverState, config: RunnableConfig) -> dict:
    """
    Evaluates execution progress and decides the next action.
    
    Analyzes the past step results and current plan to determine whether to:
    - Continue with remaining plan steps
    - Modify/replan the approach  
    - Complete the task with a final response
    
    Args:
        state: Current solver state with plan, past_steps, and input
        config: Runtime configuration containing LLM and other settings
        
    Returns:
        Dictionary with either updated plan (continue) or response (complete)
    """
    llm = config["configurable"]["llm"]
    
    # Format execution history for the replanner prompt
    past_steps_formatted = "\n".join(
        f"Step: {task}\nResult: {result}" 
        for task, result in state.get('past_steps', [])
    )
    
    # Format current plan for context
    current_plan_formatted = "\n".join(
        f"{i+1}. {step}" 
        for i, step in enumerate(state.get('plan', []))
    )
    
    # Validate that agent actually executed something
    num_completed = len(state.get('past_steps', []))
    if num_completed == 0:
        logger.error("Replanner called but no steps were executed by agent")
        return {
            "response": "Error: No execution results to evaluate",
            "content": "",
            "plan": []
        }
    
    logger.info(f"Replanner evaluating progress with {num_completed} completed steps")
    logger.debug(f"Past steps: {past_steps_formatted}")
    logger.debug(f"Current plan: {current_plan_formatted}")

    try:
        # Use structured output to get Action decision
        replanner = replanner_prompt | llm.with_structured_output(Act)
        output = await replanner.ainvoke({
            "input": state["input"],
            "plan": current_plan_formatted,
            "past_steps": past_steps_formatted,
        }, config=config)

        # Process the action decision
        if isinstance(output.action, Response):
            # Task is complete - return final response
            final_content = output.action.content if output.action.content is not None else ""
            logger.info("Replanner decided task is complete")
            logger.debug(f"Final response: {output.action.response}")
            
            return {
                "response": output.action.response,
                "content": final_content,
                "plan": []  # Clear plan to signal completion
            }
            
        elif isinstance(output.action, Plan):
            # Continue with new/modified plan
            new_plan = output.action.steps
            logger.info(f"Replanner created new plan with {len(new_plan)} steps:")
            for i, step in enumerate(new_plan, 1):
                logger.info(f"  {i}. {step}")
                
            return {"plan": new_plan}
            
        else:
            # Unexpected action type - handle gracefully
            logger.error(f"Unexpected action type from replanner: {type(output.action)}")
            return {
                "plan": [], 
                "response": "Replanning failed due to unexpected output format.", 
                "content": ""
            }

    except Exception as e:
        logger.error(f"Error during replanning: {e}")
        # End gracefully when replanner fails - don't try to be too smart
        return {
            "response": f"Task incomplete due to replanning error: {e}",
            "content": "",
            "plan": []
        }
