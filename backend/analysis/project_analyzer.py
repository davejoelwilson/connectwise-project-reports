"""Project data analysis module for generating quick insights."""

from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import json

class ProjectAnalyzer:
    def __init__(self, project_data: Dict[str, Any]):
        self.project_data = project_data
        self.project = project_data['project']
        self.tickets = project_data['tickets']
        self.time_entries = project_data['time_entries']
        self.notes = project_data['notes']
        self.members = project_data['members']

    def analyze(self) -> Dict[str, Any]:
        """Run all analysis and return combined metrics."""
        return {
            "project_metrics": self._analyze_project_metrics(),
            "ticket_analysis": self._analyze_tickets(),
            "resource_metrics": self._analyze_resources(),
            "risk_indicators": self._analyze_risks(),
            "tickets": self.tickets  # Add raw tickets to output
        }

    def _analyze_project_metrics(self) -> Dict[str, Any]:
        """Analyze basic project metrics."""
        return {
            "id": self.project["id"],
            "name": self.project["name"],
            "company": self.project.get("company", {}).get("name", "No Company Listed"),
            "hours": {
                "actual": self.project["actualHours"],
                "estimated": self.project.get("estimatedHours", 0),
                "has_estimates": self.project.get("estimatedHours", 0) > 0
            },
            "status": self.project["status"]["name"],
            "start_date": self.project.get("scheduledStart"),
            "manager": self.project.get("manager", {}).get("identifier")
        }

    def _analyze_tickets(self) -> Dict[str, Any]:
        """Analyze ticket metrics and distributions."""
        status_dist = {}
        priority_dist = {}
        stalled_tickets = []
        unassigned_tickets = []
        completed = 0
        in_progress = 0
        new_tickets = 0

        for ticket in self.tickets:
            # Status distribution
            status = ticket["status"]["name"]
            status_dist[status] = status_dist.get(status, 0) + 1
            
            # Priority distribution
            priority = ticket["priority"]["name"]
            priority_dist[priority] = priority_dist.get(priority, 0) + 1
            
            # Track completion
            if status == "Completed":
                completed += 1
            elif status == "In Progress":
                in_progress += 1
            elif status == "New":
                new_tickets += 1
                
            # Track unassigned
            if "actualHours" not in ticket:
                unassigned_tickets.append({
                    "id": ticket["id"],
                    "summary": ticket["summary"]
                })
            
            # Track stalled
            if status == "New" and ticket.get("actualHours", 0) == 0:
                stalled_tickets.append({
                    "id": ticket["id"],
                    "summary": ticket["summary"]
                })

        return {
            "total_tickets": len(self.tickets),
            "status_distribution": status_dist,
            "priority_distribution": priority_dist,
            "completion_metrics": {
                "completed": completed,
                "in_progress": in_progress,
                "new": new_tickets,
                "completion_rate": (completed / len(self.tickets) * 100) if self.tickets else 0
            },
            "stalled_tickets": stalled_tickets,
            "unassigned_tickets": unassigned_tickets
        }

    def _analyze_resources(self) -> Dict[str, Any]:
        """Analyze resource allocation and utilization."""
        member_allocation = {}
        
        # Track ticket assignments
        for ticket in self.tickets:
            assignee = ticket.get("assignedTo", {}).get("identifier")
            if assignee:
                if assignee not in member_allocation:
                    member_allocation[assignee] = {
                        "assigned_tickets": 0,
                        "completed_tickets": 0,
                        "hours_logged": 0
                    }
                member_allocation[assignee]["assigned_tickets"] += 1
                if ticket["status"]["name"] == "Completed":
                    member_allocation[assignee]["completed_tickets"] += 1
                if "actualHours" in ticket:
                    member_allocation[assignee]["hours_logged"] += ticket["actualHours"]

        return {
            "team_size": len(self.members),
            "member_allocation": member_allocation
        }

    def _analyze_risks(self) -> Dict[str, Any]:
        """Identify project risks based on metrics."""
        risks = []
        risk_level = "LOW"
        
        # Check for missing estimates
        if not self.project.get("estimatedHours"):
            risks.append("Missing project hour estimates")
            risk_level = "MEDIUM"
        
        # Check for stalled tickets
        stalled_count = len([t for t in self.tickets if t["status"]["name"] == "New" and t.get("actualHours", 0) == 0])
        if stalled_count > 5:
            risks.append(f"High number of stalled tickets ({stalled_count})")
            risk_level = "HIGH"
        
        # Check for unassigned tickets
        unassigned_count = len([t for t in self.tickets if "actualHours" not in t])
        if unassigned_count > 5:
            risks.append(f"High number of unassigned tickets ({unassigned_count})")
            risk_level = "HIGH"
        
        # Check completion rate
        completed_count = len([t for t in self.tickets if t["status"]["name"] == "Completed"])
        completion_rate = (completed_count / len(self.tickets)) if self.tickets else 0
        if completion_rate < 0.2:
            risks.append(f"Low completion rate ({completion_rate:.1%})")
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "risk_factors": risks
        }

def analyze_project_file(file_path: str) -> Dict[str, Any]:
    """Analyze a project from a JSON file."""
    with open(file_path, 'r') as f:
        project_data = json.load(f)
    
    analyzer = ProjectAnalyzer(project_data)
    return analyzer.analyze()

if __name__ == "__main__":
    # Example usage
    sample_dir = Path(__file__).parent.parent / 'data' / 'samples'
    for project_file in sample_dir.glob('project_*.json'):
        print(f"\nAnalyzing {project_file.name}...")
        analysis = analyze_project_file(str(project_file))
        
        # Save analysis results
        output_file = project_file.parent / f"{project_file.stem}_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis saved to {output_file}") 