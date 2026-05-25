export interface Firmographics {
  industries: string[];
  company_sizes: string[];
  revenue_ranges: string[];
  geographies: string[];
  funding_stages: string[];
  tech_stack_signals: string[];
}

export interface Psychographics {
  goals: string[];
  fears: string[];
  values: string[];
  decision_style: string;
  success_metrics: string[];
}

export interface PainPoint {
  pain: string;
  severity: "high" | "medium" | "low";
  current_solution: string;
  cost_of_inaction: string;
}

export interface ICPProfile {
  id: string;
  profile_name: string;
  firmographics: Firmographics;
  psychographics: Psychographics;
  job_titles: string[];
  seniority_levels: string[];
  departments: string[];
  pain_points: PainPoint[];
  buying_triggers: string[];
  objections: string[];
  channels: string[];
  sample_messaging: string;
  confidence_score: number;
}
