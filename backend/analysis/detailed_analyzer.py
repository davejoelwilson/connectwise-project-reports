"""Module for analyzing detailed project data and preparing it for AI analysis."""
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import agentops
from functools import wraps

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            agentops.record_error(str(e))
            raise
    return wrapper

class DetailedProjectAnalyzer:
    def __init__(self, project_data: Dict[str, Any]):
        self.project_data = project_data
        self.project = project_data['project']
        self.tickets = project_data['tickets']
        self.ticket_details = project_data['ticket_details']
        self.project_notes = project_data['project_notes']
        self.time_entries = project_data['project_time_entries']
        self.members = project_data['members']

    @handle_errors
    def analyze(self) -> Dict[str, Any]:
        """Run all analysis and return combined metrics."""
        return {
            "project_metrics": self._analyze_project_metrics(),
            "ticket_analysis": self._analyze_tickets(),
            "resource_metrics": self._analyze_resources(),
            "risk_indicators": self._analyze_risks(),
            "tickets": self.tickets  # Add raw tickets to output
        }

    @handle_errors
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

    @handle_errors
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

    @handle_errors
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

    @handle_errors
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

    def analyze_ticket_progress(self, ticket_id: int) -> dict:
        """Analyze progress and timeline of a specific ticket"""
        # Convert ticket_id to string for dictionary lookup
        ticket_data = self.ticket_details[str(ticket_id)]
        ticket = ticket_data['ticket']
        notes = ticket_data['notes']
        time_entries = ticket_data['time_entries']

        # Analyze notes for status changes and key updates
        status_changes = []
        key_updates = []
        for note in sorted(notes, key=lambda x: x.get('dateCreated', ''), reverse=True):
            if 'dateCreated' not in note or 'text' not in note:
                continue
                
            text = note['text'].lower()
            date = note['dateCreated']
            
            # Look for status change indicators
            if 'status changed to' in text or 'moved to' in text:
                status_changes.append({
                    'date': date,
                    'text': note.get('text', ''),
                    'by': note.get('createdBy', 'Unknown')
                })
            
            # Look for key update indicators
            if any(key in text for key in ['completed', 'blocked', 'updated', 'fixed', 'implemented']):
                key_updates.append({
                    'date': date,
                    'text': note.get('text', ''),
                    'by': note.get('createdBy', 'Unknown')
                })

        # Analyze time entries
        time_analysis = {
            'total_hours': ticket.get('actualHours', 0),  # Use ticket's actualHours instead
            'entries_by_date': {},
            'contributors': set(),
            'notes': []  # Add notes from time entries
        }

        for entry in time_entries:
            if '_info' in entry and 'notes' in entry['_info']:
                time_analysis['notes'].append(entry['_info']['notes'])
                
            # We don't have timeStart in the data, so skip the date analysis
            if 'member/identifier' in entry:
                time_analysis['contributors'].add(entry['member/identifier'])

        return {
            'ticket_id': ticket_id,
            'summary': ticket.get('summary', ''),
            'current_status': ticket.get('status', {}).get('name', 'Unknown'),
            'assigned_to': ticket.get('assignedTo/identifier'),
            'date_entered': ticket.get('dateEntered'),
            'estimated_hours': ticket.get('estimatedHours', 0),
            'actual_hours': ticket.get('actualHours', 0),
            'status_changes': status_changes,
            'key_updates': key_updates,
            'time_analysis': time_analysis
        }

    def analyze_project_timeline(self) -> dict:
        """Analyze the overall project timeline and progress"""
        
        # Collect all status changes and updates
        all_status_changes = []
        all_time_entries = []
        ticket_summaries = []

        for ticket_id_str, details in self.ticket_details.items():
            analysis = self.analyze_ticket_progress(int(ticket_id_str))
            all_status_changes.extend(analysis['status_changes'])
            
            # Create ticket summary
            ticket_summaries.append({
                'id': int(ticket_id_str),  # Convert back to int for consistency
                'summary': analysis['summary'],
                'status': analysis['current_status'],
                'progress': min(100, round((analysis['actual_hours'] or 0) / (analysis['estimated_hours'] or 1) * 100)),
                'key_updates': len(analysis['key_updates'])
            })

        # Analyze project notes
        project_updates = []
        for note in self.project_notes:
            if 'dateCreated' not in note:
                continue  # Skip notes without dateCreated field
            project_updates.append({
                'date': note.get('dateCreated'),
                'text': note.get('text', ''),
                'by': note.get('createdBy', 'Unknown')
            })

        return {
            'project_id': self.project['id'],
            'project_name': self.project['name'],
            'status': self.project['status']['name'],
            'manager': self.project['manager']['identifier'],
            'company': self.project.get('company', {}).get('name'),
            'estimated_hours': self.project['estimatedHours'],
            'actual_hours': self.project['actualHours'],
            'ticket_count': len(self.tickets),
            'active_tickets': sum(1 for t in ticket_summaries if t['status'] not in ['Closed', 'Completed']),
            'ticket_summaries': ticket_summaries,
            'project_updates': sorted(project_updates, key=lambda x: x['date'], reverse=True),
            'team_members': [m.get('identifier', str(m['id'])) for m in self.members],
            'analysis_date': datetime.now().isoformat()
        }

    def prepare_ai_prompt(self) -> str:
        """Prepare a detailed prompt for AI analysis"""
        timeline = self.analyze_project_timeline()
        
        prompt = f"""Analyze the following project data and provide insights:

Project: {timeline['project_name']} (ID: {timeline['project_id']})
Company: {timeline['company']}
Status: {timeline['status']}
Manager: {timeline['manager']}

Progress:
- Estimated Hours: {timeline['estimated_hours']}
- Actual Hours: {timeline['actual_hours']}
- Completion: {round((timeline['actual_hours'] or 0) / (timeline['estimated_hours'] or 1) * 100)}%

Tickets:
- Total: {timeline['ticket_count']}
- Active: {timeline['active_tickets']}
- Team Size: {len(timeline['team_members'])}

Recent Updates:
{chr(10).join(f"- {update['date']}: {update['text'][:100]}..." for update in timeline['project_updates'][-5:])}

Active Tickets:
{chr(10).join(f"- {t['summary']} ({t['status']}, {t['progress']}% complete)" for t in timeline['ticket_summaries'] if t['status'] not in ['Closed', 'Completed'])}

Please analyze:
1. Overall project health and progress
2. Any risks or blockers
3. Resource allocation and team performance
4. Recommendations for improvement
5. Timeline predictions
"""
        return prompt

@handle_errors
def analyze_project_file(file_path: str) -> Dict[str, Any]:
    """Analyze a project from a JSON file."""
    with open(file_path, 'r') as f:
        project_data = json.load(f)
    
    analyzer = DetailedProjectAnalyzer(project_data)
    return analyzer.analyze() 