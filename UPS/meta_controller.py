# Meta-Controller - System Orchestration
# Manages workflow coordination, resource allocation, and adaptive decision making
# Determines which mode to use based on problem characteristics and user preferences
# Handles state management across different solving approaches

# Meta-Controller: System orchestration, routing, and adaptive decision making
from typing import Dict, Any, Optional
from .config import SolverMode
from .schemas import Problem, Solution, UniversalState 