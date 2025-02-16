"""Module for AI-powered project analysis using OpenAI."""
import os
from typing import Dict, List, Optional
import json
from datetime import datetime
from openai import AsyncOpenAI
import agentops
from pathlib import Path
import logging

# Initialize AgentOps
agentops.init(os.getenv('AGENTOPS_API_KEY'))

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
            logger.info(f"Using cached analysis for project {project_id}")
            with open(cache_file) as f:
                return json.load(f)
        
        try:
            system_prompt = """You are a project analysis expert. Analyze the project data and provide insights in JSON format.
DO NOT use any markdown formatting or code blocks. Return ONLY the raw JSON object.
The response must be a valid JSON object with the following structure:
{
    "health_score": number between 0-100,
    "progress_analysis": {
        "summary": string describing overall progress,
        "completion_rate": number between 0-100,
        "on_track": boolean,
        "concerns": string[] of progress concerns
    },
    "risks": {
        "level": "LOW" | "MEDIUM" | "HIGH",
        "factors": string[] of risk factors,
        "mitigation_suggestions": string[]
    },
    "blockers": {
        "current_blockers": string[],
        "potential_blockers": string[]
    },
    "resource_analysis": {
        "summary": string describing resource utilization,
        "concerns": string[],
        "recommendations": string[]
    },
    "recommendations": {
        "immediate_actions": string[],
        "long_term_improvements": string[]
    },
    "timeline_prediction": {
        "likely_completion": string (date or time range),
        "confidence": number between 0-100,
        "factors_affecting_timeline": string[]
    }
}"""

            logger.info(f"Making OpenAI API call for project {project_id}")
            logger.debug(f"Using model: o3-mini")
            
            # Call OpenAI API with modern client
            response = await self.client.chat.completions.create(
                model="o3-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            logger.debug(f"OpenAI API response received: {len(response.choices[0].message.content)} chars")
            
            # Parse the JSON response
            try:
                content = response.choices[0].message.content
                # Remove any potential markdown formatting (shouldn't be needed with the new prompt)
                if content.startswith("```") and content.endswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json\n"):
                        content = content[5:]
                    elif content.startswith("\n"):
                        content = content[1:]
                    if content.endswith("\n"):
                        content = content[:-1]
                analysis = json.loads(content)
                analysis.update({
                    'analyzed_at': datetime.now().isoformat(),
                    'model_version': "o3-mini"
                })
                logger.info(f"Successfully parsed JSON response for project {project_id}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response content: {content}")
                # Fallback if JSON parsing fails
                analysis = {
                    'error': 'Failed to parse AI response as JSON',
                    'raw_response': response.choices[0].message.content,
                    'analyzed_at': datetime.now().isoformat(),
                    'model_version': "o3-mini"
                }
            
            # Cache the results
            with open(cache_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            logger.info(f"Cached analysis results for project {project_id}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            error_response = {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat(),
                'status': 'failed'
            }
            return error_response

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