export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface CandidateSkill {
  id: number;
  name: string;
  normalized_name?: string;
  category?: string;
  proficiency_level?: string;
  years_of_experience?: number;
  is_verified: boolean;
  source: string;
  evidence?: string;
}

export interface CandidateExperience {
  id: number;
  title: string;
  company: string;
  location?: string;
  employment_type?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  technologies: string[];
  achievements: string[];
}

export interface CandidateProject {
  id: number;
  name: string;
  description?: string;
  technologies: string[];
  url?: string;
  role?: string;
  highlights: string[];
}

export interface CandidateEducation {
  id: number;
  degree: string;
  field_of_study?: string;
  institution: string;
  location?: string;
  start_year?: number;
  end_year?: number;
  gpa?: string;
  achievements: string[];
}

export interface CandidateCertification {
  id: number;
  name: string;
  issuing_organization?: string;
  issue_date?: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
}

export interface CandidateProfile {
  id: number;
  user_id: number;
  headline?: string;
  summary?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  total_experience_years?: number;
  current_role?: string;
  current_company?: string;
  education_level?: string;
  profile_completeness: number;
  ai_extracted: boolean;
  last_analyzed_at?: string;
  skills: CandidateSkill[];
  experiences: CandidateExperience[];
  projects: CandidateProject[];
  education: CandidateEducation[];
  certifications: CandidateCertification[];
}

export interface CareerPreference {
  id: number;
  preferred_roles: string[];
  preferred_locations: string[];
  preferred_work_modes: string[];
  preferred_employment_types: string[];
  experience_level?: string;
  min_salary?: number;
  max_salary?: number;
  salary_currency: string;
  notice_period_days?: number;
  willing_to_relocate: boolean;
}

export interface JobListing {
  id: number;
  title: string;
  company: string;
  company_logo_url?: string;
  description?: string;
  description_html?: string;
  responsibilities?: string[];
  required_skills: string[];
  preferred_skills: string[];
  min_experience_years?: number;
  max_experience_years?: number;
  location?: string;
  work_mode?: string;
  employment_type?: string;
  min_salary?: number;
  max_salary?: number;
  salary_currency?: string;
  salary_period?: string;
  date_posted?: string;
  source_name?: string;
  source_url?: string;
  apply_url?: string;
  is_active: boolean;
  last_verified_at?: string;
}

export interface JobSearchResponse {
  jobs: JobListing[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface JobSource {
  id: number;
  name: string;
  source_type: string;
  is_active: boolean;
  is_configured: boolean;
  last_sync_at?: string;
  total_listings: number;
  last_error?: string;
}

export interface MatchEvidence {
  claim: string;
  source: string;
  text: string;
}

export interface JobMatch {
  id: number;
  listing: JobListing;
  overall_score: number;
  required_skill_score: number;
  preferred_skill_score: number;
  experience_score: number;
  semantic_score: number;
  preference_score: number;
  is_eligible: boolean;
  eligibility_warnings: string[];
  matched_skills: string[];
  missing_skills: string[];
  explanation?: string;
  evidence: MatchEvidence[];
  scoring_version: string;
}

export interface CareerRecommendation {
  role_title: string;
  fit_score: number;
  why_it_fits: string;
  relevant_skills: string[];
  relevant_experience: string[];
  missing_skills: string[];
  entry_level_considerations?: string;
  recommended_next_steps: string[];
  alternative_paths: string[];
  confidence: string;
}

export interface CareerAnalysisResponse {
  recommendations: CareerRecommendation[];
  profile_summary: string;
  overall_readiness: string;
  warnings: string[];
  generated_at: string;
}

export interface LearningItemResource {
  title: string;
  url: string;
  type: string;
}

export interface LearningItemProject {
  title: string;
  description: string;
}

export interface LearningItem {
  id: number;
  skill_name: string;
  category?: string;
  priority: string;
  why_important?: string;
  week_number?: number;
  estimated_hours?: number;
  resources: LearningItemResource[];
  practice_projects: LearningItemProject[];
  is_completed: boolean;
  completed_at?: string;
  evidence?: string;
}

export interface LearningRoadmap {
  id: number;
  target_role: string;
  description?: string;
  total_weeks?: number;
  hours_per_week: number;
  overall_progress: number;
  ai_generated: boolean;
  items: LearningItem[];
  created_at: string;
}

export interface GeneratedDocument {
  id: number;
  document_type: string;
  title?: string;
  content?: string;
  content_html?: string;
  file_path?: string;
  template_name?: string;
  version: number;
  listing_id?: number;
  created_at: string;
  updated_at: string;
}

export interface ApplicationStatusHistory {
  id: number;
  from_status?: string;
  to_status: string;
  notes?: string;
  changed_at: string;
}

export interface Application {
  id: number;
  listing_id?: number;
  status: 'saved' | 'preparing' | 'ready_to_apply' | 'applied' | 'assessment' | 'interview' | 'rejected' | 'offer' | 'withdrawn';
  applied_at?: string;
  company_name?: string;
  job_title?: string;
  source_url?: string;
  apply_url?: string;
  notes?: string;
  next_step?: string;
  next_step_date?: string;
  status_history: ApplicationStatusHistory[];
  created_at: string;
  updated_at: string;
}

export interface AnalyticsResponse {
  total_jobs_discovered: number;
  relevant_matches: number;
  saved_jobs: number;
  applications_submitted: number;
  interviews: number;
  offers: number;
  conversion_rate?: number;
  skill_gaps: { skill: string; frequency: number }[];
  application_timeline: { stage: string; count: number }[];
  learning_progress: number;
}
