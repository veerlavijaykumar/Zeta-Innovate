import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Building, Briefcase, Bookmark, ExternalLink, ArrowRight } from 'lucide-react';
import { JobListing, JobMatch } from '@/types';
import { MatchScore } from './MatchScore';
import { SkillBadge } from './SkillBadge';

interface JobCardProps {
  job: JobListing;
  match?: JobMatch;
  isSaved?: boolean;
  onToggleSave?: (jobId: number) => void;
  onTrackApplication?: (jobId: number) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  match,
  isSaved = false,
  onToggleSave,
  onTrackApplication,
}) => {
  const formatSalary = () => {
    if (job.min_salary && job.max_salary) {
      const cur = job.salary_currency === 'INR' ? '₹' : job.salary_currency || '$';
      const minLPA = (job.min_salary / 100000).toFixed(1);
      const maxLPA = (job.max_salary / 100000).toFixed(1);
      if (job.salary_currency === 'INR') {
        return `${cur}${minLPA} - ${maxLPA} LPA`;
      }
      return `${cur}${job.min_salary.toLocaleString()} - ${cur}${job.max_salary.toLocaleString()}`;
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between group">
      <div>
        {/* Top Header */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1 min-w-0">
            <Link
              to={`/jobs/${job.id}`}
              className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1"
            >
              {job.title}
            </Link>
            <div className="flex items-center gap-2 text-xs text-slate-500 mt-1 flex-wrap">
              <span className="flex items-center gap-1 font-medium text-slate-700">
                <Building className="w-3.5 h-3.5 text-slate-400" />
                {job.company}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {job.location || 'Remote'}
              </span>
              {job.work_mode && (
                <>
                  <span>•</span>
                  <span className="capitalize px-2 py-0.5 rounded-full text-[11px] bg-slate-100 text-slate-600 font-medium">
                    {job.work_mode}
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {match && (
              <MatchScore
                score={match.overall_score}
                isEligible={match.is_eligible}
                size="sm"
              />
            )}
            {onToggleSave && (
              <button
                onClick={() => onToggleSave(job.id)}
                className={`p-1.5 rounded-lg border transition-colors ${
                  isSaved
                    ? 'bg-indigo-50 border-indigo-200 text-indigo-600'
                    : 'border-slate-200 text-slate-400 hover:text-slate-600 hover:bg-slate-50'
                }`}
                title={isSaved ? 'Remove from saved' : 'Save job'}
              >
                <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
              </button>
            )}
          </div>
        </div>

        {/* Short description */}
        {job.description && (
          <p className="text-xs text-slate-600 line-clamp-2 mt-2 leading-relaxed">
            {job.description}
          </p>
        )}

        {/* Skills preview */}
        {job.required_skills && job.required_skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {job.required_skills.slice(0, 5).map((sk) => (
              <SkillBadge key={sk} name={sk} />
            ))}
            {job.required_skills.length > 5 && (
              <span className="text-[11px] text-slate-400 self-center">
                +{job.required_skills.length - 5} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Footer info & CTA */}
      <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs">
        <div className="text-slate-600 font-semibold">
          {formatSalary() || (
            <span className="text-slate-400 font-normal">Salary undisclosed</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {onTrackApplication && (
            <button
              onClick={() => onTrackApplication(job.id)}
              className="text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors"
            >
              Track App
            </button>
          )}

          <Link
            to={`/jobs/${job.id}`}
            className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-lg transition-colors"
          >
            <span>View Match</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
};
