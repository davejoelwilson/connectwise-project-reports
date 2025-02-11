# Project Analysis Documentation

## V1 Implementation (2025-02-11)

### Overview
First version of automated project analysis that processes ConnectWise project data to generate insights about project health, risks, and resource allocation.

### Key Files
```
backend/
├── analysis/
│   ├── __init__.py          # Package exports
│   └── project_analyzer.py   # Core analysis logic
└── scripts/
    └── analyze_projects.py   # CLI runner script
```

### Core Components

#### ProjectAnalyzer Class (`project_analyzer.py`)
- **Purpose**: Analyzes raw project data and generates structured metrics
- **Input**: JSON project data with structure:
  - project: Basic project info
  - tickets: List of project tickets
  - time_entries: Time tracking data
  - notes: Project notes
  - members: Team member data

#### Analysis Categories
1. **Project Metrics**
   - Project ID and name
   - Actual vs estimated hours
   - Project status
   - Start date
   - Project manager

2. **Ticket Analysis**
   - Total ticket count
   - Status distribution
   - Priority distribution
   - Completion metrics
   - Stalled tickets
   - Unassigned tickets

3. **Resource Metrics**
   - Team size
   - Member allocation
   - Ticket assignments
   - Hours logged

4. **Risk Indicators**
   - Risk level (LOW/MEDIUM/HIGH)
   - Missing estimates
   - Stalled tickets (>5 triggers HIGH)
   - Unassigned tickets (>5 triggers HIGH)
   - Low completion rate (<20% triggers MEDIUM)

### Analysis Rules

#### Completion Rate Calculation
```python
completion_rate = (completed_tickets / total_tickets) * 100
where:
- completed_tickets = count of tickets with status "Completed"
- total_tickets = total number of tickets in project
```

#### Risk Level Determination
Risk levels escalate based on severity:
1. Starts at "LOW"
2. Escalates to "MEDIUM" if any of:
   - Missing project hour estimates
   - Completion rate < 20%
3. Escalates to "HIGH" if any of:
   - More than 5 stalled tickets
   - More than 5 unassigned tickets

#### Ticket Classifications
1. **Stalled Ticket**: A ticket that:
   - Has status "New"
   - Has 0 actual hours logged
   - No recent activity

2. **Unassigned Ticket**: A ticket that:
   - Has no actual hours logged
   - May indicate no work started or tracking issues

#### Resource Metrics
1. **Team Size**: Count of unique members in project
2. **Member Allocation**:
   ```python
   per_member = {
       "assigned_tickets": count of tickets assigned,
       "completed_tickets": count of assigned tickets marked Completed,
       "hours_logged": sum of actual hours on assigned tickets
   }
   ```

#### Status Categories
- **New**: Not started
- **In Progress**: Work has begun
- **Completed**: Work finished
- Other statuses (e.g., "Documentation") counted but not factored in completion rate

### Calculation Examples
From project 3899 (Cybersecurity Program):
```
Completion Rate: 21.9%
- Total Tickets: 31
- Completed: 7
- In Progress: 12
- New: 12

Risk Level: HIGH
- Missing estimates (triggers MEDIUM)
- 7 stalled tickets (triggers HIGH)
- 10 unassigned tickets (triggers HIGH)
```

### Known Calculation Limitations
1. Completion rate doesn't consider ticket size/complexity
2. Stalled tickets only based on "New" status and hours
3. Risk levels don't consider:
   - Project value/priority
   - Client importance
   - Security implications
   - Timeline pressure

### Future Calculation Improvements
1. Weighted completion rate based on ticket size
2. More sophisticated stalled ticket detection:
   - Time since last update
   - Dependencies
   - Priority level
3. Enhanced risk scoring:
   - Project type considerations
   - Client SLA factors
   - Resource availability impact
4. Velocity metrics:
   - Average completion time
   - Burndown rate
   - Resource efficiency

### Usage
```bash
# Run analysis on all project files
PYTHONPATH=. python backend/scripts/analyze_projects.py
```

### Output
1. **Console Output**
   - Project name and status
   - Hours (actual/estimated)
   - Completion rate
   - Risk level
   - Risk factors
   - Stalled tickets

2. **JSON Analysis File**
   - Location: `backend/data/samples/project_[ID]_analysis.json`
   - Contains full analysis results including raw ticket data
   - Machine-readable format for further processing

3. **Streamlit Visualization**
   - Location: `backend/visualization/app.py`
   - Interactive dashboard showing:
     - Project metrics and status
     - Ticket status distribution (donut chart)
     - Priority distribution (bar chart)
     - Risk assessment with color coding
     - Detailed ticket table (expanded by default)
     - Stalled ticket warnings
   - Features:
     - Project search and filtering
     - Multiple sort options (name, company, hours, completion, risk)
     - Responsive layout with charts
     - Color-coded risk indicators

### Risk Calculation Rules
- **LOW**: No significant issues
- **MEDIUM**: Triggered by:
  - Missing hour estimates
  - Completion rate < 20%
- **HIGH**: Triggered by:
  - >5 stalled tickets
  - >5 unassigned tickets

### Current Limitations
1. No historical trend analysis
2. No velocity calculations
3. No budget tracking
4. No dependency tracking between tickets
5. Limited resource utilization analysis
6. No timeline predictions

### Next Steps
1. Add velocity and burndown metrics
2. Implement trend analysis
3. Add visualization capabilities
4. Set up automated alerting
5. Add timeline predictions
6. Enhance resource analysis

### Sample Analysis Results
From initial run (2025-02-11):
- 5 projects analyzed
- Common issues:
  - All projects missing hour estimates
  - 3 projects with low completion rates
  - 1 project (Cybersecurity Program) with HIGH risk
  - Multiple stalled tickets in security-related tasks 