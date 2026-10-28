import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import {
  Compass,
  Briefcase,
  Sparkles,
  Send,
  BookOpen,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
} from 'lucide-react';
import { JobCard } from '@/components/common/JobCard';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.getProfile(),
  });

  const { data: analytics } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(),
  });

  const { data: jobsData, isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs', 'dashboard'],
    queryFn: () => api.searchJobs({ page_size: 4 }),
  });

  const completeness = profile?.profile_completeness || 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-700 via-indigo-600 to-indigo-800 rounded-2xl p-7 text-white shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-indigo-100 text-xs font-medium mb-3 backdrop-blur-sm">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Career Discovery & Application Copilot</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome, {user?.full_name || 'Candidate'}!
          </h1>
          <p className="text-indigo-100 text-sm mt-1 max-w-xl leading-relaxed">
            Discover tailored engineering roles, identify competency gaps, and generate truthful, ATS-optimized resumes.
          </p>
        </div>

        <div className="flex sm:flex-col gap-3">
          <Link
            to="/jobs"
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-white text-indigo-700 font-semibold text-xs shadow-sm hover:bg-indigo-50 transition-colors"
          >
            <span>Explore Vacancies</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/profile"
            className="inline-flex items-center justify-center px-4 py-2.5 rounded-xl bg-indigo-500/40 text-white border border-white/20 font-semibold text-xs hover:bg-indigo-500/60 transition-colors"
          >
            Update Profile
          </Link>
        </div>
      </div>

      {/* Profile Completeness Alert if < 70% */}
      {completeness < 70 && (
        <div className="bg-white rounded-xl border border-indigo-100 p-5 shadow-sm flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-extrabold text-sm flex-shrink-0">
              {completeness}%
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                Complete your candidate profile to unlock AI matching
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Upload your resume PDF or add verified skills to improve recommendation precision.
              </p>
            </div>
          </div>
          <Link
            to="/profile"
            className="text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-lg transition-colors"
          >
            Upload Resume
          </Link>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Discovered Jobs</span>
            <Briefcase className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {analytics?.total_jobs_discovered || 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Verified vacancies in DB</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Relevant Matches</span>
            <Sparkles className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {analytics?.relevant_matches || 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">High fit (≥ 70% relevance)</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Applications</span>
            <Send className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {analytics?.applications_submitted || 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Submitted & in pipeline</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Learning Progress</span>
            <BookOpen className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {analytics?.learning_progress || 0}%
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Competencies mastered</div>
        </div>
      </div>

      {/* Featured Jobs Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Recent Opportunities</h2>
            <p className="text-xs text-slate-500">Live vacancies ready for matching & application tailoring</p>
          </div>
          <Link
            to="/jobs"
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
          >
            <span>View all vacancies</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {jobsLoading ? (
          <LoadingSkeleton count={3} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobsData?.jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
