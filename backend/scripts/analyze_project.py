#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
import sys
import logging
from datetime import datetime

from backend.connectwise.client import ConnectWiseClient
from backend.analysis.detailed_analyzer import DetailedProjectAnalyzer
from backend.analysis.ai_analyzer import AIProjectAnalyzer
from backend.scripts.collect_detailed_data import collect_project_detailed_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_project(project_id: int):
    """Run complete analysis for a single project"""
    try:
        # Initialize clients
        cw_client = ConnectWiseClient()
        
        # Create output directories
        data_dir = Path('data')
        detailed_dir = data_dir / 'detailed'
        analysis_dir = data_dir / 'analysis'
        ai_dir = data_dir / 'ai_analysis'
        
        for directory in [data_dir, detailed_dir, analysis_dir, ai_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Collect detailed data
        logger.info(f"Collecting detailed data for project {project_id}...")
        detailed_data = await collect_project_detailed_data(cw_client, project_id)
        
        # Save detailed data
        detailed_file = detailed_dir / f"project_{project_id}_detailed.json"
        with open(detailed_file, 'w') as f:
            json.dump(detailed_data, f, indent=2)
        
        # Step 2: Analyze project data
        logger.info("Analyzing project data...")
        analyzer = DetailedProjectAnalyzer(detailed_data)
        analysis = analyzer.analyze_project_timeline()
        
        # Save analysis
        analysis_file = analysis_dir / f"project_{project_id}_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Step 3: Generate AI insights
        logger.info("Generating AI insights...")
        ai_analyzer = AIProjectAnalyzer()
        prompt = analyzer.prepare_ai_prompt()
        ai_analysis = await ai_analyzer.analyze_project(prompt, project_id)
        
        # Save AI analysis
        ai_file = ai_dir / f"project_{project_id}_ai_analysis.json"
        with open(ai_file, 'w') as f:
            json.dump(ai_analysis, f, indent=2)
        
        logger.info(f"Analysis complete for project {project_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error analyzing project {project_id}: {e}")
        return False
    finally:
        await cw_client.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_project.py <project_id>")
        sys.exit(1)
        
    try:
        project_id = int(sys.argv[1])
    except ValueError:
        print("Error: project_id must be a number")
        sys.exit(1)
        
    success = asyncio.run(analyze_project(project_id))
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 