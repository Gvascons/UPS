# UPS - Universal Problem Solver

A sophisticated multi-modal AI system that implements two complementary approaches to problem-solving: **Solution Generation** (Mode 1) and **Solution Evolution** (Mode 2).

## 🎯 System Overview

UPS combines systematic problem-solving with iterative improvement to tackle complex challenges across domains. The system uses LangGraph workflows, multi-agent coordination, and persistent state management to deliver robust solutions.

### Architecture Modes

- **Mode 1 (Solver)**: ✅ **Implemented** - Generates solutions from scratch using Plan-Execute methodology
- **Mode 2 (Evolver)**: 🚧 **Planned** - Evolves and optimizes existing solutions through iterative refinement

## 🏗️ Project Structure

```
UPS/
├── UPS/
│   ├── solver/          # Mode 1: Solution Generation
│   │   ├── engine.py    # Main entry point with CLI and streaming
│   │   ├── graph.py     # LangGraph workflow definition
│   │   ├── nodes.py     # Planner → Agent → Replanner nodes
│   │   ├── schemas.py   # State management and structured outputs
│   │   ├── prompts.py   # Specialized prompts for each workflow stage
│   │   ├── tools.py     # Python execution + web search tools
│   │   ├── utils.py     # Graph visualization utilities
│   │   └── config.py    # Configuration constants
│   │
│   ├── evolver/         # Mode 2: Solution Evolution (Planned)
│   │   └── ...          # Future implementation
│   │
│   ├── context.txt      # Problem input file
│   ├── main.py          # System orchestrator
│   └── meta_controller.py # Mode selection logic
│
├── metadata/            # Intermediate files and step tracking
├── output/              # Final deliverable files
└── reference/           # Analysis reference (adam system)
```

## 🔧 Mode 1: Solution Generation

### Workflow Architecture

The solver implements a **Plan → Execute → Replan** cycle:

```mermaid
graph LR
    A[START] --> B[Planner]
    B --> C[Agent]
    C --> D[Replanner]
    D --> C
    D --> E[END]
```

### Core Components

**🧠 Planner Node**
- Breaks down complex problems into actionable steps
- Creates structured execution plans with tool awareness
- Handles LLM structured output with fallback parsing

**⚡ Agent Node** 
- Executes plan steps using ReAct pattern (max 7 iterations)
- Integrates with tools: `execute_python_code` + `web_search`
- Maintains persistent state across execution steps

**🔄 Replanner Node**
- Evaluates progress after each step execution
- Decides: Continue (new plan) vs Complete (final response)
- Handles completion criteria and error recovery

### Tool Ecosystem

**🐍 Python Execution**
- Isolated subprocess execution with 60s timeout
- Comprehensive error handling and output capture
- Supports data processing, ML, calculations, file I/O

**🌐 Web Search**
- DuckDuckGo integration for research and information gathering
- Result filtering and content summarization
- Documentation and example discovery

### File Management Strategy

**📁 Directory Usage**
- `metadata/`: Intermediate artifacts, research findings, step-by-step tracking
- `output/`: Final deliverable files when explicitly requested by problem

**💾 Persistent State**
- Cross-step file sharing for complex workflows
- Automatic directory creation and management
- Descriptive file naming for step continuity

## 🚀 Usage

### Basic Execution
```bash
# Run with default context.txt
python -m UPS.solver.engine

# Custom input file
python -m UPS.solver.engine --input_file my_problem.txt

# Enable Langfuse tracing
python -m UPS.solver.engine --enable_tracing
```

### Example Problem (current context.txt)
```
Create a machine learning model to predict house prices using the Boston housing dataset. 
Include data preprocessing, model training, evaluation, and save the results to a CSV file.
```

### Expected Output Structure
```
metadata/
├── step1_research.txt      # Dataset and approach research
├── step2_data.csv          # Preprocessed dataset
├── step3_model.pkl         # Trained model artifacts
└── step4_evaluation.txt    # Model performance metrics

output/
├── house_price_predictions.csv  # Final predictions
└── model_report.txt              # Summary report
```

## 🔬 Technical Features

### LLM Integration
- **Multi-Provider Support**: OpenAI, Anthropic, Google Gemini
- **Structured Outputs**: Pydantic models with manual parsing fallbacks
- **Error Recovery**: Graceful degradation when LLM calls fail

### Execution Management
- **Async Streaming**: Real-time progress updates during execution
- **State Persistence**: Operator-based state merging with `past_steps` accumulation
- **Timeout Handling**: 60-second limits on code execution with proper cleanup

### Observability
- **Langfuse Tracing**: Optional execution tracking and performance monitoring
- **Graph Visualization**: Automatic workflow diagram generation
- **Comprehensive Logging**: Debug, info, warning, and error level tracking

### Quality Assurance
- **Comprehensive Testing**: 24/24 test coverage for tools and core functionality
- **Error Handling**: Graceful failures at each workflow node
- **Validation**: Input validation and state consistency checks

## 📋 Dependencies

### Core Requirements
```
langgraph>=0.2.0          # Workflow orchestration
langchain>=0.3.0          # LLM framework
pydantic>=2.0.0           # Structured data validation
duckduckgo-search         # Web search functionality
python-dotenv             # Environment management
langfuse                  # Optional: Execution tracing
```

### LLM Providers (Choose One)
```
langchain-openai          # OpenAI GPT models
langchain-anthropic       # Anthropic Claude models  
langchain-google-genai    # Google Gemini models
```

## 🎯 Mode 2: Evolution (Planned)

The evolution system will implement:

**🧬 Solution Refinement**
- Iterative improvement of Mode 1 solutions
- Performance-based optimization cycles
- Multi-criteria evaluation frameworks

**🔄 Adaptive Learning**
- Solution pattern recognition and reuse
- Dynamic strategy adjustment based on problem types
- Cross-domain knowledge transfer

**📊 Evaluation Systems**
- Automated solution quality assessment
- Comparative analysis across solution variants
- Success metrics tracking and optimization

## 🤝 Contributing

This system represents a foundation for systematic AI problem-solving. The current Mode 1 implementation provides robust solution generation, while Mode 2 will add evolutionary capabilities for solution optimization.

### Development Priorities
1. ✅ Mode 1 core functionality and testing
2. 🚧 Mode 2 evolution framework design
3. 🔮 Multi-agent coordination enhancements
4. 🔮 Advanced evaluation and optimization systems

## 📊 Performance Characteristics

- **Execution Speed**: Typical problems resolve in 2-10 minutes
- **Success Rate**: High completion rate with graceful error handling
- **Resource Usage**: Moderate computational requirements with configurable timeouts
- **Scalability**: Designed for complex, multi-step problems requiring tool usage

## 🔐 Configuration

### Environment Variables
```bash
# Required for LLM providers
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  
GOOGLE_API_KEY=your_key_here

# Optional: Langfuse tracing
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_PUBLIC_KEY=your_public_key
```

### System Settings
- **Metadata Directory**: `metadata/` (configurable via `config.py`)
- **Output Directory**: `output/` (configurable via `config.py`)
- **Execution Timeout**: 60 seconds per tool call
- **ReAct Iterations**: Maximum 7 per agent execution

---

*UPS represents a systematic approach to AI-powered problem solving, combining the reliability of structured workflows with the flexibility of multi-agent systems.*
