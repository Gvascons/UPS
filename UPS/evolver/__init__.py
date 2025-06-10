# Evolver Package - Mode 2 Evolution Engine
# Optimizes existing working solutions through evolutionary techniques
# Implements multi-strategy evolution: local optimization, structural mutation, crossover, novelty search
# Manages solution archives and convergence monitoring for continuous improvement

# Mode 2: Evolution Engine

from .graph import create_evolver_graph
from .engine import create_initial_evolver_state, run_evolver_graph

__all__ = [
    "create_evolver_graph",
    "create_initial_evolver_state", 
    "run_evolver_graph"
]
