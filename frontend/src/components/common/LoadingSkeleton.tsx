import React from 'react';

export const LoadingSkeleton: React.FC<{ count?: number; height?: string }> = ({
  count = 3,
  height = 'h-28',
}) => {
  return (
    <div className="space-y-4 w-full">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`${height} bg-slate-200/70 rounded-xl animate-pulse`}
        />
      ))}
    </div>
  );
};
