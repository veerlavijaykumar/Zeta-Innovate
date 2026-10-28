import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  Settings,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Shield,
  Loader2,
  Database,
  Key,
} from 'lucide-react';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

export const SettingsPage: React.FC = () => {
  const queryClient = useQueryClient();

  const [syncQuery, setSyncQuery] = useState('Software Engineer');
  const [syncLocation, setSyncLocation] = useState('India');
  const [syncResult, setSyncResult] = useState<string | null>(null);

  // Job Sources Query
  const { data: sources, isLoading } = useQuery({
    queryKey: ['job-sources'],
    queryFn: () => api.getJobSources(),
  });

  // Sync Mutation
  const syncMutation = useMutation({
    mutationFn: () => api.syncJobs(syncQuery, syncLocation),
    onSuccess: (res) => {
      setSyncResult(res.message);
      queryClient.invalidateQueries({ queryKey: ['job-sources'] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
    onError: (err: any) => {
      setSyncResult(`Sync failed: ${err.message}`);
    },
  });

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-200 pb-5">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-indigo-600" />
          <h1 className="text-2xl font-bold text-slate-900">Job Sources & System Connectors</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Monitor API connector health, configure external job feeds, and trigger manual synchronization.
        </p>
      </div>

      {/* Sync Status Banner */}
      {syncResult && (
        <div className={`p-4 rounded-xl text-xs flex items-center gap-2 border ${
          syncResult.includes('failed')
            ? 'bg-rose-50 border-rose-200 text-rose-700'
            : 'bg-emerald-50 border-emerald-200 text-emerald-800'
        }`}>
          {syncResult.includes('failed') ? (
            <AlertCircle className="w-4 h-4 text-rose-500" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          )}
          <span>{syncResult}</span>
        </div>
      )}

      {/* Connected Sources List */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
        <h2 className="text-base font-bold text-slate-900">Connected Job Ingestion Connectors</h2>

        {isLoading ? (
          <LoadingSkeleton count={2} height="h-24" />
        ) : (
          <div className="space-y-4">
            {sources?.map((source) => (
              <div
                key={source.id}
                className="border border-slate-200 rounded-xl p-5 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-slate-900 capitalize">
                      {source.name}
                    </span>
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                      {source.source_type}
                    </span>
                    {source.is_configured ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>Connected & Active</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                        <AlertCircle className="w-3 h-3 text-amber-600" />
                        <span>Credentials Required</span>
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500">
                    Total listings ingested: <strong className="text-slate-700">{source.total_listings}</strong>
                    {source.last_sync_at && (
                      <span> • Last synced: {new Date(source.last_sync_at).toLocaleString()}</span>
                    )}
                  </div>
                  {source.last_error && (
                    <div className="text-xs text-rose-600 font-medium pt-1">
                      Error: {source.last_error}
                    </div>
                  )}
                </div>

                {!source.is_configured && source.name === 'adzuna' && (
                  <div className="text-right">
                    <a
                      href="https://developer.adzuna.com/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                    >
                      <span>Get Free API Key</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Manual Connector Ingestion Trigger */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <RefreshCw className="w-4 h-4 text-indigo-600" />
          <span>Manual Sync Trigger</span>
        </h2>
        <p className="text-xs text-slate-500">
          Query active connectors to fetch, normalize, and deduplicate new tech job vacancies.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Role Query
            </label>
            <input
              type="text"
              value={syncQuery}
              onChange={(e) => setSyncQuery(e.target.value)}
              className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Location
            </label>
            <input
              type="text"
              value={syncLocation}
              onChange={(e) => setSyncLocation(e.target.value)}
              className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>
        </div>

        <button
          onClick={() => syncMutation.mutate()}
          disabled={syncMutation.isPending}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm transition-colors disabled:opacity-50 mt-2"
        >
          {syncMutation.isPending ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Syncing Listings...</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Trigger Ingestion Sync</span>
            </>
          )}
        </button>
      </div>

      {/* Setup Guide for Evaluators */}
      <div className="bg-slate-50 rounded-xl border border-slate-200 p-6 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
          <Key className="w-4 h-4 text-indigo-600" />
          <span>External API Integration Guide</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          To connect the live Adzuna search engine, sign up for free at{' '}
          <a
            href="https://developer.adzuna.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 font-semibold underline"
          >
            developer.adzuna.com
          </a>
          . Then add your credentials in <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 font-mono text-[11px]">backend/.env</code>:
        </p>
        <pre className="bg-slate-900 text-slate-100 p-3.5 rounded-lg font-mono text-xs overflow-x-auto">
          ADZUNA_APP_ID="your_app_id"{"\n"}
          ADZUNA_APP_KEY="your_app_key"{"\n"}
          GEMINI_API_KEY="your_google_gemini_api_key"
        </pre>
      </div>
    </div>
  );
};
