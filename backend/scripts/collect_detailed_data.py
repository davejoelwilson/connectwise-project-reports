#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional

from backend.connectwise.client import ConnectWiseClient

async def collect_ticket_details(client: ConnectWiseClient, ticket_id: int) -> dict:
    """Collect all details for a single ticket including notes, time entries, and status"""
    
    # Get basic ticket info
    ticket = await client.get_ticket(ticket_id)
    
    # Get ticket notes
    notes = await client.get_ticket_notes(ticket_id)
    
    # Get time entries
    time_entries = await client.get_ticket_time_entries(ticket_id)
    
    # Get member details for anyone involved
    member_ids = {
        ticket.get('assignedTo', {}).get('identifier'),
        *(entry.get('member', {}).get('identifier') for entry in time_entries),
        *(note.get('createdBy') for note in notes)
    }
    member_ids.discard(None)
    
    members = await client.get_members({
        'conditions': f"identifier IN ({','.join(member_ids)})"
    }) if member_ids else []
    
    return {
        'ticket': ticket,
        'notes': notes,
        'time_entries': time_entries,
        'members': members,
        'collected_at': datetime.now().isoformat()
    }

async def collect_project_detailed_data(client: ConnectWiseClient, project_id: int) -> dict:
    """Collect detailed data for a project including all ticket details"""
    
    # Get project data first
    project_data = await client.get_project(project_id)
    project_notes = await client.get_project_notes(project_id)
    
    # Get all tickets for the project
    tickets = await client.get_project_tickets(project_id)
    
    # Collect detailed data for each ticket
    ticket_details = {}
    for ticket in tickets:
        ticket_id = str(ticket['id'])  # Convert to string
        ticket_details[ticket_id] = await collect_ticket_details(client, int(ticket_id))
    
    # Get all time entries for the project
    time_entries = await client.get_time_entries({
        'conditions': f'chargeToId={project_id} AND chargeToType="Project"'
    })
    
    # Get all members involved
    member_ids = {
        project_data.get('manager', {}).get('identifier'),
        *(entry.get('member', {}).get('identifier') for entry in time_entries),
        *(ticket.get('assignedTo', {}).get('identifier') for ticket in tickets),
        *(note.get('createdBy') for note in project_notes)
    }
    member_ids.discard(None)
    
    members = await client.get_members({
        'conditions': f"identifier IN ({','.join(member_ids)})"
    }) if member_ids else []
    
    return {
        'project': project_data,
        'project_notes': project_notes,
        'tickets': tickets,
        'ticket_details': ticket_details,
        'project_time_entries': time_entries,
        'members': members,
        'collected_at': datetime.now().isoformat()
    }

async def main():
    client = ConnectWiseClient()
    
    # Create output directory if it doesn't exist
    output_dir = Path('data/detailed')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Get all active projects
        projects = await client.get_projects({
            'conditions': "status/name='Active'"
        })
        
        # Collect detailed data for each project
        for project in projects:
            project_id = project['id']
            print(f"Collecting detailed data for project {project_id}...")
            
            try:
                detailed_data = await collect_project_detailed_data(client, project_id)
                
                # Save to file
                output_file = output_dir / f"project_{project_id}_detailed.json"
                with open(output_file, 'w') as f:
                    json.dump(detailed_data, f, indent=2)
                print(f"Saved detailed data for project {project_id}")
                
            except Exception as e:
                print(f"Error collecting data for project {project_id}: {e}")
                continue
            
    finally:
        await client.http_client.aclose()

if __name__ == '__main__':
    asyncio.run(main()) 