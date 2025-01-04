import json
import pytest
from pathlib import Path
from jsonschema import validate
from datetime import datetime
import main

def load_schema():
    """Load the decision schema."""
    with open('decision_schema.json', 'r') as f:
        return json.load(f)

def test_schema_validation():
    """Test that test_decision.json matches our schema."""
    schema = load_schema()
    with open('test_decision.json', 'r') as f:
        test_data = json.load(f)
    
    # This will raise an exception if validation fails
    validate(instance=test_data, schema=schema)

def test_get_multiple_inputs(monkeypatch):
    """Test the get_multiple_inputs function with mocked user input."""
    # Mock user inputs for a pro entry
    inputs = iter([
        "Better performance",  # description
        "9",                  # impact
        "0.95",              # likelihood
        "1500",              # cost
        "n"                  # don't add another
    ])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
    result = main.get_multiple_inputs("test prompt", "pro")
    
    assert len(result) == 1
    assert result[0]["description"] == "Better performance"
    assert result[0]["impact"] == 9.0
    assert result[0]["likelihood"] == 0.95
    assert result[0]["cost"] == 1500.0

def test_save_decision(tmp_path):
    """Test the save_decision function."""
    test_data = {
        "decision": "Test decision",
        "pros": [{
            "description": "Test pro",
            "impact": 8,
            "likelihood": 0.9,
            "cost": 100
        }],
        "cons": [{
            "description": "Test con",
            "impact": 6,
            "likelihood": 0.5,
            "cost": 50
        }],
        "timestamp": datetime.now().isoformat()
    }
    
    # Temporarily redirect the decisions directory
    original_decisions_dir = Path("decisions")
    test_decisions_dir = tmp_path / "decisions"
    test_decisions_dir.mkdir()
    
    try:
        # Patch the decisions directory
        main.Path = lambda x: test_decisions_dir if x == "decisions" else Path(x)
        
        filepath = main.save_decision(test_data)
        assert filepath.exists()
        
        # Load and validate saved data
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        validate(instance=saved_data, schema=load_schema())
        
    finally:
        # Restore original Path behavior
        main.Path = Path

def test_ai_analysis_format():
    """Test the format of AI analysis output."""
    test_data = {
        "decision": "Test decision",
        "pros": [{
            "description": "Test pro",
            "impact": 8,
            "likelihood": 0.9,
            "cost": 100
        }],
        "cons": [{
            "description": "Test con",
            "impact": 6,
            "likelihood": 0.5,
            "cost": 50
        }],
        "timestamp": datetime.now().isoformat()
    }
    
    result = main.get_ai_analysis(test_data)
    
    assert "analysis" in result
    assert "model_used" in result
    assert "timestamp" in result
    assert isinstance(result["analysis"], str)
    assert isinstance(result["model_used"], str)
    assert isinstance(result["timestamp"], str)

if __name__ == "__main__":
    pytest.main([__file__])
