import json
from pathlib import Path
from datetime import datetime
import ollama
import sys

def load_project_config():
    """Load project configuration."""
    try:
        with open('project-description.json', 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading project configuration: {str(e)}")
        return None

# Configure Ollama client
ollama.client = ollama.Client(host='http://localhost:11434')

def generate_suggestions(decision, category, count=5, temperature=0.7):
    """Generate AI suggestions for pros/cons."""
    try:
        model = 'llama3.2'
        
        # Create appropriate prompt based on category
        if category == "pros":
            prompt = f"""Generate exactly {count} benefits of {decision}.
            Format as a simple numbered list.
            No introductions or explanations.
            Just {count} numbered items.
            
            Required format:
            1. [clear, specific benefit]
            2. [clear, specific benefit]
            3. [clear, specific benefit]
            4. [clear, specific benefit]
            5. [clear, specific benefit]"""
        else:
            prompt = f"""Generate exactly {count} drawbacks of {decision}.
            Format as a simple numbered list.
            No introductions or explanations.
            Just {count} numbered items.
            
            Required format:
            1. [clear, specific drawback]
            2. [clear, specific drawback]
            3. [clear, specific drawback]
            4. [clear, specific drawback]
            5. [clear, specific drawback]"""
        
        response = ollama.chat(
            model=model, 
            messages=[{'role': 'user', 'content': prompt}],
            options={"temperature": temperature}
        )
        
        # Process the response to extract clean suggestions
        content = response['message']['content'].strip()
        suggestions = []
        
        # Split into lines and process each line
        for line in content.split('\n'):
            # Remove leading numbers, dots, and spaces
            cleaned = line.strip()
            if cleaned:
                # Remove leading numbers and dots (e.g., "1.", "2.", etc.)
                cleaned = '.'.join(cleaned.split('.')[1:]).strip()
                if cleaned:
                    suggestions.append(cleaned)
        
        # Ensure we have exactly count suggestions
        while len(suggestions) < count:
            suggestions.append(f"Example {category} {len(suggestions) + 1}")
        
        return suggestions[:count]
    except Exception as e:
        print(f"AI suggestion generation failed: {str(e)}")
        if "connection refused" in str(e).lower():
            print("Error: Please ensure Ollama is running on http://localhost:11434")
        # Fallback suggestions if AI fails
        return [f"Example {category} {i+1}" for i in range(count)]

def get_selected_items(items, prompt):
    """Get user selection from a list of items."""
    print("\n".join(f"{i+1}. {item}" for i, item in enumerate(items)))
    print("\nEnter numbers (e.g., 1,2,3), '*' for all, or press Enter to skip")
    while True:
        selection = input(prompt).strip()
        if not selection:  # Empty input means skip
            return []
        if selection == '*':
            return items
        try:
            indices = [int(i.strip()) - 1 for i in selection.split(',')]
            if all(0 <= i < len(items) for i in indices):
                return [items[i] for i in indices]
        except ValueError:
            pass
        print("Please enter comma-separated numbers, '*' for all, or press Enter to skip")

def evaluate_item(item, category):
    """Get impact, likelihood, and cost evaluation for an item."""
    print(f"\nEvaluating {category}: {item}")
    impact = float(input("Rate the impact (1-10): ").strip())
    likelihood = float(input("Enter the likelihood (0-1) of this occurring: ").strip())
    cost = float(input("Enter any associated cost ($): ").strip())
    return {
        "description": item,
        "impact": impact,
        "likelihood": likelihood,
        "cost": cost
    }

def get_machine_opportunity_costs(decision):
    """Generate AI suggestions for opportunity costs."""
    try:
        model = 'llama2'  # Using llama2 model
        prompt = f"""Generate exactly 5 opportunity costs for the decision: {decision}
        These should be specific things that would be foregone by making this decision.
        Format as a simple numbered list.
        No introductions or explanations.
        Just 5 numbered items.
        
        Required format:
        1. [clear, specific opportunity cost]
        2. [clear, specific opportunity cost]
        3. [clear, specific opportunity cost]
        4. [clear, specific opportunity cost]
        5. [clear, specific opportunity cost]"""
        
        response = ollama.chat(model=model, messages=[
            {'role': 'user', 'content': prompt}
        ])
        
        content = response['message']['content'].strip()
        suggestions = []
        
        for line in content.split('\n'):
            cleaned = line.strip()
            if cleaned:
                cleaned = '.'.join(cleaned.split('.')[1:]).strip()
                if cleaned:
                    suggestions.append(cleaned)
        
        while len(suggestions) < 5:
            suggestions.append(f"Example opportunity cost {len(suggestions) + 1}")
        
        return suggestions[:5]
    except Exception as e:
        print(f"AI suggestion generation failed: {str(e)}")
        return [f"Example opportunity cost {i+1}" for i in range(5)]

def evaluate_opportunity_cost(description):
    """Get impact, likelihood, and value evaluation for an opportunity cost."""
    print(f"\nEvaluating opportunity cost: {description}")
    impact = get_valid_number_input("Rate the impact (1-10): ", 1, 10)
    likelihood = get_valid_number_input("Enter likelihood (0-1): ", 0, 1)
    value = get_valid_number_input("Estimated value ($): ", 0, float('inf'))
    
    return {
        "description": description,
        "impact": impact,
        "likelihood": likelihood,
        "value": value,
        "input_source": "HUMAN" if "Example opportunity cost" not in description else "MACHINE"
    }

def get_opportunity_costs(decision):
    """Get opportunity costs with user input and optional AI suggestions."""
    opportunity_costs = []
    
    # Get user's own opportunity costs first
    print("\nWhat opportunity costs can you think of? (what would you give up by making this decision)")
    print("Press Enter without typing anything when done adding your own opportunity costs.")
    
    while True:
        description = input("\nEnter an opportunity cost: ").strip()
        if not description:
            break
            
        opportunity_cost = evaluate_opportunity_cost(description)
        opportunity_costs.append(opportunity_cost)
    
    # Ask if they want AI suggestions
    if input("\nWould you like to see AI-generated opportunity costs? (y/n): ").lower().strip() == 'y':
        suggestions = get_machine_opportunity_costs(decision)
        print("\nAI Suggested Opportunity Costs:")
        selected_items = get_selected_items(suggestions, "Select opportunity costs (comma-separated numbers or press Enter to skip): ")
        
        for item in selected_items:
            opportunity_cost = evaluate_opportunity_cost(item)
            opportunity_cost["input_source"] = "MACHINE"
            opportunity_costs.append(opportunity_cost)
    
    return opportunity_costs

def get_pros_cons_input(decision, num_prompts, temperature):
    """Get pros and cons with user input and optional AI suggestions."""
    inputs = {"pros": [], "cons": []}
    
    for category in ["pros", "cons"]:
        selected_items = []
        
        # Get user's own pros/cons first
        print(f"\nWhat {category} can you think of? (press Enter without text to finish)")
        while True:
            item = input().strip()
            if not item:  # Empty input means we're done
                break
            selected_items.append(item)
            print("Item added. Enter another or press Enter to finish.")
        
        # Ask if they want AI suggestions
        if input(f"\nWould you like to see AI-generated {category}? (y/n): ").lower().strip() == 'y':
            while True:
                suggestions = generate_suggestions(decision, category, count=num_prompts, temperature=temperature)
                print(f"\nAI Suggested {category.capitalize()}:")
                items = get_selected_items(suggestions, f"Select additional {category} (comma-separated numbers or press Enter to skip): ")
                selected_items.extend(items)
                
                if not items:  # User pressed Enter to skip
                    break
                    
                more = input(f"Would you like to see more AI {category}? (y/n): ").lower().strip() == 'y'
                if not more:
                    break
        
        # Evaluate all selected items
        print(f"\nEvaluating selected {category}:")
        for item in selected_items:
            inputs[category].append(evaluate_item(item, category.rstrip('s')))
    
    return inputs

def get_valid_number_input(prompt, min_val, max_val):
    """Get valid number input from user within specified range."""
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Please enter a valid number.")

def get_user_input():
    """Get basic decision input from user."""
    print("\nDecision Making Assistant")
    print("-----------------------")
    
    # Get number of generated prompts
    while True:
        try:
            num_prompts = int(input("How many generated prompts would you like (1-5)? "))
            if 1 <= num_prompts <= 5:
                break
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
            
    # Get temperature for creativity
    while True:
        try:
            temp = int(input("Enter temperature for creativity (1-10, higher = more creative): "))
            if 1 <= temp <= 10:
                # Scale from 1-10 to 0.1-0.99
                temp = 0.1 + (temp - 1) * (0.89/9)
                break
            print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    decision = input("\nWhat decision are you considering? ").strip()
    
    print("\nRisk Tolerance Scale (1-10):")
    print("1: Zero tolerance for risk")
    print("2-7: Increasing tolerance for financial/emotional/physical risk")
    print("8: Willing to risk death of self")
    print("9: Willing to risk death of family")
    print("10: Maximum risk tolerance (death of self and others)")
    
    while True:
        try:
            risk_tolerance = int(input("\nWhat is your risk tolerance level (1-10)? "))
            if 1 <= risk_tolerance <= 10:
                break
            print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get pros and cons
    inputs = get_pros_cons_input(decision, num_prompts, temp)
    
    # Get opportunity costs
    opportunity_costs = get_opportunity_costs(decision)
    
    return {
        "decision": decision,
        "risk_tolerance": risk_tolerance,
        "num_prompts": num_prompts,
        "temperature": temp,
        "pros": inputs["pros"],
        "cons": inputs["cons"],
        "opportunity_costs": opportunity_costs,
        "timestamp": datetime.now().isoformat()
    }

def save_decision(data):
    """Save decision data to JSON file."""
    decisions_dir = Path("decisions")
    decisions_dir.mkdir(exist_ok=True)
    
    # Sanitize decision text for filename
    decision_prefix = data["decision"].lower()
    decision_prefix = ''.join(c if c.isalnum() or c == '_' else '_' for c in decision_prefix)
    decision_prefix = decision_prefix[:50]  # Limit length
    
    filename = f"{decision_prefix}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json"
    filepath = decisions_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    return filepath

def get_ai_analysis(data):
    """Get AI analysis using Ollama."""
    # Create prompt from decision data
    prompt = f"""
    You are assisting with a decision about: {data['decision']}
    
    Pros:
    {chr(10).join(f"- {pro['description']} (Impact: {pro['impact']}/10, Likelihood: {pro['likelihood']}, Cost: ${pro['cost']})" for pro in data['pros'])}
    
    Cons:
    {chr(10).join(f"- {con['description']} (Impact: {con['impact']}/10, Likelihood: {con['likelihood']}, Cost: ${con['cost']})" for con in data['cons'])}
    
    Opportunity Costs:
    {chr(10).join(f"- {opp['description']} (Impact: {opp['impact']}/10, Likelihood: {opp['likelihood']}, Value: ${opp['value']})" for opp in data['opportunity_costs'])}
    
    Please provide a thorough analysis considering:
    1. The weighted impact of each factor (impact × likelihood)
    2. Cost-benefit analysis including all financial implications
    3. Risk assessment based on likelihood and impact scores (User's risk tolerance: {data['risk_tolerance']}/10)
    4. Evaluation of opportunity costs and their potential impact
    5. Potential short-term and long-term consequences
    6. A clear recommendation based on the quantitative analysis and risk tolerance
    
    Format your response with clear sections for:
    - Summary of key points
    - Quantitative analysis (including weighted impacts and costs)
    - Opportunity costs evaluation
    - Risk assessment
    - Final recommendation
    """
    
    try:
        # Check Ollama connection
        ollama.list()
    except Exception as e:
        return {
            "error": f"Ollama connection failed: {str(e)}",
            "metadata": {
                "model_used": None,
                "timestamp": datetime.now().isoformat(),
                "processing_time": 0
            }
        }

    start_time = datetime.now()
    
    # Get response from Ollama
    try:
        model = 'llama2'  # Using llama2 model
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        # Process response into required format
        analysis_text = response['message']['content']
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "analysis": {
                "summary": analysis_text[:200] + "...",  # First 200 chars as summary
                "confidence": 0.8,  # Default confidence
                "recommendations": [analysis_text]  # Full analysis as recommendation
            },
            "evaluation": {
                "pros_analysis": {
                    "total_impact": sum(p["impact"] * p["likelihood"] for p in data["pros"]),
                    "total_cost": sum(p["cost"] for p in data["pros"])
                },
                "cons_analysis": {
                    "total_impact": sum(c["impact"] * c["likelihood"] for c in data["cons"]),
                    "total_cost": sum(c["cost"] for c in data["cons"])
                },
                "risk_assessment": {
                    "raw_risk_score": sum(c["impact"] * c["likelihood"] for c in data["cons"]) / len(data["cons"]) if data["cons"] else 0,
                    "risk_tolerance": data["risk_tolerance"],
                    "adjusted_risk_score": (sum(c["impact"] * c["likelihood"] for c in data["cons"]) / len(data["cons"]) if data["cons"] else 0) * (11 - data["risk_tolerance"]) / 10
                },
                "opportunity_costs_analysis": {
                    "total_impact": sum(o["impact"] * o["likelihood"] for o in data["opportunity_costs"]),
                    "total_value": sum(o["value"] for o in data["opportunity_costs"])
                }
            },
            "metadata": {
                "model_used": "llama2",  # Using llama2 model
                "timestamp": datetime.now().isoformat(),
                "processing_time": processing_time
            }
        }
    except Exception as e:
        return {
            "error": f"AI analysis failed: {str(e)}",
            "metadata": {
                "model_used": "llama2",  # Using llama2 model
                "timestamp": datetime.now().isoformat(),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        }

def process_json_file(filepath):
    """Process a JSON file containing decision data."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Get AI analysis
        print("\nGetting AI analysis...")
        ai_result = get_ai_analysis(data)
        
        # Combine data
        final_data = {
            **data,
            "ai_analysis": ai_result
        }
        
        # Save decision
        output_filepath = save_decision(final_data)
        print(f"\nProcessed decision saved to: {output_filepath}")
        
        # Generate report
        try:
            from generate_report import generate_markdown_report
            report_file = generate_markdown_report(output_filepath)
            if report_file:
                print(f"Report generated: {report_file}")
            else:
                print("Failed to generate report")
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            
            # Display AI analysis
            if "error" not in ai_result:
                print("\nAI Analysis Summary:")
                print(ai_result["analysis"]["summary"])
                print("\nRecommendations:")
                for rec in ai_result["analysis"]["recommendations"]:
                    print(f"- {rec[:100]}...")  # Show first 100 chars of each recommendation
                print("\nRisk Assessment:")
                print(f"Raw Risk Score: {ai_result['evaluation']['risk_assessment']['raw_risk_score']:.2f}")
                print(f"Risk Tolerance Level: {ai_result['evaluation']['risk_assessment']['risk_tolerance']}/10")
                print(f"Adjusted Risk Score: {ai_result['evaluation']['risk_assessment']['adjusted_risk_score']:.2f}")
                print("\nOpportunity Costs Analysis:")
                print(f"Total Impact: {ai_result['evaluation']['opportunity_costs_analysis']['total_impact']:.2f}")
                print(f"Total Value: ${ai_result['evaluation']['opportunity_costs_analysis']['total_value']:.2f}")
            else:
                print("\nCritical Error:", ai_result["error"])
            
    except Exception as e:
        print(f"Error processing JSON file: {str(e)}")

def main():
    """Main execution flow."""
    # Check if Ollama is running first
    try:
        ollama.list()
    except Exception as e:
        print("Error: Could not connect to Ollama. Please ensure it is running on http://localhost:11434")
        print(f"Details: {str(e)}")
        sys.exit(1)
        
    # Load configuration at startup
    config = load_project_config()
    if not config:
        print("Error: Could not load project configuration. Using default settings.")
        config = {
            "settings": {
                "default_model": "llama2",
                "default_temperature": 0.7,
                "default_prompts": 3
            }
        }

    # Check if a JSON file was provided as argument
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        print(f"Processing JSON file: {json_file}")
        process_json_file(json_file)
        return

    while True:
        try:
            # Get user input
            decision_data = get_user_input()
            
            # Validate input
            if not decision_data["pros"] and not decision_data["cons"]:
                print("\nError: At least one pro or con is required to proceed.")
                continue
            
            # Get AI analysis
            print("\nGetting AI analysis...")
            ai_result = get_ai_analysis(decision_data)
            
            # Combine data
            final_data = {
                **decision_data,
                "ai_analysis": ai_result
            }
            
            # Save decision
            filepath = save_decision(final_data)
            print(f"\nDecision saved to: {filepath}")
            
            # Ask if user wants to generate a report
            generate_report = input("\nWould you like to generate a markdown report? (y/n): ").lower().strip() == 'y'
            if generate_report:
                try:
                    from generate_report import generate_markdown_report
                    report_file = generate_markdown_report(filepath)
                    if report_file:
                        print(f"Report generated: {report_file}")
                    else:
                        print("Failed to generate report")
                except Exception as e:
                    print(f"Error generating report: {str(e)}")
            
            # Display AI analysis
            if "error" not in ai_result:
                print("\nAI Analysis Summary:")
                print(ai_result["analysis"]["summary"])
                print("\nRecommendations:")
                for rec in ai_result["analysis"]["recommendations"]:
                    print(f"- {rec[:100]}...")  # Show first 100 chars of each recommendation
                print("\nRisk Assessment:")
                print(f"Raw Risk Score: {ai_result['evaluation']['risk_assessment']['raw_risk_score']:.2f}")
                print(f"Risk Tolerance Level: {ai_result['evaluation']['risk_assessment']['risk_tolerance']}/10")
                print(f"Adjusted Risk Score: {ai_result['evaluation']['risk_assessment']['adjusted_risk_score']:.2f}")
                print("\nOpportunity Costs Analysis:")
                print(f"Total Impact: {ai_result['evaluation']['opportunity_costs_analysis']['total_impact']:.2f}")
                print(f"Total Value: ${ai_result['evaluation']['opportunity_costs_analysis']['total_value']:.2f}")
            else:
                print("\nCritical Error:", ai_result["error"])
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Ask if user wants to consider another decision
        continue_input = input("\nWould you like to consider another decision? (y/n): ").lower().strip()
        if continue_input != 'y':
            print("\nThank you for using the Decision Making Assistant. Your file has been saved.")
            break

if __name__ == "__main__":
    main()
