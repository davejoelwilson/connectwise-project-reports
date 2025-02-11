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
import asyncio

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
    if 'error' in ai_analysis:
        st.error(f"AI Analysis Error: {ai_analysis['error']}")
        return

    # Project Health Score with color coding
    st.header("🎯 Project Health Analysis")
    health_score = ai_analysis.get('health_score', 0)
    color = 'red' if health_score < 40 else 'yellow' if health_score < 70 else 'green'
    st.markdown(f"### Health Score: :{color}[{health_score}/100]")
    
    # Progress Analysis
    st.header("📈 Progress Analysis")
    progress = ai_analysis.get('progress_analysis', {})
    st.markdown(f"**Summary:** {progress.get('summary', 'No summary available')}")
    
    # Progress metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completion Rate", f"{progress.get('completion_rate', 0)}%")
    with col2:
        on_track = progress.get('on_track', False)
        st.metric("On Track", "✅ Yes" if on_track else "❌ No")
    with col3:
        concerns = progress.get('concerns', [])
        st.metric("Concerns", len(concerns))
    
    if concerns:
        with st.expander("View Progress Concerns"):
            for concern in concerns:
                st.warning(concern)
    
    # Risks and Blockers
    st.header("⚠️ Risks & Blockers")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risks")
        risks = ai_analysis.get('risks', {})
        risk_level = risks.get('level', 'UNKNOWN')
        risk_color = {'LOW': 'green', 'MEDIUM': 'yellow', 'HIGH': 'red'}.get(risk_level, 'gray')
        st.markdown(f"**Risk Level:** :{risk_color}[{risk_level}]")
        
        if risks.get('factors'):
            st.markdown("**Risk Factors:**")
            for factor in risks['factors']:
                st.warning(factor)
                
        if risks.get('mitigation_suggestions'):
            with st.expander("View Mitigation Suggestions"):
                for suggestion in risks['mitigation_suggestions']:
                    st.info(suggestion)
    
    with col2:
        st.subheader("Blockers")
        blockers = ai_analysis.get('blockers', {})
        
        if blockers.get('current_blockers'):
            st.markdown("**Current Blockers:**")
            for blocker in blockers['current_blockers']:
                st.error(blocker)
                
        if blockers.get('potential_blockers'):
            with st.expander("View Potential Blockers"):
                for blocker in blockers['potential_blockers']:
                    st.warning(blocker)
    
    # Resource Analysis
    st.header("👥 Resource Analysis")
    resources = ai_analysis.get('resource_analysis', {})
    st.markdown(f"**Summary:** {resources.get('summary', 'No resource analysis available')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if resources.get('concerns'):
            st.markdown("**Resource Concerns:**")
            for concern in resources['concerns']:
                st.warning(concern)
    
    with col2:
        if resources.get('recommendations'):
            st.markdown("**Resource Recommendations:**")
            for rec in resources['recommendations']:
                st.info(rec)
    
    # Recommendations
    st.header("💡 Recommendations")
    recommendations = ai_analysis.get('recommendations', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Immediate Actions")
        for action in recommendations.get('immediate_actions', []):
            st.info(action)
            
    with col2:
        st.subheader("Long-term Improvements")
        for improvement in recommendations.get('long_term_improvements', []):
            st.success(improvement)
    
    # Timeline Prediction
    st.header("🗓️ Timeline Prediction")
    timeline = ai_analysis.get('timeline_prediction', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Likely Completion", timeline.get('likely_completion', 'Unknown'))
        st.metric("Confidence", f"{timeline.get('confidence', 0)}%")
        
    with col2:
        if timeline.get('factors_affecting_timeline'):
            st.markdown("**Factors Affecting Timeline:**")
            for factor in timeline['factors_affecting_timeline']:
                st.info(factor)

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
    
    # Display styled dataframe using the new map method instead of applymap
    st.dataframe(
        tickets_df.style.map(color_status, subset=['status']),
        use_container_width=True
    )

async def run_fresh_analysis(project_id: int, detailed_data: dict) -> dict:
    """Run a fresh AI analysis for the project"""
    try:
        analyzer = DetailedProjectAnalyzer(detailed_data)
        prompt = analyzer.prepare_ai_prompt()
        
        ai_analyzer = AIProjectAnalyzer()
        analysis = await ai_analyzer.analyze_project(prompt, project_id)
        
        if 'error' in analysis:
            raise Exception(analysis['error'])
        
        # Save the new analysis
        data_dir = Path('data')
        ai_file = data_dir / 'ai_analysis' / f"project_{project_id}_ai_analysis.json"
        with open(ai_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return analysis
        
    except Exception as e:
        st.error(f"AI Analysis failed: {str(e)}")
        # Return the previous analysis if available
        try:
            data_dir = Path('data')
            ai_file = data_dir / 'ai_analysis' / f"project_{project_id}_ai_analysis.json"
            if ai_file.exists():
                with open(ai_file) as f:
                    return json.load(f)
        except:
            pass
        
        # Return a basic error structure if all else fails
        return {
            'error': str(e),
            'analyzed_at': datetime.now().isoformat(),
            'status': 'failed'
        }

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
        
        # AI Analysis Section with Refresh Button
        ai_col1, ai_col2 = st.columns([3, 1])
        with ai_col1:
            st.header("AI Analysis Insights")
            if 'analyzed_at' in ai_analysis:
                st.caption(f"Last analyzed: {ai_analysis['analyzed_at']}")
        with ai_col2:
            if st.button("🔄 Run Fresh Analysis", type="primary", help="Generate new AI insights for this project"):
                try:
                    with st.spinner("Running AI analysis..."):
                        # Run fresh analysis
                        new_analysis = asyncio.run(run_fresh_analysis(selected_project, detailed_data))
                        if 'error' not in new_analysis:
                            st.success("Analysis complete!")
                            ai_analysis = new_analysis
                            st.rerun()
                        else:
                            st.error(f"Analysis failed: {new_analysis['error']}")
                except Exception as e:
                    st.error(f"Failed to run analysis: {str(e)}")
        
        # Display AI insights
        display_ai_insights(ai_analysis)
        
        st.markdown("---")
        
        # Ticket Details
        display_ticket_details(analysis)
        
    except Exception as e:
        st.error(f"Error loading project data: {e}")

if __name__ == "__main__":
    main() 