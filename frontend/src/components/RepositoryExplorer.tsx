'use client';

import React, { useState } from 'react';
import {
  X,
  FolderGit2,
  GitBranch,
  FileCode2,
  Layers,
  ExternalLink,
  Search,
  Sparkles,
} from 'lucide-react';
import type { RepositoryState } from '@/types';

interface RepositoryExplorerProps {
  isOpen: boolean;
  onClose: () => void;
  repoState: RepositoryState;
}

export function RepositoryExplorer({
  isOpen,
  onClose,
  repoState,
}: RepositoryExplorerProps) {
  const [filter, setFilter] = useState('');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-md bg-white dark:bg-surface-900 h-full shadow-2xl flex flex-col border-l border-surface-200 dark:border-surface-800 animate-slide-in-left">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-surface-200 dark:border-surface-800">
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-brand-500" />
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white">
              Repository Details
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Main Info Card */}
          <div className="p-4 rounded-xl bg-surface-50 dark:bg-surface-800/60 border border-surface-200 dark:border-surface-700/80 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-surface-500 uppercase tracking-wider">
                Target Repository
              </span>
              <a
                href={`https://github.com/${repoState.owner}/${repoState.repo}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-brand-600 dark:text-brand-400 hover:underline"
              >
                GitHub <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div className="text-sm font-bold text-surface-900 dark:text-white">
              {repoState.owner}/{repoState.repo}
            </div>

            <div className="flex items-center gap-2 text-xs text-surface-600 dark:text-surface-300">
              <GitBranch className="w-3.5 h-3.5 text-brand-500" />
              <span>Branch:</span>
              <code className="px-1.5 py-0.5 rounded bg-surface-200 dark:bg-surface-700 text-surface-800 dark:text-surface-200 font-mono text-[11px]">
                {repoState.branch || 'main'}
              </code>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-surface-50 dark:bg-surface-800/60 border border-surface-200 dark:border-surface-700/80">
              <div className="flex items-center gap-2 text-surface-500 dark:text-surface-400 text-xs mb-1">
                <FileCode2 className="w-4 h-4 text-brand-500" />
                <span>Files Indexed</span>
              </div>
              <div className="text-xl font-bold text-surface-900 dark:text-white">
                {repoState.totalFiles}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-surface-50 dark:bg-surface-800/60 border border-surface-200 dark:border-surface-700/80">
              <div className="flex items-center gap-2 text-surface-500 dark:text-surface-400 text-xs mb-1">
                <Layers className="w-4 h-4 text-indigo-500" />
                <span>Vector Chunks</span>
              </div>
              <div className="text-xl font-bold text-surface-900 dark:text-white">
                {repoState.indexedChunks}
              </div>
            </div>
          </div>

          {/* RAG Engine Info */}
          <div className="p-4 rounded-xl bg-gradient-to-br from-brand-50/50 to-indigo-50/50 dark:from-brand-950/20 dark:to-indigo-950/20 border border-brand-200/60 dark:border-brand-900/40 space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-brand-700 dark:text-brand-300">
              <Sparkles className="w-3.5 h-3.5" />
              <span>RAG Pipeline Configuration</span>
            </div>
            <ul className="text-xs text-surface-600 dark:text-surface-400 space-y-1.5 list-disc list-inside">
              <li><strong className="text-surface-800 dark:text-surface-200">LLM:</strong> Google Gemini 2.5 Flash</li>
              <li><strong className="text-surface-800 dark:text-surface-200">Embeddings:</strong> BAAI/bge-small-en (Dense 384d)</li>
              <li><strong className="text-surface-800 dark:text-surface-200">Index Store:</strong> FAISS / LlamaIndex VectorStore</li>
              <li><strong className="text-surface-800 dark:text-surface-200">Chunking:</strong> AST Semantic Splitter (1024 / 128)</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-surface-200 dark:border-surface-800">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2 px-4 rounded-lg bg-surface-100 dark:bg-surface-800 hover:bg-surface-200 dark:hover:bg-surface-700 text-xs font-semibold text-surface-800 dark:text-surface-200 transition-colors"
          >
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
}
