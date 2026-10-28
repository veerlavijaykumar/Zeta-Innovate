import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  Loader2,
  CheckCircle2,
  GitCompare,
  TrendingUp,
} from 'lucide-react';
import { CareerRecommendation } from '@/types';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

export const CareerIntelPage: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState<CareerRecommendation | null>(null);
  const [compareRoles, setCompareRoles] = useState<string[]>([]);
  const [comparisonResult, setComparisonResult] = useState<any | null>(null);

  // Fetch Career Recommendations
  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['career-recommendations'],
    queryFn: () => api.getCareerRecommendations(),
    staleTime: 1000 * 60 * 30, // 30 mins
  });

  // Compare Careers Mutation
  const compareMutation = useMutation({
    mutationFn: (roles: string[]) => api.compareCareers(roles),
    onSuccess: (res) => {
      setComparisonResult(res);
    },
  });

  const toggleCompareRole = (roleTitle: string) => {
    if (compareRoles.includes(roleTitle)) {
      setCompareRoles(compareRoles.filter((r) => r !== roleTitle));
    } else {
      if (compareRoles.length >= 3) return;
      setCompareRoles([...compareRoles, roleTitle]);
    }
  };

  const handleRunComparison = () => {
    if (compareRoles.length >= 2) {
      compareMutation.mutate(compareRoles);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h1 className="text-2xl font-bold text-slate-900">AI Career Intelligence</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Grounded analysis of your verified profile against current tech market competencies.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 font-semibold text-xs shadow-sm transition-colors disabled:opacity-50"
        >
          {isFetching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-indigo-600" />}
          <span>Re-analyze Profile</span>
        </button>
      </div>

      {isLoading ? (
        <LoadingSkeleton count={3} height="h-36" />
      ) : error ? (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-center text-rose-800 space-y-2">
          <AlertCircle className="w-8 h-8 text-rose-500 mx-auto" />
          <h2 className="text-sm font-bold">Analysis Could Not Be Generated</h2>
          <p className="text-xs max-w-md mx-auto text-rose-600 leading-relaxed">
            {(error as any).message || 'Please ensure you have completed your profile and added skills.'}
          </p>
          <div className="pt-2">
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700"
            >
              Try Again
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Executive Assessment Overview */}
          {data && (
            <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-2xl p-6 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-indigo-300 text-xs font-bold uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Market Readiness Assessment</span>
              </div>
              <p className="text-sm leading-relaxed text-slate-200 font-medium">
                {data.overall_readiness}
              </p>
              {data.profile_summary && (
                <p className="text-xs text-slate-400 pt-1 border-t border-white/10">
                  <strong className="text-slate-300">Profile Summary:</strong> {data.profile_summary}
                </p>
              )}
            </div>
          )}

          {/* Role Comparison Bar */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <GitCompare className="w-4 h-4 text-indigo-600" />
              <span className="font-semibold">Compare Target Roles:</span>
              <span className="text-slate-400">
                ({compareRoles.length}/3 selected)
              </span>
            </div>

            <div className="flex items-center gap-3">
              {compareRoles.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {compareRoles.map((r) => (
                    <span
                      key={r}
                      className="bg-indigo-50 text-indigo-700 border border-indigo-200 text-[11px] px-2.5 py-1 rounded-md font-medium"
                    >
                      {r}
                    </span>
                  ))}
                </div>
              )}
              <button
                onClick={handleRunComparison}
                disabled={compareRoles.length < 2 || compareMutation.isPending}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm disabled:opacity-40 transition-colors flex items-center gap-1.5"
              >
                {compareMutation.isPending && <Loader2 className="w-3 h-3 animate-spin" />}
                <span>Compare Selected</span>
              </button>
            </div>
          </div>

          {/* Comparison Result Modal / View */}
          {comparisonResult && (
            <div className="bg-white rounded-xl border border-indigo-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                  <GitCompare className="w-4 h-4 text-indigo-600" />
                  <span>Role Comparison Summary</span>
                </h3>
                <button
                  onClick={() => setComparisonResult(null)}
                  className="text-xs text-slate-400 hover:text-slate-600"
                >
                  Close
                </button>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {comparisonResult.comparison_summary}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
                {comparisonResult.roles?.map((r: any) => (
                  <div key={r.role_title} className="border border-slate-200 rounded-lg p-4 bg-slate-50/50 space-y-2">
                    <div className="font-bold text-sm text-slate-900">{r.role_title}</div>
                    <div className="text-xs text-indigo-600 font-semibold">{r.fit_score}% Fit Score</div>
                    <p className="text-xs text-slate-600">{r.why_it_fits}</p>
                    {r.missing_skills?.length > 0 && (
                      <div className="text-[11px] text-rose-600 font-medium">
                        Missing: {r.missing_skills.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Roles List */}
          <div className="space-y-4">
            <h2 className="text-base font-bold text-slate-900">Recommended Career Trajectories</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {data?.recommendations?.map((rec) => {
                const isSelectedForCompare = compareRoles.includes(rec.role_title);
                return (
                  <div
                    key={rec.role_title}
                    className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:border-indigo-200 transition-all flex flex-col justify-between space-y-4"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div>
                          <h3 className="text-base font-bold text-slate-900">{rec.role_title}</h3>
                          <span className="text-[11px] text-slate-400 capitalize">
                            Confidence: {rec.confidence}
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-xl font-black text-indigo-600">{rec.fit_score}%</span>
                          <span className="text-[10px] block text-slate-400 uppercase font-bold">Fit Score</span>
                        </div>
                      </div>

                      <p className="text-xs text-slate-600 leading-relaxed mt-2">
                        {rec.why_it_fits}
                      </p>

                      {/* Demonstrated skills */}
                      {rec.relevant_skills && rec.relevant_skills.length > 0 && (
                        <div className="mt-3">
                          <span className="text-[11px] font-semibold text-emerald-800 block mb-1">
                            Demonstrated Profile Strengths:
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {rec.relevant_skills.map((s) => (
                              <span
                                key={s}
                                className="bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px] px-2 py-0.5 rounded font-medium"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Missing competencies */}
                      {rec.missing_skills && rec.missing_skills.length > 0 && (
                        <div className="mt-3">
                          <span className="text-[11px] font-semibold text-rose-800 block mb-1">
                            Growth Opportunities:
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {rec.missing_skills.map((s) => (
                              <span
                                key={s}
                                className="bg-rose-50 text-rose-700 border border-rose-100 text-[10px] px-2 py-0.5 rounded font-medium"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                      <button
                        onClick={() => toggleCompareRole(rec.role_title)}
                        className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-colors ${
                          isSelectedForCompare
                            ? 'bg-indigo-50 border-indigo-200 text-indigo-600 font-semibold'
                            : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        {isSelectedForCompare ? 'Selected for comparison' : '+ Add to compare'}
                      </button>

                      <span className="text-[11px] text-slate-400 italic">
                        {rec.alternative_paths?.length ? `Alt: ${rec.alternative_paths[0]}` : ''}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
