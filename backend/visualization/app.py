"""Streamlit app for ConnectWise Project Analysis visualization."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from backend.analysis.project_analyzer import analyze_project_file

def create_status_chart(project_data):
    """Create a donut chart for ticket status distribution."""
    status_dist = project_data['ticket_analysis']['status_distribution']
    fig = go.Figure(data=[go.Pie(
        labels=list(status_dist.keys()),
        values=list(status_dist.values()),
        hole=.3,
        marker_colors=['#2ecc71', '#3498db', '#e74c3c', '#f1c40f']
    )])
    fig.update_layout(title="Ticket Status Distribution")
    return fig

def create_priority_chart(project_data):
    """Create a bar chart for ticket priority distribution."""
    priority_dist = project_data['ticket_analysis']['priority_distribution']
    fig = go.Figure(data=[go.Bar(
        x=list(priority_dist.keys()),
        y=list(priority_dist.values()),
        marker_color='#3498db'
    )])
    fig.update_layout(title="Ticket Priority Distribution")
    return fig

def get_project_engineers(project_data):
    """Get unique list of engineers assigned to tickets."""
    engineers = set()
    for ticket in project_data.get('tickets', []):
        if ticket.get('assignedTo', {}).get('identifier'):
            engineers.add(ticket['assignedTo']['identifier'])
    return sorted(list(engineers))

def display_project_header(project_data):
    """Display project header with customer and engineers."""
    metrics = project_data['project_metrics']
    
    # Get company name from project metrics
    company_name = metrics['company']
    engineers = get_project_engineers(project_data)
    
    st.markdown(f"### 📁 {metrics['name']}")
    st.markdown(f"**Customer:** {company_name}")
    if engineers:
        st.markdown(f"**Engineers:** {', '.join(engineers)}")
    st.markdown("---")

def display_project_metrics(project_data):
    """Display key project metrics in columns."""
    metrics = project_data['project_metrics']
    completion = project_data['ticket_analysis']['completion_metrics']
    
    # Display status separately with full width
    st.markdown(f"**Project Status:** {metrics['status']}")
    st.markdown("---")
    
    # Use columns for the numeric metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Actual Hours", f"{metrics['hours']['actual']:.1f}")
    with col2:
        st.metric("Completion Rate", f"{completion['completion_rate']:.1f}%")

def display_risk_indicators(project_data):
    """Display risk indicators with appropriate styling."""
    risk_level = project_data['risk_indicators']['risk_level']
    risk_color = {
        'LOW': 'green',
        'MEDIUM': 'orange',
        'HIGH': 'red'
    }.get(risk_level, 'gray')
    
    st.subheader("Risk Assessment")
    st.markdown(f"**Risk Level:** :{risk_color}[{risk_level}]")
    
    if project_data['risk_indicators']['risk_factors']:
        st.warning("Risk Factors")
        for risk in project_data['risk_indicators']['risk_factors']:
            st.markdown(f"- {risk}")

def display_stalled_tickets(project_data):
    """Display stalled tickets if any exist."""
    stalled = project_data['ticket_analysis']['stalled_tickets']
    if stalled:
        st.error(f"Stalled Tickets ({len(stalled)}):")
        for ticket in stalled:
            st.markdown(f"- {ticket['summary']} (ID: {ticket['id']})")

def display_ticket_table(project_data):
    """Display a table of all tickets in the project."""
    # Safely get tickets with error handling
    tickets = project_data.get('tickets', [])
    if not tickets:
        st.info("No tickets found in this project")
        return
    
    try:
        # Create DataFrame for better display
        df = pd.DataFrame([{
            'ID': ticket.get('id', 'N/A'),
            'Summary': ticket.get('summary', 'No summary'),
            'Status': ticket.get('status', {}).get('name', 'Unknown'),
            'Hours': ticket.get('actualHours', 0),
            'Priority': ticket.get('priority', {}).get('name', 'Unknown')
        } for ticket in tickets])
        
        # Sort by status and then ID
        df = df.sort_values(['Status', 'ID'])
        
        # Calculate total hours
        total_hours = df['Hours'].sum()
        
        with st.expander("📋 Ticket Details", expanded=True):
            # Show ticket count and total hours
            st.markdown(f"**Total Tickets:** {len(tickets)} | **Total Hours:** {total_hours:.1f}")
            
            # Display the table with custom formatting
            st.dataframe(
                df,
                column_config={
                    'ID': st.column_config.NumberColumn(
                        'Ticket ID',
                        help='ConnectWise ticket identifier'
                    ),
                    'Summary': st.column_config.TextColumn(
                        'Summary',
                        width='large'
                    ),
                    'Status': st.column_config.TextColumn(
                        'Status',
                        width='medium'
                    ),
                    'Hours': st.column_config.NumberColumn(
                        'Hours',
                        format="%.1f",
                        help='Actual hours logged'
                    ),
                    'Priority': st.column_config.TextColumn(
                        'Priority',
                        width='medium'
                    )
                },
                hide_index=True,
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Error displaying ticket table: {str(e)}")
        st.info("Please check the data structure of the project")

def get_all_analyses():
    """Get analyses for all projects."""
    sample_dir = Path(__file__).parent.parent / 'data' / 'samples'
    analyses = []
    
    for project_file in sample_dir.glob("project_*.json"):
        if '_analysis' not in project_file.name:
            analysis = analyze_project_file(str(project_file))
            analyses.append(analysis)
    
    return analyses

def filter_projects(analyses, search_term="", risk_level=None, risk_factor=None):
    """Filter projects based on search term and risk criteria."""
    filtered = analyses
    
    # Text search filter
    if search_term:
        search_term = search_term.lower()
        filtered = [
            analysis for analysis in filtered
            if search_term in analysis['project_metrics']['name'].lower()
            or search_term in analysis.get('project_metrics', {}).get('company_name', '').lower()
        ]
    
    # Risk level filter
    if risk_level:
        filtered = [
            analysis for analysis in filtered
            if analysis['risk_indicators']['risk_level'] == risk_level
        ]
    
    # Risk factor filter
    if risk_factor:
        filtered = [
            analysis for analysis in filtered
            if any(risk_factor.lower() in factor.lower() 
                  for factor in analysis['risk_indicators']['risk_factors'])
        ]
    
    return filtered

def sort_projects(analyses, sort_by="name"):
    """Sort projects based on given criteria."""
    if sort_by == "name":
        return sorted(analyses, key=lambda x: x['project_metrics']['name'])
    elif sort_by == "company":
        return sorted(analyses, key=lambda x: x['project_metrics'].get('company_name', ''))
    elif sort_by == "hours":
        return sorted(analyses, key=lambda x: x['project_metrics']['hours']['actual'], reverse=True)
    elif sort_by == "completion":
        return sorted(analyses, key=lambda x: x['ticket_analysis']['completion_metrics']['completion_rate'], reverse=True)
    elif sort_by == "risk":
        risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        return sorted(analyses, key=lambda x: risk_order[x['risk_indicators']['risk_level']])
    return analyses

def main():
    st.set_page_config(
        page_title="ConnectWise Project Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    # Initialize session state
    if 'analyses' not in st.session_state:
        st.session_state.analyses = []
    if 'risk_level_filter' not in st.session_state:
        st.session_state.risk_level_filter = None
    if 'risk_factor_filter' not in st.session_state:
        st.session_state.risk_factor_filter = None
    
    # Sidebar
    with st.sidebar:
        st.title("🔧 Controls")
        
        # Run Analysis Button
        if st.button("🔄 Run Analysis", type="primary", use_container_width=True):
            with st.spinner("Running analysis..."):
                st.session_state.analyses = get_all_analyses()
        
        if len(st.session_state.analyses) > 0:
            st.divider()
            
            # Search
            search = st.text_input(
                "🔍 Search projects",
                placeholder="Type to filter projects...",
                help="Filter by project or company name"
            )
            
            # Sort
            sort_by = st.selectbox(
                "📋 Sort by",
                options=[
                    "name",
                    "company",
                    "hours",
                    "completion",
                    "risk"
                ],
                format_func=lambda x: {
                    "name": "Project Name (A-Z)",
                    "company": "Company Name (A-Z)",
                    "hours": "Hours (High to Low)",
                    "completion": "Completion Rate (High to Low)",
                    "risk": "Risk Level (High to Low)"
                }[x]
            )
            
            st.divider()
            
            # Risk Filters
            st.markdown("### Risk Filters")
            
            # Risk Level Quick Filters
            st.markdown("**🎯 Risk Level**")
            risk_cols = st.columns(3)
            with risk_cols[0]:
                high = st.button("🔴 HIGH", help="Show only HIGH risk projects", use_container_width=True)
                if high:
                    st.session_state.risk_level_filter = "HIGH"
                    st.session_state.risk_factor_filter = None
            with risk_cols[1]:
                medium = st.button("🟡 MED", help="Show only MEDIUM risk projects", use_container_width=True)
                if medium:
                    st.session_state.risk_level_filter = "MEDIUM"
                    st.session_state.risk_factor_filter = None
            with risk_cols[2]:
                low = st.button("🟢 LOW", help="Show only LOW risk projects", use_container_width=True)
                if low:
                    st.session_state.risk_level_filter = "LOW"
                    st.session_state.risk_factor_filter = None
            
            # Risk Factor Filters
            st.markdown("**⚠️ Risk Factors**")
            if st.button("Stalled Tickets", help="Show projects with stalled tickets", use_container_width=True):
                st.session_state.risk_factor_filter = "stalled tickets"
                st.session_state.risk_level_filter = None
            if st.button("Missing Estimates", help="Show projects missing estimates", use_container_width=True):
                st.session_state.risk_factor_filter = "Missing estimates"
                st.session_state.risk_level_filter = None
            if st.button("Unassigned Tickets", help="Show projects with unassigned tickets", use_container_width=True):
                st.session_state.risk_factor_filter = "unassigned tickets"
                st.session_state.risk_level_filter = None
            
            st.divider()
            
            # Clear Filters
            if st.button("🔄 Clear All Filters", type="secondary", use_container_width=True):
                st.session_state.risk_level_filter = None
                st.session_state.risk_factor_filter = None
    
    # Main Content
    st.title("📊 ConnectWise Project Analysis")
    
    if len(st.session_state.analyses) > 0:
        # Filter and sort analyses
        filtered_analyses = filter_projects(
            st.session_state.analyses,
            search,
            st.session_state.risk_level_filter,
            st.session_state.risk_factor_filter
        )
        sorted_analyses = sort_projects(filtered_analyses, sort_by)
        
        # Show active filters and count
        col1, col2 = st.columns([3, 1])
        with col1:
            active_filters = []
            if st.session_state.risk_level_filter:
                active_filters.append(f"Risk Level: {st.session_state.risk_level_filter}")
            if st.session_state.risk_factor_filter:
                active_filters.append(f"Risk Factor: {st.session_state.risk_factor_filter}")
            if active_filters:
                st.markdown("**Active Filters:** " + " | ".join(active_filters))
        with col2:
            st.markdown(f"*Showing {len(filtered_analyses)} of {len(st.session_state.analyses)} projects*")
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["📊 Dashboard View", "📋 Detailed View"])
        
        with tab1:
            # Single column layout for project cards
            for analysis in sorted_analyses:
                with st.container():
                    display_project_header(analysis)
                    
                    # Create two columns for metrics and charts
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        display_project_metrics(analysis)
                        
                        # Risk summary
                        risk_level = analysis['risk_indicators']['risk_level']
                        risk_color = {'LOW': 'green', 'MEDIUM': 'orange', 'HIGH': 'red'}.get(risk_level, 'gray')
                        st.markdown(f"**Risk Level:** :{risk_color}[{risk_level}]")
                        
                        if analysis['risk_indicators']['risk_factors']:
                            with st.expander("⚠️ Risk Factors"):
                                for risk in analysis['risk_indicators']['risk_factors']:
                                    st.markdown(f"- {risk}")
                    
                    with col2:
                        # Charts side by side
                        subcol1, subcol2 = st.columns(2)
                        with subcol1:
                            st.plotly_chart(
                                create_status_chart(analysis), 
                                use_container_width=True,
                                key=f"status_chart_dash_{analysis['project_metrics']['name']}"
                            )
                        with subcol2:
                            st.plotly_chart(
                                create_priority_chart(analysis), 
                                use_container_width=True,
                                key=f"priority_chart_dash_{analysis['project_metrics']['name']}"
                            )
                    
                    # Add ticket table below charts
                    display_ticket_table(analysis)
                    st.divider()
        
        with tab2:
            # Original detailed view
            for analysis in sorted_analyses:
                display_project_header(analysis)
                display_project_metrics(analysis)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(
                        create_status_chart(analysis), 
                        use_container_width=True,
                        key=f"status_chart_detail_{analysis['project_metrics']['name']}"
                    )
                with col2:
                    st.plotly_chart(
                        create_priority_chart(analysis), 
                        use_container_width=True,
                        key=f"priority_chart_detail_{analysis['project_metrics']['name']}"
                    )
                
                display_risk_indicators(analysis)
                display_ticket_table(analysis)
                display_stalled_tickets(analysis)
                st.divider()
        
        if not filtered_analyses:
            st.info("No projects match your search criteria")
    
    else:
        st.info("Click 'Run Analysis' in the sidebar to load project data")

if __name__ == "__main__":
    main() 