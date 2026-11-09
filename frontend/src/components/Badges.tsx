import React from 'react';

export const SeverityBadge: React.FC<{ severity: string; size?: 'sm' | 'md' }> = ({ severity, size = 'md' }) => {
  const sev = (severity || 'INFO').toUpperCase();
  const baseClasses = size === 'sm' 
    ? 'px-1.5 py-0.5 text-xs font-semibold rounded'
    : 'px-2.5 py-1 text-xs font-bold rounded-sm uppercase tracking-wider';

  switch (sev) {
    case 'CRITICAL':
      return <span className={`${baseClasses} bg-red-100 text-red-800 border border-red-300`}>CRITICAL</span>;
    case 'HIGH':
      return <span className={`${baseClasses} bg-orange-100 text-orange-800 border border-orange-300`}>HIGH</span>;
    case 'MEDIUM':
      return <span className={`${baseClasses} bg-amber-100 text-amber-800 border border-amber-300`}>MEDIUM</span>;
    case 'LOW':
      return <span className={`${baseClasses} bg-blue-100 text-blue-800 border border-blue-300`}>LOW</span>;
    default:
      return <span className={`${baseClasses} bg-slate-100 text-slate-700 border border-slate-300`}>{sev}</span>;
  }
};

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const st = (status || 'NEW').toUpperCase();
  const baseClasses = 'px-2 py-0.5 text-xs font-medium rounded-full inline-flex items-center gap-1';

  switch (st) {
    case 'ESCALATED_HUMAN_REVIEW':
      return (
        <span className={`${baseClasses} bg-purple-100 text-purple-900 border border-purple-300 animate-pulse font-semibold`}>
          <span className="w-1.5 h-1.5 rounded-full bg-purple-600"></span>
          UNCERTAIN — HUMAN REVIEW
        </span>
      );
    case 'CONTAINED':
      return (
        <span className={`${baseClasses} bg-emerald-100 text-emerald-800 border border-emerald-300`}>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
          CONTAINED
        </span>
      );
    case 'INVESTIGATING':
      return (
        <span className={`${baseClasses} bg-blue-100 text-blue-800 border border-blue-300`}>
          <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
          INVESTIGATING
        </span>
      );
    case 'RESOLVED':
      return (
        <span className={`${baseClasses} bg-slate-100 text-slate-700 border border-slate-300`}>
          <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
          RESOLVED
        </span>
      );
    case 'FALSE_POSITIVE':
      return (
        <span className={`${baseClasses} bg-zinc-100 text-zinc-600 border border-zinc-300`}>
          FALSE POSITIVE
        </span>
      );
    default:
      return (
        <span className={`${baseClasses} bg-amber-100 text-amber-800 border border-amber-300`}>
          <span className="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
          NEW
        </span>
      );
  }
};

export const ConfidenceBadge: React.FC<{ confidence: number }> = ({ confidence }) => {
  const pct = Math.round(confidence * 100);
  let color = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (pct < 50) color = 'bg-red-50 text-red-700 border-red-200';
  else if (pct < 75) color = 'bg-amber-50 text-amber-700 border-amber-200';

  return (
    <span className={`px-2 py-0.5 text-xs font-mono border rounded ${color}`}>
      {pct}% CONFIDENCE
    </span>
  );
};
