#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import agentops

from backend.connectwise.client import ConnectWiseClient
from backend.analysis.detailed_analyzer import DetailedProjectAnalyzer
from backend.analysis.ai_analyzer import AIProjectAnalyzer
from backend.scripts.collect_detailed_data import collect_project_detailed_data

# Initialize AgentOps
agentops.init(os.getenv('AGENTOPS_API_KEY'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Only show the message
)
# Set third-party loggers to WARNING to reduce noise
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

@agentops.track_agent(name='project-analysis-pipeline')
async def list_projects(client: ConnectWiseClient) -> List[Dict]:
    """Get a simple list of all projects"""
    projects = await client.get_projects({
        'fields': ['id', 'name', 'status/name', 'company/name']  # Minimal fields
    })
    return projects

@agentops.track_agent(name='project-analysis-pipeline')
async def run_pipeline(project_ids: Optional[List[int]] = None):
    """Run the complete analysis pipeline for specified projects"""
    
    # Initialize clients
    cw_client = ConnectWiseClient()
    success = True
    error_message = None
    processed_count = 0
    total_projects = len(project_ids) if project_ids else 0
    
    try:
        # First just list available projects
        if not project_ids:
            print("\nFetching available projects...")
            projects = await list_projects(cw_client)
            
            if not projects:
                print("No projects found in the system.")
                agentops.end_session("Success", "Listed projects - none found")
                return
            
            print("\nAvailable projects:")
            print("ID\tStatus\t\tCompany\t\tName")
            print("-" * 80)
            for p in projects:
                print(f"{p['id']}\t{p.get('status', {}).get('name', 'Unknown'):<10}\t{p.get('company', {}).get('name', 'Unknown'):<10}\t{p.get('name', 'Unknown')}")
            
            # Ask for confirmation
            print("\nUse --project-ids argument to analyze specific projects.")
            print("Example: python backend/scripts/run_analysis_pipeline.py --project-ids 123 456")
            agentops.end_session("Success", "Listed available projects")
            return
        
        # If specific projects were provided, proceed with analysis
        print(f"\nStarting analysis for {len(project_ids)} projects...")
        
        # Create output directories
        data_dir = Path('data')
        detailed_dir = data_dir / 'detailed'
        analysis_dir = data_dir / 'analysis'
        ai_dir = data_dir / 'ai_analysis'
        
        for directory in [data_dir, detailed_dir, analysis_dir, ai_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Process each project
        for project_id in project_ids:
            try:
                print(f"\nProcessing project {project_id}...")
                
                # Step 1: Collect detailed data
                print("Collecting detailed data...")
                detailed_data = await collect_project_detailed_data(cw_client, project_id)
                
                # Save detailed data
                detailed_file = detailed_dir / f"project_{project_id}_detailed.json"
                with open(detailed_file, 'w') as f:
                    json.dump(detailed_data, f, indent=2)
                
                # Step 2: Analyze project data
                print("Analyzing project data...")
                analyzer = DetailedProjectAnalyzer(detailed_data)
                analysis = analyzer.analyze_project_timeline()
                
                # Save analysis
                analysis_file = analysis_dir / f"project_{project_id}_analysis.json"
                with open(analysis_file, 'w') as f:
                    json.dump(analysis, f, indent=2)
                
                # Step 3: Generate AI insights
                print("Generating AI insights...")
                ai_analyzer = AIProjectAnalyzer()
                prompt = analyzer.prepare_ai_prompt()
                ai_analysis = await ai_analyzer.analyze_project(prompt, project_id)
                
                # Save AI analysis
                ai_file = ai_dir / f"project_{project_id}_ai_analysis.json"
                with open(ai_file, 'w') as f:
                    json.dump(ai_analysis, f, indent=2)
                
                print(f"Completed analysis for project {project_id}")
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing project {project_id}: {e}")
                success = False
                error_message = str(e)
                agentops.record_error(str(e))
                continue
    
    except Exception as e:
        success = False
        error_message = str(e)
        agentops.record_error(str(e))
        raise
    
    finally:
        await cw_client.http_client.aclose()
        # End AgentOps session with appropriate status and details
        if success:
            status_message = f"Successfully processed {processed_count}/{total_projects} projects"
            agentops.end_session("Success", status_message)
        else:
            status_message = f"Failed after processing {processed_count}/{total_projects} projects. Error: {error_message}"
            agentops.end_session("Failed", status_message)

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Run the project analysis pipeline')
    parser.add_argument('--project-ids', type=int, nargs='+',
                      help='List of project IDs to analyze. If not provided, will only list available projects.')
    
    args = parser.parse_args()
    asyncio.run(run_pipeline(args.project_ids))

if __name__ == '__main__':
    main() 