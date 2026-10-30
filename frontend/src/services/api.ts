/**
 * CareerMap AI - HTTP API Client
 */
import {
  User,
  AuthTokens,
  CandidateProfile,
  CareerPreference,
  JobSearchResponse,
  JobListing,
  JobSource,
  JobMatch,
  CareerAnalysisResponse,
  LearningRoadmap,
  LearningItem,
  GeneratedDocument,
  Application,
  AnalyticsResponse,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class ApiClient {
  private getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
      ...options.headers,
    };

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      // Clear token on unauthorized if not on auth endpoints
      if (!endpoint.startsWith('/auth/login') && !endpoint.startsWith('/auth/register')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }

    if (!res.ok) {
      let errorMessage = `Request failed with status ${res.status}`;
      try {
        const errorData = await res.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // use default error message
      }
      throw new Error(errorMessage);
    }

    if (res.status === 204) {
      return {} as T;
    }

    return res.json();
  }

  // --- Auth ---
  async register(data: { email: string; password: string; full_name: string }): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }): Promise<AuthTokens> {
    const res = await this.request<AuthTokens>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    localStorage.setItem('access_token', res.access_token);
    localStorage.setItem('refresh_token', res.refresh_token);
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // --- Profile ---
  async getProfile(): Promise<CandidateProfile> {
    return this.request<CandidateProfile>('/profile');
  }

  async updateProfile(data: Partial<CandidateProfile>): Promise<CandidateProfile> {
    return this.request<CandidateProfile>('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async addSkill(data: { name: string; category?: string; proficiency_level?: string }): Promise<void> {
    return this.request<void>('/profile/skills', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteSkill(skillId: number): Promise<void> {
    return this.request<void>(`/profile/skills/${skillId}`, {
      method: 'DELETE',
    });
  }

  async addExperience(data: any): Promise<void> {
    return this.request<void>('/profile/experiences', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteExperience(id: number): Promise<void> {
    return this.request<void>(`/profile/experiences/${id}`, {
      method: 'DELETE',
    });
  }

  async addProject(data: any): Promise<void> {
    return this.request<void>('/profile/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteProject(id: number): Promise<void> {
    return this.request<void>(`/profile/projects/${id}`, {
      method: 'DELETE',
    });
  }

  async uploadResume(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_BASE_URL}/profile/resume/upload`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Resume upload failed');
    }
    return res.json();
  }

  async extractResume(resumeId: number): Promise<any> {
    return this.request<any>(`/profile/resume/${resumeId}/extract`, {
      method: 'POST',
    });
  }

  async getPreferences(): Promise<CareerPreference> {
    return this.request<CareerPreference>('/profile/preferences');
  }

  async updatePreferences(data: Partial<CareerPreference>): Promise<CareerPreference> {
    return this.request<CareerPreference>('/profile/preferences', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // --- Jobs ---
  async searchJobs(params: Record<string, any> = {}): Promise<JobSearchResponse> {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, String(val));
      }
    });
    return this.request<JobSearchResponse>(`/jobs?${query.toString()}`);
  }

  async getJobDetail(id: number): Promise<JobListing> {
    return this.request<JobListing>(`/jobs/${id}`);
  }

  async getJobSources(): Promise<JobSource[]> {
    return this.request<JobSource[]>('/jobs/sources');
  }

  async syncJobs(query?: string, location?: string): Promise<{ new_listings_synced: number; message: string }> {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (location) params.append('location', location);
    return this.request(`/jobs/sync?${params.toString()}`, { method: 'POST' });
  }

  async getSavedJobs(): Promise<any[]> {
    return this.request<any[]>('/jobs/saved');
  }

  async saveJob(listingId: number, notes?: string): Promise<any> {
    return this.request<any>('/jobs/saved', {
      method: 'POST',
      body: JSON.stringify({ listing_id: listingId, notes }),
    });
  }

  async unsaveJob(listingId: number): Promise<void> {
    return this.request<void>(`/jobs/saved/${listingId}`, {
      method: 'DELETE',
    });
  }

  // --- Matching ---
  async runMatching(limit: number = 20): Promise<JobMatch[]> {
    return this.request<JobMatch[]>(`/matching/run?limit=${limit}`, {
      method: 'POST',
    });
  }

  async getJobMatch(listingId: number): Promise<JobMatch> {
    return this.request<JobMatch>(`/matching/job/${listingId}`);
  }

  // --- Career Intel ---
  async getCareerRecommendations(refresh: boolean = false): Promise<CareerAnalysisResponse> {
    const query = refresh ? '?refresh=true' : '';
    return this.request<CareerAnalysisResponse>(`/career/recommendations${query}`);
  }

  async compareCareers(roles: string[]): Promise<any> {
    return this.request<any>('/career/compare', {
      method: 'POST',
      body: JSON.stringify({ roles }),
    });
  }

  // --- Learning Roadmaps ---
  async getRoadmaps(): Promise<{ roadmaps: LearningRoadmap[]; total: number }> {
    return this.request<{ roadmaps: LearningRoadmap[]; total: number }>('/learning');
  }

  async generateRoadmap(targetRole: string, hoursPerWeek: number = 10): Promise<LearningRoadmap> {
    return this.request<LearningRoadmap>('/learning/generate', {
      method: 'POST',
      body: JSON.stringify({ target_role: targetRole, hours_per_week: hoursPerWeek }),
    });
  }

  async updateLearningItem(itemId: number, isCompleted: boolean, evidence?: string): Promise<LearningItem> {
    return this.request<LearningItem>(`/learning/items/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify({ is_completed: isCompleted, evidence }),
    });
  }

  // --- Documents Studio ---
  async listDocuments(): Promise<GeneratedDocument[]> {
    return this.request<GeneratedDocument[]>('/documents');
  }

  async generateTailoredResume(listingId: number, customizeInstructions?: string): Promise<GeneratedDocument> {
    return this.request<GeneratedDocument>('/documents/resume', {
      method: 'POST',
      body: JSON.stringify({ listing_id: listingId, customize_instructions: customizeInstructions }),
    });
  }

  async generateCoverLetter(listingId: number, tone: string = 'professional', customizeInstructions?: string): Promise<GeneratedDocument> {
    return this.request<GeneratedDocument>('/documents/cover-letter', {
      method: 'POST',
      body: JSON.stringify({ listing_id: listingId, tone, customize_instructions: customizeInstructions }),
    });
  }

  // --- Application Tracking ---
  async listApplications(status?: string): Promise<{ applications: Application[]; total: number }> {
    const query = status ? `?status_filter=${status}` : '';
    return this.request<{ applications: Application[]; total: number }>(`/applications${query}`);
  }

  async createApplication(listingId: number, notes?: string): Promise<Application> {
    return this.request<Application>('/applications', {
      method: 'POST',
      body: JSON.stringify({ listing_id: listingId, notes }),
    });
  }

  async updateApplicationStatus(appId: number, status: string, notes?: string): Promise<Application> {
    return this.request<Application>(`/applications/${appId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, notes }),
    });
  }

  async deleteApplication(appId: number): Promise<void> {
    return this.request<void>(`/applications/${appId}`, {
      method: 'DELETE',
    });
  }

  // --- Analytics ---
  async getAnalytics(): Promise<AnalyticsResponse> {
    return this.request<AnalyticsResponse>('/analytics');
  }
}

export const api = new ApiClient();
