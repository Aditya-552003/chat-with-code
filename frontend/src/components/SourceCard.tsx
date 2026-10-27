'use client';

import React, { useState } from 'react';
import {
  FileCode2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Hash,
} from 'lucide-react';
import type { SourceReference } from '@/types';

interface SourceCardProps {
  source: SourceReference;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(source.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const relevancePercent = source.relevance_score
    ? Math.round(source.relevance_score * 100)
    : null;

  return (
    <div className="rounded-lg border border-surface-200 dark:border-surface-700/80 bg-white dark:bg-surface-800/80 overflow-hidden shadow-sm transition-all hover:border-brand-300 dark:hover:border-brand-700">
      {/* Header bar */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between p-2.5 cursor-pointer select-none bg-surface-50/60 dark:bg-surface-850/60 hover:bg-surface-100/80 dark:hover:bg-surface-700/50 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <span className="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-md bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300 text-[10px] font-bold">
            {index + 1}
          </span>
          <FileCode2 className="w-3.5 h-3.5 text-brand-500 flex-shrink-0" />
          <span className="text-xs font-mono font-medium text-surface-800 dark:text-surface-200 truncate">
            {source.file_path}
          </span>
          {source.start_line && source.end_line && (
            <span className="inline-flex items-center gap-0.5 text-[11px] font-mono text-surface-400 dark:text-surface-500 flex-shrink-0">
              <Hash className="w-2.5 h-2.5" />
              {source.start_line}-{source.end_line}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          {relevancePercent !== null && (
            <span
              className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
                relevancePercent >= 75
                  ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300'
                  : relevancePercent >= 50
                  ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300'
                  : 'bg-surface-100 dark:bg-surface-700 text-surface-600 dark:text-surface-400'
              }`}
            >
              {relevancePercent}% match
            </span>
          )}

          {source.github_url && (
            <a
              href={source.github_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="p-1 text-surface-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors"
              title="Open file in GitHub"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}

          <button
            type="button"
            className="p-1 text-surface-400 hover:text-surface-600 dark:hover:text-surface-200"
          >
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Expandable Snippet Code */}
      {isExpanded && (
        <div className="border-t border-surface-200 dark:border-surface-700 bg-surface-900 text-surface-100 p-3 relative group">
          <button
            type="button"
            onClick={handleCopy}
            className="absolute top-2 right-2 p-1.5 rounded bg-surface-800/80 hover:bg-surface-700 text-surface-300 hover:text-white transition-colors border border-surface-700"
            title="Copy code snippet"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          <pre className="text-xs font-mono overflow-x-auto whitespace-pre leading-relaxed pr-8">
            <code>{source.snippet}</code>
          </pre>
        </div>
      )}
    </div>
  );
}
