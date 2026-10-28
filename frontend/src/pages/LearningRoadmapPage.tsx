import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  BookOpen,
  CheckCircle2,
  Circle,
  ExternalLink,
  Plus,
  Loader2,
  Calendar,
  Clock,
  Sparkles,
  AlertCircle,
  Code,
} from 'lucide-react';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';

export const LearningRoadmapPage: React.FC = () => {
  const queryClient = useQueryClient();

  const [targetRole, setTargetRole] = useState('Full Stack Engineer');
  const [hoursPerWeek, setHoursPerWeek] = useState(10);
  const [activeRoadmapId, setActiveRoadmapId] = useState<number | null>(null);

  // Roadmaps Query
  const { data, isLoading } = useQuery({
    queryKey: ['roadmaps'],
    queryFn: () => api.getRoadmaps(),
  });

  const roadmaps = data?.roadmaps || [];
  const currentRoadmap =
    roadmaps.find((r) => r.id === activeRoadmapId) || roadmaps[0] || null;

  // Generate Roadmap Mutation
  const generateMutation = useMutation({
    mutationFn: () => api.generateRoadmap(targetRole, hoursPerWeek),
    onSuccess: (newRoadmap) => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      setActiveRoadmapId(newRoadmap.id);
    },
  });

  // Toggle Item Completion Mutation
  const toggleItemMutation = useMutation({
    mutationFn: ({ itemId, isCompleted }: { itemId: number; isCompleted: boolean }) =>
      api.updateLearningItem(itemId, isCompleted),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });

  return (
    <div className="space-y-8 animate-fade-in max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            <h1 className="text-2xl font-bold text-slate-900">Personalized Learning Roadmap</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Bridge your verified competency gaps with real educational resources and milestone projects.
          </p>
        </div>
      </div>

      {/* Generator Form */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Generate New Role Curriculum</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Target Role
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. AI / Machine Learning Engineer, Cloud Architect"
              className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Weekly Availability
            </label>
            <select
              value={hoursPerWeek}
              onChange={(e) => setHoursPerWeek(Number(e.target.value))}
              className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-300 bg-white"
            >
              <option value={5}>5 hours / week</option>
              <option value={10}>10 hours / week</option>
              <option value={15}>15 hours / week</option>
              <option value={20}>20 hours / week</option>
            </select>
          </div>
        </div>

        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending || !targetRole.trim()}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm transition-colors disabled:opacity-50"
        >
          {generateMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Synthesizing Curriculum...</span>
            </>
          ) : (
            <>
              <Plus className="w-4 h-4" />
              <span>Generate Roadmap</span>
            </>
          )}
        </button>
      </div>

      {/* Roadmaps selector tabs if multiple exist */}
      {roadmaps.length > 1 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {roadmaps.map((r) => (
            <button
              key={r.id}
              onClick={() => setActiveRoadmapId(r.id)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors border ${
                (currentRoadmap?.id === r.id)
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {r.target_role} ({Math.round(r.overall_progress)}%)
            </button>
          ))}
        </div>
      )}

      {/* Active Roadmap Timeline */}
      {isLoading ? (
        <LoadingSkeleton count={3} height="h-28" />
      ) : currentRoadmap ? (
        <div className="space-y-6">
          {/* Roadmap Header Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-slate-900">{currentRoadmap.target_role}</h2>
                <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    {currentRoadmap.total_weeks} Weeks Plan
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    {currentRoadmap.hours_per_week} hrs/week
                  </span>
                </div>
              </div>

              <div className="text-right">
                <span className="text-2xl font-black text-indigo-600">
                  {Math.round(currentRoadmap.overall_progress)}%
                </span>
                <span className="text-[10px] block uppercase font-bold text-slate-400">
                  Curriculum Progress
                </span>
              </div>
            </div>

            {currentRoadmap.description && (
              <p className="text-xs text-slate-600 mt-3 pt-3 border-t border-slate-100 leading-relaxed">
                {currentRoadmap.description}
              </p>
            )}
          </div>

          {/* Weekly Items */}
          <div className="space-y-4">
            {currentRoadmap.items?.map((item) => {
              const priorityColors: Record<string, string> = {
                critical: 'bg-rose-50 text-rose-700 border-rose-200',
                high: 'bg-amber-50 text-amber-700 border-amber-200',
                medium: 'bg-blue-50 text-blue-700 border-blue-200',
                low: 'bg-slate-100 text-slate-600 border-slate-200',
              };

              return (
                <div
                  key={item.id}
                  className={`bg-white rounded-xl border p-5 transition-all shadow-sm ${
                    item.is_completed
                      ? 'border-emerald-200 bg-emerald-50/20'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() =>
                          toggleItemMutation.mutate({
                            itemId: item.id,
                            isCompleted: !item.is_completed,
                          })
                        }
                        className="mt-0.5 text-slate-400 hover:text-indigo-600 transition-colors flex-shrink-0"
                      >
                        {item.is_completed ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600 fill-emerald-50" />
                        ) : (
                          <Circle className="w-5 h-5" />
                        )}
                      </button>

                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-bold text-slate-400 uppercase">
                            Week {item.week_number}
                          </span>
                          <h3
                            className={`text-sm font-bold ${
                              item.is_completed ? 'line-through text-slate-500' : 'text-slate-900'
                            }`}
                          >
                            {item.skill_name}
                          </h3>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold uppercase ${
                              priorityColors[item.priority] || priorityColors.medium
                            }`}
                          >
                            {item.priority}
                          </span>
                        </div>

                        {item.why_important && (
                          <p className="text-xs text-slate-600 leading-relaxed">
                            {item.why_important}
                          </p>
                        )}
                      </div>
                    </div>

                    <span className="text-xs text-slate-400 flex-shrink-0">
                      {item.estimated_hours} hrs
                    </span>
                  </div>

                  {/* Verified Resources */}
                  {item.resources && item.resources.length > 0 && (
                    <div className="mt-3.5 pt-3 border-t border-slate-100 pl-8 space-y-1.5">
                      <div className="text-[11px] font-semibold text-slate-700">
                        Verified Study Materials:
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {item.resources.map((res, i) => (
                          <a
                            key={i}
                            href={res.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-[11px] text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-md transition-colors"
                          >
                            <span>{res.title}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Practice Projects */}
                  {item.practice_projects && item.practice_projects.length > 0 && (
                    <div className="mt-2.5 pl-8 space-y-1">
                      {item.practice_projects.map((proj, i) => (
                        <div key={i} className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                          <strong className="text-slate-900 flex items-center gap-1.5 mb-0.5">
                            <Code className="w-3.5 h-3.5 text-indigo-600" />
                            {proj.title}
                          </strong>
                          <span className="text-slate-500 text-[11px]">{proj.description}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <EmptyState
          icon={BookOpen}
          title="No Learning Roadmaps Yet"
          description="Synthesize your first personalized learning plan to systematically bridge missing competencies."
        />
      )}
    </div>
  );
};
