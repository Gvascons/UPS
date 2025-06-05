# Solver Tools - Mode 1 Execution Capabilities
# Provides tools for solution synthesis and validation
# Includes code execution, web search, file operations, and data processing utilities
# Enables the solver to generate, test, and validate working solutions

from typing import List, Dict, Any
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_community.tools import DuckDuckGoSearchRun
import re
import subprocess
import tempfile
import traceback
import os
import sys
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Instantiate the search tool once for reuse
ddgo_search = DuckDuckGoSearchRun(max_results=10)

@tool
def execute_python_code(code: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Execute Python code in an isolated subprocess and capture the output.

    Args:
        code: The Python code to execute as a string
        timeout: Maximum execution time in seconds (default: 60)

    Returns:
        A dictionary containing the execution results and any errors
    """
    # Initialize result structure
    execution_result = {
        "output": "",
        "success": False,
        "timeout": False,
        "code": "",
        "errors": {
            "error": None,
            "traceback": None
        }
    }

    # Extract code from markdown code blocks if present (improved patterns)
    code_patterns = [
        r"```python\s*(.*?)```",  # python specified
        r"```\s*(.*?)```",        # generic code block
    ]
    
    for pattern in code_patterns:
        match = re.search(pattern, code, re.DOTALL)
        if match:
            code = match.group(1).strip()
            break
    
    code = code.strip()
    
    # Validate code is not empty
    if not code:
        execution_result["errors"]["error"] = "No code provided to execute"
        return execution_result

    # Store the processed code in the result
    execution_result["code"] = code

    temp_file_path = None
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code)

        # Execute the code in a separate process
        process = subprocess.Popen(
            [sys.executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            # Wait for the process to complete with timeout
            stdout, stderr = process.communicate(timeout=timeout)

            # Prepare output (combine stdout and stderr if present)
            raw_output = stdout.strip()
            if stderr.strip():
                if raw_output:
                    raw_output += f"\n\nSTDERR:\n{stderr.strip()}"
                else:
                    raw_output = f"STDERR:\n{stderr.strip()}"

            # Check return code to determine success
            if process.returncode != 0:
                # Execution failed
                execution_result["success"] = False
                execution_result["output"] = raw_output
                execution_result["errors"]["error"] = f"Process returned non-zero exit code: {process.returncode}"
                if stderr.strip():
                    execution_result["errors"]["traceback"] = stderr.strip()
            else:
                # Successful execution
                execution_result["output"] = raw_output
                execution_result["success"] = True

        except subprocess.TimeoutExpired:
            process.kill()
            execution_result["timeout"] = True
            execution_result["errors"]["error"] = f"Code execution timed out after {timeout} seconds"
            execution_result["success"] = False

    except Exception as e:
        # Handle any other exceptions
        execution_result["errors"]["error"] = f"{type(e).__name__}: {str(e)}"
        execution_result["errors"]["traceback"] = traceback.format_exc()
        execution_result["success"] = False
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Could not delete temp file {temp_file_path}: {cleanup_error}")

    return execution_result

@tool
def web_search(query: str) -> str:
    """
    Perform a web search using DuckDuckGo for the given query and return the results.
    Useful for finding real-time information, documentation, or answers to specific questions.
    
    Args:
        query: The search query string
        
    Returns:
        Search results as a string
    """
    logger.info(f"Executing web search: {query}")
    
    if not query.strip():
        return "Error: Empty search query provided"
    
    try:
        search_results = ddgo_search.run(query.strip())
        
        # Check if results are empty or uninformative
        if not search_results or "No good DuckDuckGo Search Result was found" in search_results:
            return f"No results found for query: {query}"
        
        # Truncate very long results to avoid overwhelming context
        max_length = 3000
        if len(search_results) > max_length:
            search_results = search_results[:max_length] + "\n\n... (results truncated for brevity)"
            
        return search_results
    except Exception as e:
        logger.error(f"Error during web search for '{query}': {e}")
        return f"Failed to perform web search for query: {query}. Error: {e}"

# Define the tools list with only the essential tools
tools = [
    execute_python_code,
    web_search
]

# Instantiate ToolNode for use in the graph
tool_node = ToolNode(tools)
