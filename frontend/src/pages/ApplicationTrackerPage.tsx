import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  Send,
  Building,
  ExternalLink,
  Calendar,
  Clock,
  Trash2,
  ChevronRight,
  Plus,
  Loader2,
  CheckCircle,
} from 'lucide-react';
import { Application } from '@/types';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';

const PIPELINE_STAGES = [
  { key: 'saved', label: 'Saved / Research', color: 'bg-slate-100 border-slate-200 text-slate-700' },
  { key: 'ready_to_apply', label: 'Ready to Apply', color: 'bg-blue-50 border-blue-200 text-blue-700' },
  { key: 'applied', label: 'Applied', color: 'bg-indigo-50 border-indigo-200 text-indigo-700' },
  { key: 'interview', label: 'Interviewing', color: 'bg-amber-50 border-amber-200 text-amber-700' },
  { key: 'offer', label: 'Offer Received', color: 'bg-emerald-50 border-emerald-200 text-emerald-700' },
  { key: 'rejected', label: 'Archived / Rejected', color: 'bg-rose-50 border-rose-200 text-rose-700' },
];

export const ApplicationTrackerPage: React.FC = () => {
  const queryClient = useQueryClient();

  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [newStatus, setNewStatus] = useState('');
  const [statusNote, setStatusNote] = useState('');
  const [nextStep, setNextStep] = useState('');

  // Applications Query
  const { data, isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => api.listApplications(),
  });

  const applications = data?.applications || [];

  // Update Status Mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ appId, status, notes, nextStep }: any) =>
      api.updateApplicationStatus(appId, status, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      setSelectedApp(null);
      setStatusNote('');
    },
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: (appId: number) => api.deleteApplication(appId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });

  const handleStatusChange = (app: Application, nextStage: string) => {
    updateStatusMutation.mutate({
      appId: app.id,
      status: nextStage,
      notes: `Transitioned to ${nextStage}`,
    });
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Send className="w-5 h-5 text-indigo-600" />
            <h1 className="text-2xl font-bold text-slate-900">Application Pipeline Tracker</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Track application stages, interview rounds, and status transition history.
          </p>
        </div>

        <div className="text-xs text-slate-500 font-semibold bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm">
          <span>Total Tracked: </span>
          <span className="text-indigo-600 font-bold">{applications.length}</span>
        </div>
      </div>

      {isLoading ? (
        <LoadingSkeleton count={3} height="h-44" />
      ) : applications.length === 0 ? (
        <EmptyState
          icon={Send}
          title="No Applications in Pipeline"
          description="Track opportunities directly from the Job Discovery page to monitor application status and milestones."
        />
      ) : (
        /* Kanban Board */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {PIPELINE_STAGES.map((stage) => {
            const stageApps = applications.filter((a) => a.status === stage.key);
            return (
              <div key={stage.key} className="bg-slate-100/70 rounded-xl p-3 flex flex-col min-h-[500px]">
                {/* Column Header */}
                <div className="flex items-center justify-between mb-3 px-1">
                  <span className="text-xs font-bold text-slate-700 tracking-tight">
                    {stage.label}
                  </span>
                  <span className="text-[11px] font-bold bg-white text-slate-600 px-2 py-0.5 rounded-full border border-slate-200 shadow-2xs">
                    {stageApps.length}
                  </span>
                </div>

                {/* Cards */}
                <div className="space-y-2.5 flex-1 overflow-y-auto">
                  {stageApps.map((app) => (
                    <div
                      key={app.id}
                      className="bg-white rounded-lg p-3.5 border border-slate-200 shadow-2xs hover:shadow-xs transition-all space-y-2.5 group"
                    >
                      <div>
                        <h4 className="text-xs font-bold text-slate-900 leading-snug line-clamp-1">
                          {app.job_title || 'Opportunity'}
                        </h4>
                        <div className="text-[11px] text-indigo-600 font-medium mt-0.5 flex items-center gap-1">
                          <Building className="w-3 h-3 text-slate-400" />
                          <span>{app.company_name || 'Company'}</span>
                        </div>
                      </div>

                      {app.notes && (
                        <p className="text-[11px] text-slate-500 bg-slate-50 p-2 rounded border border-slate-100 line-clamp-2">
                          {app.notes}
                        </p>
                      )}

                      {/* Card actions */}
                      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                        <select
                          value={app.status}
                          onChange={(e) => handleStatusChange(app, e.target.value)}
                          className="text-[10px] bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 font-medium text-slate-700"
                        >
                          {PIPELINE_STAGES.map((s) => (
                            <option key={s.key} value={s.key}>
                              Move to: {s.label}
                            </option>
                          ))}
                        </select>

                        <div className="flex items-center gap-1">
                          {app.apply_url && (
                            <a
                              href={app.apply_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-slate-400 hover:text-indigo-600 p-1"
                              title="Official Application Link"
                            >
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                          <button
                            onClick={() => deleteMutation.mutate(app.id)}
                            className="text-slate-400 hover:text-rose-500 p-1"
                            title="Delete"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
