# System Patterns

## How the System is Built

### Architecture
1. Single Directory Structure
   - All core Python modules in root directory
   - Separate decisions directory for storing decision records
   - Centralized logging with daily rotation

2. Core Components
   - main.py: Entry point and orchestration
   - model_handler.py: Ollama model management
   - input_processor.py: User input handling
   - decision_logger.py: Logging system
   - ai_assistant.py: AI integration logic
   - json_manager.py: Data storage handling
   - error_handler.py: Error management

### Data Flow
1. Input Processing
   - Free text and integer inputs for pros/cons
   - Numerical and descriptive text for estimates
   - No strict validation to maintain flexibility

2. Storage Pattern
   - JSON-based storage
   - Timestamped files (decision_YYYY_MM_DD_HH_MM_SS.json)
   - Single directory organization
   - Original input preservation

## Key Technical Decisions

1. AI Integration
   - Ollama as the AI backend
   - Structured JSON response format
   - Templated prompts with custom append capability
   - Toggle-able AI assistance

2. Error Management
   - Exit with logging for Ollama errors
   - Default model fallback system
   - Local connection health monitoring
   - Critical-only user feedback

3. Logging Strategy
   - Daily rotating log file
   - Multiple logging levels (ERROR, INFO)
   - Comprehensive field inclusion
   - Standardized timestamp format

## Architecture Patterns

1. Input/Output
   - Interactive CLI interface
   - Operation-based input flow (add/edit/remove)
   - Current list display after changes
   - Critical error validation

2. Data Management
   - JSON-based persistence
   - Timestamped file organization
   - Centralized logging
   - Original data preservation

3. AI Integration
   - Template-based prompting
   - Structured response parsing
   - Configurable assistance points
   - Default-off toggle mode

4. Error Handling
   - Hierarchical error management
   - Health check system
   - Fallback mechanisms
   - Critical error prioritization
