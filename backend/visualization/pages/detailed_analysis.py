"""Detailed project analysis page with AI insights."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

import streamlit as st
import json
from datetime import datetime
import pandas as pd

from backend.analysis.detailed_analyzer import DetailedProjectAnalyzer
from backend.analysis.ai_analyzer import AIProjectAnalyzer

def load_project_data(project_id: int) -> tuple[dict, dict, dict]:
    """Load all analysis data for a project"""
    data_dir = Path('data')
    
    # Load detailed data
    detailed_file = data_dir / 'detailed' / f"project_{project_id}_detailed.json"
    with open(detailed_file) as f:
        detailed_data = json.load(f)
    
    # Load analysis
    analysis_file = data_dir / 'analysis' / f"project_{project_id}_analysis.json"
    with open(analysis_file) as f:
        analysis = json.load(f)
    
    # Load AI analysis
    ai_file = data_dir / 'ai_analysis' / f"project_{project_id}_ai_analysis.json"
    with open(ai_file) as f:
        ai_analysis = json.load(f)
    
    return detailed_data, analysis, ai_analysis

def display_project_header(analysis: dict):
    """Display project header information"""
    st.title(f"Detailed Analysis: {analysis['project_name']}")
    st.write(f"Company: {analysis['company']}")
    st.write(f"Status: {analysis['status']}")
    st.write(f"Project Manager: {analysis['manager']}")

def display_progress_metrics(analysis: dict):
    """Display project progress metrics"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        progress = round((analysis['actual_hours'] or 0) / (analysis['estimated_hours'] or 1) * 100)
        st.metric("Progress", f"{progress}%")
        
    with col2:
        st.metric("Estimated Hours", f"{analysis['estimated_hours']:.1f}")
        
    with col3:
        st.metric("Actual Hours", f"{analysis['actual_hours']:.1f}")

def display_ticket_metrics(analysis: dict):
    """Display ticket-related metrics"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Tickets", analysis['ticket_count'])
        
    with col2:
        st.metric("Active Tickets", analysis['active_tickets'])

def display_ai_insights(ai_analysis: dict):
    """Display AI-generated insights"""
    st.header("AI Analysis Insights")
    
    # Display health score
    health_score = ai_analysis.get('health_score', 0)
    st.progress(health_score / 100)
    st.write(f"Project Health Score: {health_score}/100")
    
    # Progress Analysis
    st.subheader("Progress Analysis")
    st.write(ai_analysis.get('progress_analysis', 'No analysis available'))
    
    # Risks and Blockers
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risks")
        risks = ai_analysis.get('risks', [])
        for risk in risks:
            st.warning(risk)
            
    with col2:
        st.subheader("Blockers")
        blockers = ai_analysis.get('blockers', [])
        for blocker in blockers:
            st.error(blocker)
    
    # Resource Analysis
    st.subheader("Resource Analysis")
    st.write(ai_analysis.get('resource_analysis', 'No analysis available'))
    
    # Recommendations
    st.subheader("Recommendations")
    recommendations = ai_analysis.get('recommendations', [])
    for rec in recommendations:
        st.info(rec)
    
    # Timeline Prediction
    st.subheader("Timeline Prediction")
    st.write(ai_analysis.get('timeline_prediction', 'No prediction available'))

def display_ticket_details(analysis: dict):
    """Display detailed ticket information"""
    st.header("Ticket Details")
    
    # Convert ticket summaries to dataframe
    tickets_df = pd.DataFrame(analysis['ticket_summaries'])
    
    # Add styling
    def color_status(val):
        if val == 'Closed' or val == 'Completed':
            return 'color: green'
        elif val == 'In Progress':
            return 'color: orange'
        else:
            return 'color: red'
    
    # Display styled dataframe
    st.dataframe(
        tickets_df.style.applymap(color_status, subset=['status']),
        use_container_width=True
    )

def main():
    st.set_page_config(
        page_title="Detailed Project Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    # Project selector
    data_dir = Path('data/detailed')
    project_files = list(data_dir.glob('project_*_detailed.json'))
    project_ids = [int(f.stem.split('_')[1]) for f in project_files]
    
    if not project_ids:
        st.error("No project data available. Please run the analysis pipeline first.")
        return
    
    selected_project = st.selectbox(
        "Select Project",
        project_ids,
        format_func=lambda x: f"Project {x}"
    )
    
    try:
        # Load data
        detailed_data, analysis, ai_analysis = load_project_data(selected_project)
        
        # Display sections
        display_project_header(analysis)
        
        st.markdown("---")
        
        # Metrics
        col1, col2 = st.columns(2)
        with col1:
            display_progress_metrics(analysis)
        with col2:
            display_ticket_metrics(analysis)
        
        st.markdown("---")
        
        # AI Insights
        display_ai_insights(ai_analysis)
        
        st.markdown("---")
        
        # Ticket Details
        display_ticket_details(analysis)
        
    except Exception as e:
        st.error(f"Error loading project data: {e}")

if __name__ == "__main__":
    main() 