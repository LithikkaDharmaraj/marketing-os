export type WorkflowStep =
  | "intake"
  | "scraping"
  | "cleaning"
  | "extracting"
  | "positioning"
  | "icp_generating"
  | "embedding"
  | "completed"
  | "failed";

export interface WorkflowProgress {
  type: string;
  run_id: string;
  step: WorkflowStep;
  step_label: string;
  steps_done: number;
  steps_total: number;
  percent: number;
  message: string;
  error?: string | null;
}

export interface WorkflowStatus {
  id: string;
  status: WorkflowStep;
  progress: {
    steps_total: number;
    steps_done: number;
    current_step: string;
    percent: number;
  };
  temporal_run_id?: string;
  started_at?: string;
  completed_at?: string;
}
