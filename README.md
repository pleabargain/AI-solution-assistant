# AI-Assisted Decision Making System - Proof of Concept

A Python-based decision making system that uses Ollama for AI assistance in analyzing decisions.

## Prerequisites

1. Python (latest stable version)
2. Ollama installed and running locally
3. llama-3.2 model pulled in Ollama

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is running with llama-3.2 model:
```bash
# Pull llama-3.2 model if not already done
ollama pull llama-3.2
```

## Usage

Run the program:
```bash
python main.py
```

The program will:
1. Ask for a decision you're considering
2. Get one pro and one con from you
3. Use Ollama's AI to analyze your decision
4. Save the decision and analysis to a JSON file in the `decisions` directory

## Features

- Basic decision input capture
- AI-powered analysis using Ollama
- JSON-based storage with timestamps
- Error handling for AI integration
- Cross-platform compatibility using pathlib

## Project Structure

```
.
├── main.py              # Main application file
├── requirements.txt     # Project dependencies
├── README.md           # This file
└── decisions/          # Directory for stored decisions (created on first run)
    └── decision_*.json # Timestamped decision files
```

## Example Output

The program will create JSON files in the `decisions` directory with this structure:

```json
{
  "decision": "What user entered",
  "pros": ["Pro reason"],
  "cons": ["Con reason"],
  "timestamp": "ISO format timestamp",
  "ai_analysis": {
    "analysis": "AI's analysis text",
    "model_used": "llama-3.2",
    "timestamp": "ISO format timestamp"
  }
}
