# Evolver Schemas - Mode 2 Data Models
# Simple data structures for superhuman evolution system
# Designed for immediate implementation with architecture for advanced expansion
# Supports systematic improvement toward competition-winning performance

from typing import Annotated, List, Tuple, TypedDict, Optional, Dict, Any
import operator
from pydantic import BaseModel, Field
from enum import Enum

# === CORE EVOLUTION STATE ===
class EvolverState(TypedDict):
    """State for Mode 2 Evolutionary Improvement - designed for superhuman performance"""
    # Baseline and Progress
    baseline_solution: str                                          # Original solver output
    current_best: str                                               # Best solution so far
    current_generation: int                                         # Generation counter
    
    # Evolution Tracking
    mutation_history: Annotated[List[Tuple[str, str, float]], operator.add]  # (type, result, score)
    solution_archive: List[Dict[str, Any]]                          # All solutions with metadata
    performance_scores: List[float]                                 # Quality scores over time
    
    # Learning & Memory (superhuman intelligence)
    successful_patterns: Dict[str, int]                             # What mutations work
    failed_approaches: Dict[str, str]                               # What to avoid and why
    breakthrough_moments: List[str]                                 # Major improvements found
    
    # Control & Completion
    human_baseline_score: float                                     # Human performance to beat
    superhuman_achieved: bool                                       # Whether we surpassed humans
    final_evolved_solution: str                                     # Best solution discovered
    evolution_complete: bool                                        # Whether to stop evolving

# === MUTATION STRATEGIES ===
class MutationType(str, Enum):
    """Types of mutations for systematic improvement"""
    ENHANCE_PROMPTS = "enhance_prompts"                             # Improve instruction clarity
    OPTIMIZE_APPROACH = "optimize_approach"                         # Change methodology
    ADD_REASONING_STEPS = "add_reasoning_steps"                     # Insert analysis phases
    IMPROVE_VALIDATION = "improve_validation"                       # Strengthen verification
    EXPAND_CONTEXT = "expand_context"                               # Add domain knowledge

# === PYDANTIC MODELS FOR STRUCTURED OUTPUT ===
class MutationProposal(BaseModel):
    """Single mutation attempt for systematic improvement"""
    mutation_type: MutationType = Field(description="Type of improvement to apply")
    target_component: str = Field(description="What part of solution to modify")
    modification_description: str = Field(description="Specific changes to make")
    improved_content: str = Field(description="The mutated solution content")
    expected_improvement: str = Field(description="Why this should perform better")
    risk_assessment: str = Field(description="Potential issues or limitations")

class PerformanceEvaluation(BaseModel):
    """Evaluation of a solution's quality toward superhuman performance"""
    accuracy_score: float = Field(ge=0.0, le=1.0, description="Solution correctness (0-1)")
    completeness_score: float = Field(ge=0.0, le=1.0, description="Addresses all requirements (0-1)")
    efficiency_score: float = Field(ge=0.0, le=1.0, description="Resource optimization (0-1)")
    robustness_score: float = Field(ge=0.0, le=1.0, description="Edge case handling (0-1)")
    innovation_score: float = Field(ge=0.0, le=1.0, description="Novel approach quality (0-1)")
    
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted combination of all metrics")
    human_comparison: float = Field(description="Performance vs human baseline (1.0 = equal)")
    is_superhuman: bool = Field(description="Whether this exceeds human performance")
    detailed_feedback: str = Field(description="Specific evaluation commentary")

class EvolutionDecision(BaseModel):
    """Decision on whether to continue evolution or complete with results"""
    continue_evolution: bool = Field(description="Whether to generate more mutations")
    reasoning: str = Field(description="Why continuing or stopping")
    next_focus_areas: Optional[List[str]] = Field(default=None, description="What to improve next")
    superhuman_threshold_met: bool = Field(description="Whether superhuman performance achieved")

class SuperhumanEvolutionReport(BaseModel):
    """Final report on evolution toward superhuman performance"""
    baseline_performance: float = Field(description="Starting solution quality score")
    final_performance: float = Field(description="Best evolved solution quality score")
    improvement_factor: float = Field(description="Multiplicative improvement over baseline")
    human_baseline_comparison: float = Field(description="Performance vs human baseline")
    
    generations_completed: int = Field(description="Total evolution rounds")
    mutations_attempted: int = Field(description="Total mutations tried")
    successful_improvements: int = Field(description="Mutations that improved performance")
    
    breakthrough_discoveries: List[str] = Field(description="Major improvements found")
    most_effective_mutations: List[str] = Field(description="Best-performing mutation types")
    superhuman_achievement: bool = Field(description="Whether superhuman performance reached")
    
    final_solution: str = Field(description="The evolved superhuman solution")
    evolution_summary: str = Field(description="Overall evolution process summary")

# === FUTURE EXPANSION HOOKS ===
# Ready for advanced features when expansion flags are enabled

class AdvancedMutation(BaseModel):
    """For future ADVANCED_MUTATION_ENABLED expansion"""
    strategy_type: str = Field(description="AlphaEvolve strategy used")
    crossover_parents: Optional[List[str]] = Field(default=None, description="Parent solutions combined")
    novelty_vector: Optional[List[float]] = Field(default=None, description="Novelty search direction")

class EnsembleSolution(BaseModel):
    """For future ENSEMBLE_GENERATION_ENABLED expansion"""
    component_solutions: List[str] = Field(description="Individual solutions combined")
    ensemble_method: str = Field(description="How solutions are combined")
    ensemble_performance: float = Field(description="Combined solution quality")

class CompetitionMetrics(BaseModel):
    """For future COMPETITION_MODE expansion"""
    leaderboard_rank: Optional[int] = Field(default=None, description="Kaggle ranking")
    percentile_score: float = Field(description="Competition percentile performance")
    winning_probability: float = Field(description="Estimated chance of victory") 