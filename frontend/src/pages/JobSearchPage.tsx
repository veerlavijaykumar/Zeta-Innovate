import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  Search,
  MapPin,
  Filter,
  RefreshCw,
  Sparkles,
  Bookmark,
  Building,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { JobCard } from '@/components/common/JobCard';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';

export const JobSearchPage: React.FC = () => {
  const queryClient = useQueryClient();

  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [workMode, setWorkMode] = useState('');
  const [employmentType, setEmploymentType] = useState('');
  const [page, setPage] = useState(1);
  const [matchingRunning, setMatchingRunning] = useState(false);

  // Search Jobs Query
  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['jobs', { query, location, workMode, employmentType, page }],
    queryFn: () =>
      api.searchJobs({
        query: query || undefined,
        location: location || undefined,
        work_mode: workMode || undefined,
        employment_type: employmentType || undefined,
        page,
        page_size: 10,
      }),
  });

  // Saved Jobs Query
  const { data: savedJobs } = useQuery({
    queryKey: ['saved-jobs'],
    queryFn: () => api.getSavedJobs(),
  });

  const savedJobIds = new Set(savedJobs?.map((s) => s.listing_id) || []);

  // Toggle Save Mutation
  const saveMutation = useMutation({
    mutationFn: (listingId: number) => {
      if (savedJobIds.has(listingId)) {
        return api.unsaveJob(listingId);
      }
      return api.saveJob(listingId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['saved-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });

  // Run AI Matching Mutation
  const handleRunMatching = async () => {
    setMatchingRunning(true);
    try {
      await api.runMatching(20);
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    } catch (e) {
      console.error(e);
    } finally {
      setMatchingRunning(false);
    }
  };

  const handleTrackApplication = async (jobId: number) => {
    try {
      await api.createApplication(jobId);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      alert('Application tracked successfully in your Applications Pipeline!');
    } catch (err: any) {
      alert(err.message || 'Could not track application');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Multi-Source Job Discovery</h1>
          <p className="text-xs text-slate-500 mt-1">
            Search verified listings, filter by preferences, and calculate genuine fit scores.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunMatching}
            disabled={matchingRunning}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm transition-colors disabled:opacity-50"
          >
            {matchingRunning ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>Calculate AI Matches</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {/* Query input */}
          <div className="relative md:col-span-2">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by role, company, or tech keywords..."
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(1);
              }}
              className="w-full text-xs pl-9 pr-3 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          {/* Location input */}
          <div className="relative">
            <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="City (e.g. Bangalore, Delhi)"
              value={location}
              onChange={(e) => {
                setLocation(e.target.value);
                setPage(1);
              }}
              className="w-full text-xs pl-9 pr-3 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          {/* Work Mode */}
          <div>
            <select
              value={workMode}
              onChange={(e) => {
                setWorkMode(e.target.value);
                setPage(1);
              }}
              className="w-full text-xs px-3 py-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="">All Work Modes</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">Onsite</option>
            </select>
          </div>
        </div>

        {/* Second filter row */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-500">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-700">Type:</span>
              <select
                value={employmentType}
                onChange={(e) => {
                  setEmploymentType(e.target.value);
                  setPage(1);
                }}
                className="text-xs px-2 py-1 rounded border border-slate-200 bg-white"
              >
                <option value="">Any Type</option>
                <option value="full-time">Full-time</option>
                <option value="contract">Contract</option>
                <option value="part-time">Part-time</option>
              </select>
            </div>
          </div>

          <div>
            <span className="font-semibold text-slate-800">{data?.total || 0}</span> opportunities found
          </div>
        </div>
      </div>

      {/* Listings */}
      {isLoading ? (
        <LoadingSkeleton count={4} height="h-32" />
      ) : data?.jobs && data.jobs.length > 0 ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                isSaved={savedJobIds.has(job.id)}
                onToggleSave={(id) => saveMutation.mutate(id)}
                onTrackApplication={handleTrackApplication}
              />
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-6">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-2 rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-slate-50 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs font-semibold text-slate-600 px-3">
                Page {page} of {data.total_pages}
              </span>
              <button
                disabled={page >= data.total_pages}
                onClick={() => setPage(page + 1)}
                className="p-2 rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-slate-50 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          icon={Search}
          title="No jobs match your search filters"
          description="Try clearing your filters or trigger external connector synchronization in Settings to discover more opportunities."
          actionText="Clear Filters"
          onAction={() => {
            setQuery('');
            setLocation('');
            setWorkMode('');
            setEmploymentType('');
            setPage(1);
          }}
        />
      )}
    </div>
  );
};
