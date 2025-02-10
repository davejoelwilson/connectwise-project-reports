import json
from typing import Dict, Any, Optional
from pathlib import Path

class ProjectConfig:
    def __init__(self, config_path: str = "project_config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load the project configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

    def get_project_config(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific project"""
        return self.config.get('managed_projects', {}).get(project_id)

    def get_global_settings(self) -> Dict[str, Any]:
        """Get global configuration settings"""
        return self.config.get('global_settings', {})

    def is_managed_project(self, project_id: str) -> bool:
        """Check if a project is managed by this system"""
        return project_id in self.config.get('managed_projects', {})

    def get_all_managed_projects(self) -> Dict[str, Dict[str, Any]]:
        """Get all managed projects configuration"""
        return self.config.get('managed_projects', {})

    def get_project_team(self, project_id: str) -> list:
        """Get team members for a specific project"""
        project = self.get_project_config(project_id)
        return project.get('team', []) if project else []

    def get_report_recipients(self, project_id: str) -> list:
        """Get report recipients for a specific project"""
        project = self.get_project_config(project_id)
        return project.get('report_recipients', []) if project else []

    def get_metrics_config(self, project_id: str) -> Dict[str, Any]:
        """Get metrics configuration for a specific project"""
        project = self.get_project_config(project_id)
        return project.get('metrics', {}) if project else {}

    def get_notification_config(self, project_id: str) -> Dict[str, Any]:
        """Get notification configuration for a specific project"""
        project = self.get_project_config(project_id)
        return project.get('notifications', {}) if project else {}

    def get_work_hours(self) -> Dict[str, str]:
        """Get configured work hours"""
        return self.get_global_settings().get('work_hours', {
            'start': '09:00',
            'end': '17:00'
        })

    def get_holidays(self) -> list:
        """Get configured holidays"""
        return self.get_global_settings().get('holidays', []) 