#!/usr/bin/env python3
import asyncio
import json
from datetime import datetime
from pathlib import Path
from connectwise.client import ConnectWiseClient

async def collect_project_data(client: ConnectWiseClient, project_id: int) -> dict:
    """Collect all relevant data for a single project"""
    
    # Get basic project info
    project = await client.get_project(project_id)
    
    # Get project notes
    notes = await client.get_project_notes(project_id)
    
    # Get project tickets
    tickets = await client.get_project_tickets(project_id)
    
    # Get time entries for project
    time_entries = await client.get_time_entries({
        'conditions': f'chargeToId={project_id} AND chargeToType="Project"'
    })
    
    # Get all members involved
    member_ids = {
        project.get('manager', {}).get('identifier'),
        *(entry.get('member', {}).get('identifier') for entry in time_entries),
        *(ticket.get('assignedTo', {}).get('identifier') for ticket in tickets)
    }
    member_ids.discard(None)
    
    members = await client.get_members({
        'conditions': f"identifier IN ({','.join(member_ids)})"
    }) if member_ids else []
    
    return {
        'project': project,
        'notes': notes,
        'tickets': tickets,
        'time_entries': time_entries,
        'members': members,
        'collected_at': datetime.now().isoformat()
    }

async def main():
    """Main function to collect sample data"""
    client = ConnectWiseClient()
    
    try:
        # Get a list of recent projects
        projects = await client.get_projects({
            'page': 1,
            'pageSize': 5,  # Get 5 recent projects
            'orderBy': 'lastUpdated desc'
        })
        
        # Create data directory if it doesn't exist
        data_dir = Path(__file__).parent.parent / 'data' / 'samples'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect data for each project
        for project in projects:
            project_id = project['id']
            print(f"Collecting data for project {project_id}: {project.get('name', 'Unknown')}")
            
            data = await collect_project_data(client, project_id)
            
            # Save to file
            output_file = data_dir / f"project_{project_id}_sample.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Saved data to {output_file}")
    
    finally:
        await client.close()

if __name__ == '__main__':
    asyncio.run(main()) 