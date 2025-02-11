#!/usr/bin/env python3

import asyncio
import json
from pathlib import Path
from backend.analysis.project_analyzer import analyze_project_file

async def main():
    """Analyze all sample project data files."""
    sample_dir = Path(__file__).parent.parent / 'data' / 'samples'
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Analyze each project file
    for project_file in sample_dir.glob('project_*.json'):
        if '_analysis' not in project_file.name:  # Skip analysis files
            print(f"\nAnalyzing {project_file.name}...")
            analysis = analyze_project_file(str(project_file))
            
            # Print key metrics
            print("\nKey Metrics:")
            print(f"Project: {analysis['project_metrics']['name']}")
            print(f"Status: {analysis['project_metrics']['status']}")
            print(f"Hours: {analysis['project_metrics']['hours']['actual']} actual / {analysis['project_metrics']['hours']['estimated']} estimated")
            print(f"Completion Rate: {analysis['ticket_analysis']['completion_metrics']['completion_rate']:.1f}%")
            print(f"Risk Level: {analysis['risk_indicators']['risk_level']}")
            
            if analysis['risk_indicators']['risk_factors']:
                print("\nRisk Factors:")
                for risk in analysis['risk_indicators']['risk_factors']:
                    print(f"- {risk}")
            
            if analysis['ticket_analysis']['stalled_tickets']:
                print("\nStalled Tickets:")
                for ticket in analysis['ticket_analysis']['stalled_tickets']:
                    print(f"- {ticket['summary']} (ID: {ticket['id']})")
            
            # Save analysis results
            output_file = project_file.parent / f"{project_file.stem}_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"\nFull analysis saved to {output_file}")

if __name__ == '__main__':
    asyncio.run(main()) 