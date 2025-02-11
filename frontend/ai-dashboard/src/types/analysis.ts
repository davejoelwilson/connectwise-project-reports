export interface ProgressAnalysis {
  summary: string;
  completion_rate: number;
  on_track: boolean;
  concerns: string[];
}

export interface Risk {
  level: 'LOW' | 'MEDIUM' | 'HIGH';
  factors: string[];
  mitigation_suggestions: string[];
}

export interface Blockers {
  current_blockers: string[];
  potential_blockers: string[];
}

export interface ResourceAnalysis {
  summary: string;
  concerns: string[];
  recommendations: string[];
}

export interface Recommendations {
  immediate_actions: string[];
  long_term_improvements: string[];
}

export interface TimelinePrediction {
  likely_completion: string;
  confidence: number;
  factors_affecting_timeline: string[];
}

export interface AIAnalysis {
  health_score: number;
  project_name: string;
  company_name: string;
  progress_analysis: ProgressAnalysis;
  risks: Risk;
  blockers: Blockers;
  resource_analysis: ResourceAnalysis;
  recommendations: Recommendations;
  timeline_prediction: TimelinePrediction;
  analyzed_at: string;
  model_version: string;
}

export interface ProjectSummary {
  id: number;
  name: string;
  company: string;
  status: string;
  manager: string;
  estimated_hours: number;
  actual_hours: number;
  ticket_count: number;
  active_tickets: number;
} 