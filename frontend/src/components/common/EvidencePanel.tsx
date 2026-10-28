import React from 'react';
import { ShieldCheck, AlertCircle, FileText, Sparkles } from 'lucide-react';
import { MatchEvidence } from '@/types';

interface EvidencePanelProps {
  score: number;
  explanation?: string;
  evidence: MatchEvidence[];
  eligibilityWarnings?: string[];
  matchedSkills?: string[];
  missingSkills?: string[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  score,
  explanation,
  evidence,
  eligibilityWarnings = [],
  matchedSkills = [],
  missingSkills = [],
}) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
      <div className="flex items-start justify-between border-b border-slate-100 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-semibold text-slate-900">Explainable Match Intelligence</h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Evidence-backed transparency. Grounded in actual resume claims and job criteria.
          </p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-extrabold text-slate-900">{Math.round(score)}%</span>
          <div className="text-[10px] uppercase font-bold text-slate-600 tracking-wider">Overall Relevance</div>
        </div>
      </div>

      {/* Explanation summary */}
      {explanation && (
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-100 text-sm text-slate-700 leading-relaxed">
          <strong className="text-slate-900 block mb-1">Match Rationale:</strong>
          {explanation}
        </div>
      )}

      {/* Eligibility Warnings */}
      {eligibilityWarnings.length > 0 && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-4">
          <div className="flex items-center gap-2 text-amber-800 font-semibold text-sm mb-1.5">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span>Eligibility Warnings</span>
          </div>
          <ul className="list-disc list-inside text-xs text-amber-700 space-y-1">
            {eligibilityWarnings.map((warn, i) => (
              <li key={i}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Skills breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-emerald-50/50 rounded-lg border border-emerald-100 p-3.5">
          <div className="text-xs font-semibold text-emerald-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Matched Requirements ({matchedSkills.length})</span>
          </div>
          {matchedSkills.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {matchedSkills.map((sk) => (
                <span key={sk} className="bg-emerald-100 text-emerald-800 text-xs px-2 py-0.5 rounded font-medium">
                  {sk}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No direct skill overlaps identified.</p>
          )}
        </div>

        <div className="bg-rose-50/50 rounded-lg border border-rose-100 p-3.5">
          <div className="text-xs font-semibold text-rose-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4 text-rose-500" />
            <span>Competency Gaps ({missingSkills.length})</span>
          </div>
          {missingSkills.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {missingSkills.map((sk) => (
                <span key={sk} className="bg-rose-100 text-rose-800 text-xs px-2 py-0.5 rounded font-medium">
                  {sk}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-emerald-600 font-medium">All core requirements met!</p>
          )}
        </div>
      </div>

      {/* Verified Resume Evidence */}
      {evidence.length > 0 && (
        <div className="space-y-2.5">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5" />
            <span>Profile Evidence Supporting Match</span>
          </div>
          <div className="space-y-2">
            {evidence.map((ev, index) => (
              <div key={index} className="border border-slate-200 rounded-lg p-3 bg-white hover:border-slate-300 transition-colors">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-800">{ev.claim}</span>
                  <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded uppercase font-medium">
                    Source: {ev.source}
                  </span>
                </div>
                {ev.text && (
                  <p className="text-xs text-slate-600 italic bg-slate-50 rounded p-2 mt-1 border border-slate-100">
                    "{ev.text}"
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
