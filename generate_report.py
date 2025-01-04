import json
from pathlib import Path
import sys

def generate_markdown_report(json_file_path):
    """Generate a markdown report from a decision JSON file."""
    try:
        # Read and parse JSON file
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Extract decision name and create report filename
        decision_name = data['decision'].lower().replace(' ', '_')
        report_path = Path('reports')
        report_path.mkdir(exist_ok=True)
        
        markdown_content = f"""# Decision Analysis Report: {data['decision']}

## Overview
Decision: {data['decision']}
Date: {data['timestamp']}

## Pros Analysis
"""
        # Add pros with their evaluations if available
        if isinstance(data['pros'][0], dict):  # New format with evaluations
            for pro in data['pros']:
                source_tag = f"[{pro.get('input_source', 'UNKNOWN')}]" if 'input_source' in pro else ""
                markdown_content += f"""
### {pro['description']} {source_tag}
- Impact: {pro['impact']}/10
- Likelihood: {pro['likelihood']}
- Cost: ${pro['cost']}
- Weighted Impact: {pro['impact'] * pro['likelihood']:.1f}
"""
        else:  # Old format without evaluations
            for pro in data['pros']:
                markdown_content += f"- {pro}\n"

        markdown_content += "\n## Cons Analysis\n"
        
        # Add cons with their evaluations if available
        if isinstance(data['cons'][0], dict):  # New format with evaluations
            for con in data['cons']:
                source_tag = f"[{con.get('input_source', 'UNKNOWN')}]" if 'input_source' in con else ""
                markdown_content += f"""
### {con['description']} {source_tag}
- Impact: {con['impact']}/10
- Likelihood: {con['likelihood']}
- Cost: ${con['cost']}
- Weighted Impact: {con['impact'] * con['likelihood']:.1f}
"""
        else:  # Old format without evaluations
            for con in data['cons']:
                markdown_content += f"- {con}\n"

        # Add AI analysis if available
        if 'ai_analysis' in data:
            markdown_content += "\n## AI Analysis\n"
            if 'error' in data['ai_analysis']:
                markdown_content += f"\nError: {data['ai_analysis']['error']}\n"
            else:
                if isinstance(data['ai_analysis'], dict) and 'analysis' in data['ai_analysis']:
                    if isinstance(data['ai_analysis']['analysis'], dict):
                        # New format
                        markdown_content += f"\n### Summary\n{data['ai_analysis']['analysis']['summary']}\n"
                        markdown_content += f"\n### Recommendations\n{data['ai_analysis']['analysis']['recommendations'][0]}\n"
                        
                        # Add evaluation metrics
                        eval_data = data['ai_analysis']['evaluation']
                        markdown_content += f"""
### Evaluation Metrics
- Total Pros Impact: {eval_data['pros_analysis']['total_impact']:.1f}
- Total Pros Cost: ${eval_data['pros_analysis']['total_cost']:.2f}
- Total Cons Impact: {eval_data['cons_analysis']['total_impact']:.1f}
- Total Cons Cost: ${eval_data['cons_analysis']['total_cost']:.2f}
- Raw Risk Score: {eval_data['risk_assessment']['raw_risk_score']:.1f}
- Risk Tolerance: {eval_data['risk_assessment']['risk_tolerance']}/10
- Adjusted Risk Score: {eval_data['risk_assessment']['adjusted_risk_score']:.1f}
"""
                    else:
                        # Old format
                        markdown_content += data['ai_analysis']['analysis']

        # Save the report
        report_file = report_path / f"{decision_name}_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return report_file
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_report.py <path_to_json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    report_file = generate_markdown_report(json_file)
    if report_file:
        print(f"Report generated: {report_file}")
    else:
        print("Failed to generate report")
