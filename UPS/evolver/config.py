# Evolver Configuration - Mode 2 Settings
# Evolutionary system designed to surpass human performance through systematic improvement
# Architecture supports scaling from basic mutations to advanced competition-winning strategies
# Goal: Transform solver output into superhuman-quality solutions

# === CORE EVOLUTION ENGINE ===
# Immediate implementation - basic but functional
EVOLUTION_ROUNDS = 15                    # Sufficient for meaningful evolution
POPULATION_SIZE = 8                      # Manageable but diverse
MUTATIONS_PER_ROUND = 5                  # Multiple attempts per generation
ELITE_PRESERVATION = 2                   # Keep best solutions

# === MUTATION STRATEGIES ===
# Current: Simple mutations / Future: Advanced AlphaEvolve strategies
MUTATION_TYPES = [
    "enhance_prompts",                   # Improve instruction clarity and specificity
    "optimize_approach",                 # Change problem-solving methodology
    "add_reasoning_steps",               # Insert additional analysis phases
    "improve_validation",                # Strengthen solution verification
    "expand_context"                     # Add domain knowledge and constraints
]

# AlphaEvolve strategy weights (future expansion)
STRATEGY_WEIGHTS = {
    "local_optimization": 0.30,          # Fine-tune current approach
    "structural_changes": 0.40,          # Modify core algorithm/methodology
    "crossover_operations": 0.20,        # Combine successful elements
    "novelty_search": 0.10               # Explore unconventional approaches
}

# === PERFORMANCE TARGETING ===
# Designed for superhuman results
IMPROVEMENT_THRESHOLD = 0.05             # 5% minimum improvement to continue
HUMAN_BASELINE_TARGET = 1.2              # 20% better than human performance
COMPETITION_TARGET = 0.90                # 90th percentile competition score
THEORETICAL_LIMIT_TARGET = 0.95          # 95% of theoretical maximum

# === EVALUATION SYSTEM ===
# Scalable evaluation architecture
EVALUATION_TIMEOUT = 120                 # 2 minutes per solution
QUICK_SCREENING_TIMEOUT = 30             # Fast initial filtering
COMPREHENSIVE_EVAL_TIMEOUT = 300         # Deep analysis for top candidates

# Quality metrics for superhuman performance
EVALUATION_CRITERIA = [
    "accuracy",                          # Solution correctness
    "completeness",                      # Addresses all requirements
    "efficiency",                        # Resource optimization
    "robustness",                        # Edge case handling
    "innovation"                         # Novel approach quality
]

# === LEARNING & MEMORY ===
# Foundation for advanced pattern recognition
SOLUTION_ARCHIVE_SIZE = 100              # Learn from all attempts
PATTERN_MEMORY_DEPTH = 50                # Remember successful patterns
FAILURE_ANALYSIS_ENABLED = True          # Learn from unsuccessful attempts
META_LEARNING_ENABLED = True             # Improve evolution strategy itself

# === SCALABILITY HOOKS ===
# Architecture ready for advanced features
PARALLEL_EVALUATION_LIMIT = 4            # Current: basic / Future: distributed
ADVANCED_MUTATION_ENABLED = False        # Flag for sophisticated algorithms
ENSEMBLE_GENERATION_ENABLED = False      # Flag for multi-solution combinations
EXTERNAL_TOOL_INTEGRATION = False        # Flag for AutoML/specialized tools

# === RESOURCE MANAGEMENT ===
# Realistic current limits with expansion capability
MAX_GENERATION_TIME = 30                 # Minutes per evolution round
TOTAL_EVOLUTION_BUDGET = 8               # Hours for complete evolution
CHECKPOINT_FREQUENCY = 3                 # Save progress every N generations
EARLY_STOPPING_PATIENCE = 5             # Rounds without improvement

# === DIRECTORY STRUCTURE ===
EVOLUTION_DIR = "evolution"
ARCHIVE_DIR = f"{EVOLUTION_DIR}/archive"
GENERATIONS_DIR = f"{EVOLUTION_DIR}/generations"
BEST_SOLUTIONS_DIR = f"{EVOLUTION_DIR}/best"
ANALYSIS_DIR = f"{EVOLUTION_DIR}/analysis"
LINEAGE_DIR = f"{EVOLUTION_DIR}/lineage"

# === LLM OPTIMIZATION ===
# Tuned for breakthrough thinking
PRIMARY_MODEL = "claude-3-7-sonnet-latest"
MAX_TOKENS = 6000                        # Allow complex solutions
TEMPERATURE = 0.75                       # Balance creativity and precision
REASONING_DEPTH = 2                      # Multiple reasoning passes

# === CONVERGENCE CONTROL ===
# Stop when superhuman performance is achieved
CONVERGENCE_THRESHOLD = 0.01             # 1% improvement required
SUPERHUMAN_THRESHOLD = 1.15              # 15% better than human baseline
AUTO_STOP_AT_TARGET = True               # Stop when goals achieved
MAX_STAGNATION_ROUNDS = 6                # Limit unproductive evolution

# === FUTURE EXPANSION FLAGS ===
# Ready for advanced capabilities
COMPETITION_MODE = False                 # Kaggle/contest optimization
DISTRIBUTED_MODE = False                 # Multi-machine evolution  
AUTOML_INTEGRATION = False               # External ML framework usage
NEURAL_ARCHITECTURE_SEARCH = False       # Advanced model discovery 