import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  MapPin,
  Building,
  ExternalLink,
  Sparkles,
  Bookmark,
  Send,
  FileEdit,
  ArrowLeft,
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import { MatchScore } from '@/components/common/MatchScore';
import { EvidencePanel } from '@/components/common/EvidencePanel';
import { SkillBadge } from '@/components/common/SkillBadge';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

export const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const jobId = parseInt(id || '0', 10);

  // Job Listing Query
  const { data: job, isLoading: jobLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api.getJobDetail(jobId),
    enabled: !!jobId,
  });

  // Job Match Query
  const { data: match, isLoading: matchLoading } = useQuery({
    queryKey: ['match', jobId],
    queryFn: () => api.getJobMatch(jobId),
    enabled: !!jobId,
  });

  // Track Application Mutation
  const trackMutation = useMutation({
    mutationFn: () => api.createApplication(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      alert('Application tracked successfully in your Applications Pipeline!');
    },
    onError: (err: any) => {
      alert(err.message || 'Could not track application');
    },
  });

  if (jobLoading) {
    return <LoadingSkeleton count={3} height="h-36" />;
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <h2 className="text-lg font-bold text-slate-800">Job Not Found</h2>
        <Link to="/jobs" className="text-xs text-indigo-600 hover:underline mt-2 inline-block">
          Return to Job Search
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-5xl mx-auto">
      {/* Back button */}
      <div>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to listings</span>
        </button>
      </div>

      {/* Hero Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-7 shadow-sm space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{job.title}</h1>
            <div className="flex items-center gap-2 text-xs text-slate-500 mt-2 flex-wrap">
              <span className="flex items-center gap-1 font-semibold text-slate-800">
                <Building className="w-4 h-4 text-slate-400" />
                {job.company}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4 text-slate-400" />
                {job.location || 'Remote'}
              </span>
              {job.work_mode && (
                <>
                  <span>•</span>
                  <span className="capitalize px-2.5 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700 font-medium">
                    {job.work_mode}
                  </span>
                </>
              )}
            </div>
          </div>

          {match && (
            <div className="flex-shrink-0">
              <MatchScore
                score={match.overall_score}
                size="lg"
                isEligible={match.is_eligible}
              />
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center gap-3">
          {job.apply_url && (
            <a
              href={job.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm transition-colors"
            >
              <span>Apply on Official Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}

          <Link
            to={`/documents?jobId=${job.id}`}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 font-semibold text-xs shadow-sm transition-colors"
          >
            <FileEdit className="w-3.5 h-3.5 text-indigo-600" />
            <span>Tailor Resume for this Role</span>
          </Link>

          <button
            onClick={() => trackMutation.mutate()}
            disabled={trackMutation.isPending}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
          >
            <Send className="w-3.5 h-3.5 text-slate-600" />
            <span>Track Application</span>
          </button>
        </div>
      </div>

      {/* Explainable AI Evidence Panel */}
      {matchLoading ? (
        <LoadingSkeleton count={1} height="h-44" />
      ) : match ? (
        <EvidencePanel
          score={match.overall_score}
          explanation={match.explanation}
          evidence={match.evidence || []}
          eligibilityWarnings={match.eligibility_warnings || []}
          matchedSkills={match.matched_skills || []}
          missingSkills={match.missing_skills || []}
        />
      ) : null}

      {/* Job Description Body */}
      <div className="bg-white rounded-xl border border-slate-200 p-7 shadow-sm space-y-6">
        <div>
          <h2 className="text-base font-bold text-slate-900 mb-3">Job Description & Responsibilities</h2>
          <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-line font-sans">
            {job.description}
          </div>
        </div>

        {job.required_skills && job.required_skills.length > 0 && (
          <div className="pt-4 border-t border-slate-100">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">
              Required Technical Competencies
            </h3>
            <div className="flex flex-wrap gap-2">
              {job.required_skills.map((sk) => (
                <SkillBadge key={sk} name={sk} />
              ))}
            </div>
          </div>
        )}

        {job.preferred_skills && job.preferred_skills.length > 0 && (
          <div className="pt-2">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">
              Preferred Qualifications
            </h3>
            <div className="flex flex-wrap gap-2">
              {job.preferred_skills.map((sk) => (
                <SkillBadge key={sk} name={sk} status="neutral" />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
