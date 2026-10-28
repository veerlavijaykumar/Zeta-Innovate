import React from 'react';
import { Check, X } from 'lucide-react';

interface SkillBadgeProps {
  name: string;
  status?: 'matched' | 'missing' | 'neutral';
  category?: string;
  className?: string;
}

export const SkillBadge: React.FC<SkillBadgeProps> = ({
  name,
  status = 'neutral',
  category,
  className = '',
}) => {
  let styleClasses = 'bg-slate-100 text-slate-700 border-slate-200';

  if (status === 'matched') {
    styleClasses = 'bg-emerald-50 text-emerald-800 border-emerald-200';
  } else if (status === 'missing') {
    styleClasses = 'bg-rose-50 text-rose-700 border-rose-200';
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium border transition-colors ${styleClasses} ${className}`}
      title={category ? `Category: ${category}` : undefined}
    >
      {status === 'matched' && <Check className="w-3 h-3 text-emerald-600 stroke-[2.5]" />}
      {status === 'missing' && <X className="w-3 h-3 text-rose-500 stroke-[2.5]" />}
      <span>{name}</span>
    </span>
  );
};
