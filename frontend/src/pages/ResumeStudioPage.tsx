import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  FileEdit,
  Sparkles,
  Download,
  Printer,
  Loader2,
  FileText,
  Mail,
  ShieldCheck,
  CheckCircle2,
  Building,
} from 'lucide-react';
import { GeneratedDocument } from '@/types';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

export const ResumeStudioPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const initialJobId = searchParams.get('jobId') ? Number(searchParams.get('jobId')) : undefined;

  const [selectedJobId, setSelectedJobId] = useState<number | undefined>(initialJobId);
  const [docType, setDocType] = useState<'resume' | 'cover_letter'>('resume');
  const [tone, setTone] = useState('professional');
  const [customInstructions, setCustomInstructions] = useState('');
  const [activeDoc, setActiveDoc] = useState<GeneratedDocument | null>(null);

  // Load user's saved/recent jobs for dropdown
  const { data: jobsData } = useQuery({
    queryKey: ['jobs', 'studio-select'],
    queryFn: () => api.searchJobs({ page_size: 20 }),
  });

  // Load generated documents history
  const { data: documents, isLoading: docsLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => api.listDocuments(),
  });

  // Generate Resume Mutation
  const resumeMutation = useMutation({
    mutationFn: () => api.generateTailoredResume(selectedJobId!, customInstructions),
    onSuccess: (doc) => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setActiveDoc(doc);
    },
    onError: (err: any) => {
      alert(err.message || 'Resume tailoring failed');
    },
  });

  // Generate Cover Letter Mutation
  const coverLetterMutation = useMutation({
    mutationFn: () => api.generateCoverLetter(selectedJobId!, tone, customInstructions),
    onSuccess: (doc) => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setActiveDoc(doc);
    },
    onError: (err: any) => {
      alert(err.message || 'Cover letter generation failed');
    },
  });

  const isGenerating = resumeMutation.isPending || coverLetterMutation.isPending;

  const handleGenerate = () => {
    if (!selectedJobId) {
      alert('Please select a target job opportunity first.');
      return;
    }
    if (docType === 'resume') {
      resumeMutation.mutate();
    } else {
      coverLetterMutation.mutate();
    }
  };

  const handlePrint = () => {
    const iframe = document.getElementById('preview-iframe') as HTMLIFrameElement;
    if (iframe?.contentWindow) {
      iframe.contentWindow.print();
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <FileEdit className="w-5 h-5 text-indigo-600" />
            <h1 className="text-2xl font-bold text-slate-900">AI Resume & Cover Letter Studio</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Job-specific tailoring grounded strictly in your verified profile facts.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200 font-semibold">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Anti-Hallucination Guard Active</span>
          </span>
        </div>
      </div>

      {/* Generation Config Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
        <h2 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Tailoring Specifications</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Target Job Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Target Job Opportunity
            </label>
            <select
              value={selectedJobId || ''}
              onChange={(e) => setSelectedJobId(Number(e.target.value))}
              className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="">Select a target vacancy...</option>
              {jobsData?.jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title} — {j.company}
                </option>
              ))}
            </select>
          </div>

          {/* Document Type */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Document Format
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setDocType('resume')}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold border transition-colors ${
                  docType === 'resume'
                    ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Tailored Resume</span>
              </button>
              <button
                type="button"
                onClick={() => setDocType('cover_letter')}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold border transition-colors ${
                  docType === 'cover_letter'
                    ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Cover Letter</span>
              </button>
            </div>
          </div>

          {/* Tone (for cover letter) */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Communication Tone
            </label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              disabled={docType !== 'cover_letter'}
              className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white disabled:bg-slate-50 disabled:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="professional">Professional & Direct</option>
              <option value="enthusiastic">Energetic & Mission-aligned</option>
              <option value="concise">Concise Executive Brief</option>
            </select>
          </div>
        </div>

        {/* Custom Instructions */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Special Focus / Preferences (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g. Emphasize backend scalability, highlight PostgreSQL query optimization..."
            value={customInstructions}
            onChange={(e) => setCustomInstructions(e.target.value)}
            className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || !selectedJobId}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm transition-colors disabled:opacity-40"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Tailoring with Evidence...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate Tailored {docType === 'resume' ? 'Resume' : 'Cover Letter'}</span>
            </>
          )}
        </button>
      </div>

      {/* Main Preview & History Split */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Document History Sidebar */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3 lg:col-span-1">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-2">
            Generated Versions ({documents?.length || 0})
          </h3>

          {docsLoading ? (
            <LoadingSkeleton count={3} height="h-16" />
          ) : documents && documents.length > 0 ? (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => setActiveDoc(doc)}
                  className={`p-3 rounded-lg border text-left cursor-pointer transition-all ${
                    activeDoc?.id === doc.id
                      ? 'border-indigo-500 bg-indigo-50/50'
                      : 'border-slate-100 bg-slate-50/50 hover:border-slate-200'
                  }`}
                >
                  <div className="text-xs font-bold text-slate-900 line-clamp-1">{doc.title}</div>
                  <div className="text-[10px] text-slate-400 mt-1 capitalize">
                    {doc.document_type.replace('_', ' ')} • v{doc.version}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic py-4 text-center">
              No tailored documents generated yet.
            </p>
          )}
        </div>

        {/* Live Preview Iframe Pane */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                {activeDoc?.title || 'Document Preview'}
              </h2>
              <span className="text-xs text-slate-400">
                {activeDoc ? `Version ${activeDoc.version}` : 'Generate or pick a version on the left to preview'}
              </span>
            </div>

            {activeDoc && (
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePrint}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print / PDF</span>
                </button>
              </div>
            )}
          </div>

          {activeDoc?.content_html ? (
            <div className="border border-slate-200 rounded-lg overflow-hidden bg-slate-100 p-2 shadow-inner">
              <iframe
                id="preview-iframe"
                srcDoc={`<!DOCTYPE html><html><head><meta charset="utf-8"><style>
                  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1e293b; line-height: 1.6; padding: 24px; max-width: 800px; margin: 0 auto; }
                  h1 { font-size: 22px; margin: 0 0 4px 0; color: #0f172a; }
                  h2 { font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; color: #4338ca; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-top: 18px; }
                  .contact-info { font-size: 12px; color: #64748b; margin-bottom: 16px; }
                  .skills-grid { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
                  .skill-tag { background: #eff6ff; color: #1e40af; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; }
                  .job-entry { margin-bottom: 14px; }
                  .job-header { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; }
                  .dates { color: #64748b; font-size: 12px; font-weight: 400; }
                  .bullets { margin: 4px 0 0 18px; padding: 0; font-size: 12px; }
                  .bullets li { margin-bottom: 3px; }
                  .project-entry { margin-bottom: 10px; font-size: 12px; }
                </style></head><body>${activeDoc.content_html}</body></html>`}
                className="w-full h-[650px] bg-white rounded border border-slate-300"
                title="Preview"
              />
            </div>
          ) : (
            <div className="text-center py-20 text-slate-400 border border-dashed border-slate-200 rounded-lg bg-slate-50/50">
              <FileText className="w-10 h-10 mx-auto text-slate-300 mb-2" />
              <p className="text-xs">No active document selected for preview.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
