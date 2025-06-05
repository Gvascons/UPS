# Solver Schemas - Mode 1 Data Models
# Defines data structures for solution generation workflow
# Includes Problem, Solution, SolverState, and structured output models
# Handles state management through the LangGraph workflow

from typing import Annotated, List, Tuple, TypedDict, Union
import operator
from pydantic import BaseModel, Field

# --- State Definition ---
class SolverState(TypedDict):
    """State for the Mode 1 Solution Generator workflow"""
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple[str, str]], operator.add]
    response: str
    content: str

# --- Pydantic Models for Structured Output ---
class Plan(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class Response(BaseModel):
    """Response to user, including final content if applicable."""
    response: str = Field(description="Summary response to the user.")
    content: str | None = Field(default=None, description="The primary output content (e.g., CSV data).")

class Act(BaseModel):
    """Action to perform."""
    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )
