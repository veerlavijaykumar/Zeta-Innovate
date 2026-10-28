import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  BarChart2,
  TrendingUp,
  Briefcase,
  Send,
  Sparkles,
  BookOpen,
  CheckCircle2,
} from 'lucide-react';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

export const AnalyticsPage: React.FC = () => {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(),
  });

  const timelineData = analytics?.application_timeline || [];
  const skillGaps = analytics?.skill_gaps || [];

  const BAR_COLORS = ['#6366f1', '#818cf8', '#3b82f6', '#10b981', '#059669'];

  if (isLoading) {
    return <LoadingSkeleton count={3} height="h-44" />;
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-200 pb-5">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-5 h-5 text-indigo-600" />
          <h1 className="text-2xl font-bold text-slate-900">Career & Application Analytics</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Real metrics calculated directly from your verified searches, matches, and application pipelines.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Ingested</span>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {analytics?.total_jobs_discovered || 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Vacancies in system</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">High Relevance</span>
          <div className="text-2xl font-black text-indigo-600 mt-1">
            {analytics?.relevant_matches || 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">≥ 70% Match Score</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Applied</span>
          <div className="text-2xl font-black text-blue-600 mt-1">
            {analytics?.applications_submitted || 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Active applications</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Conversion Rate</span>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {analytics?.conversion_rate ? `${analytics.conversion_rate}%` : 'N/A'}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Applied to interview</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Application Funnel Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Application Pipeline Volume</h2>
            <p className="text-xs text-slate-500">Distribution of applications across stages</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="stage" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '12px',
                    border: 'none',
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {timelineData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Most Frequent Competency Gaps */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Top Missing Competencies</h2>
            <p className="text-xs text-slate-500">
              Skills most frequently missing across evaluated job matches
            </p>
          </div>

          {skillGaps.length > 0 ? (
            <div className="space-y-2.5 pt-2">
              {skillGaps.map((gap, i) => (
                <div key={i} className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span className="font-semibold text-slate-800">{gap.skill}</span>
                  <span className="font-bold text-rose-600 bg-rose-50 px-2.5 py-0.5 rounded-full border border-rose-200">
                    Missing in {gap.frequency} jobs
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic py-16 text-center">
              Run AI job matching to identify frequent market competency gaps.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
