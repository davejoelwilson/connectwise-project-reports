"""Module for AI-powered project analysis using OpenAI."""
import os
from typing import Dict, List, Optional
import json
from datetime import datetime
from openai import AsyncOpenAI
import agentops
from pathlib import Path

# Initialize AgentOps
agentops.init(os.getenv('AGENTOPS_API_KEY'))

class AIProjectAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.cache_dir = Path('data/ai_analysis')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @agentops.record_action('analyze_project')
    async def analyze_project(self, prompt: str, project_id: int) -> dict:
        """Analyze project data using OpenAI's API"""
        
        # Check cache first
        cache_file = self.cache_dir / f"analysis_{project_id}_{datetime.now().strftime('%Y%m%d')}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        
        try:
            # Call OpenAI API with modern client
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a project analysis expert. Analyze the project data and provide insights about health, progress, risks, resources, and timeline."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            analysis = {
                'insights': response.choices[0].message.content,
                'analyzed_at': datetime.now().isoformat(),
                'model_version': "gpt-4"
            }
            
            # Cache the results
            with open(cache_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat(),
                'status': 'failed'
            }

    async def analyze_multiple_projects(self, project_prompts: Dict[int, str]) -> Dict[int, dict]:
        """Analyze multiple projects in parallel"""
        results = {}
        for project_id, prompt in project_prompts.items():
            results[project_id] = await self.analyze_project(prompt, project_id)
        return results

    def get_cached_analysis(self, project_id: int, date: Optional[str] = None) -> Optional[dict]:
        """Retrieve cached analysis for a project"""
        if date:
            cache_file = self.cache_dir / f"analysis_{project_id}_{date}.json"
            if cache_file.exists():
                with open(cache_file) as f:
                    return json.load(f)
        else:
            # Get most recent analysis
            files = list(self.cache_dir.glob(f"analysis_{project_id}_*.json"))
            if files:
                latest = max(files, key=lambda x: x.stat().st_mtime)
                with open(latest) as f:
                    return json.load(f)
        return None

    def clear_cache(self, project_id: Optional[int] = None, before_date: Optional[str] = None):
        """Clear cached analyses"""
        if project_id:
            pattern = f"analysis_{project_id}_*.json"
        else:
            pattern = "analysis_*.json"
            
        for file in self.cache_dir.glob(pattern):
            if before_date:
                file_date = file.stem.split('_')[-1]
                if file_date < before_date:
                    file.unlink()
            else:
                file.unlink() 