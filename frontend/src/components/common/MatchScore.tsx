import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

interface MatchScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  isEligible?: boolean;
}

export const MatchScore: React.FC<MatchScoreProps> = ({
  score,
  size = 'md',
  showLabel = true,
  isEligible = true,
}) => {
  const rounded = Math.round(score);

  let colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (rounded < 50) {
    colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';
  } else if (rounded < 70) {
    colorClasses = 'bg-amber-50 text-amber-700 border-amber-200';
  } else if (rounded < 85) {
    colorClasses = 'bg-blue-50 text-blue-700 border-blue-200';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3.5 py-1.5 font-bold',
  }[size];

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full border font-semibold tracking-tight transition-colors ${colorClasses} ${sizeClasses}`}
      title={`${rounded}% Overall Match`}
    >
      <span>{rounded}%</span>
      {showLabel && <span className="font-normal opacity-90">Match</span>}
      {!isEligible && (
        <span title="Eligibility warning">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
        </span>
      )}
      {isEligible && rounded >= 75 && (
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
      )}
    </div>
  );
};
