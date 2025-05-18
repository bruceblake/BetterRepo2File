export interface Job {
  job_id: string;
  status: 'processing' | 'completed' | 'error';
  phase: string;
  current: number;
  total: number;
  error?: string;
  result?: JobResult;
}

export interface JobResult {
  copy_text: string;
  manifest_html: string;
  skipped_md: string;
  stats: {
    used: number;
    budget: number;
  };
}

export type Stage = 'A' | 'B' | 'C';

export interface WizardState {
  vibe: string;
  stage: Stage;
  repoFile?: File;
  plannerOutput?: string;
  previousOutput?: File;
  feedbackLog?: File;
}