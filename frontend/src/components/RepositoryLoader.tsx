'use client';

import React, { useState } from 'react';
import {
  Search,
  Loader2,
  FolderGit2,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  GitBranch,
  FileCode2,
  Layers,
  ExternalLink,
  X,
  Sparkles,
} from 'lucide-react';
import type { IndexingStatus } from '@/types';

interface RepositoryLoaderProps {
  url: string;
  owner: string;
  repo: string;
  branch: string;
  status: IndexingStatus;
  totalFiles: number;
  indexedChunks: number;
  isLoading: boolean;
  error: string | null;
  isConnected: boolean;
  onLoad: (url: string) => void;
  onDisconnect: () => void;
}

const POPULAR_REPOS = [
  { name: 'FastAPI', url: 'https://github.com/fastapi/fastapi' },
  { name: 'Flask', url: 'https://github.com/pallets/flask' },
  { name: 'HTTPX', url: 'https://github.com/encode/httpx' },
  { name: 'Pydantic', url: 'https://github.com/pydantic/pydantic' },
];

const STEPS: { key: IndexingStatus; label: string; desc: string }[] = [
  { key: 'queued', label: 'Queued', desc: 'Validating repository and branch' },
  { key: 'loading', label: 'Fetching', desc: 'Downloading source code via GitHub API' },
  { key: 'chunking', label: 'Chunking', desc: 'Parsing AST and syntax blocks' },
  { key: 'embedding', label: 'Embedding', desc: 'Generating dense vector representations' },
  { key: 'indexing', label: 'Indexing', desc: 'Building FAISS similarity index' },
  { key: 'completed', label: 'Ready', desc: 'Knowledge base active & searchable' },
];

export function RepositoryLoader({
  url: initialUrl,
  owner,
  repo,
  branch,
  status,
  totalFiles,
  indexedChunks,
  isLoading,
  error,
  isConnected,
  onLoad,
  onDisconnect,
}: RepositoryLoaderProps) {
  const [inputUrl, setInputUrl] = useState(initialUrl || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputUrl.trim() && !isLoading) {
      onLoad(inputUrl.trim());
    }
  };

  const handleSelectExample = (repoUrl: string) => {
    setInputUrl(repoUrl);
    if (!isLoading) {
      onLoad(repoUrl);
    }
  };

  const getStepState = (stepKey: IndexingStatus) => {
    const order: IndexingStatus[] = ['queued', 'loading', 'chunking', 'embedding', 'indexing', 'completed'];
    const currentIndex = order.indexOf(status);
    const stepIndex = order.indexOf(stepKey);

    if (status === 'failed') return 'failed';
    if (currentIndex > stepIndex || status === 'completed') return 'completed';
    if (currentIndex === stepIndex) return 'current';
    return 'upcoming';
  };

  return (
    <div className="w-full bg-white dark:bg-surface-900 border-b border-surface-200 dark:border-surface-800 transition-colors shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Case 1: Active Connected Repository */}
        {isConnected ? (
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 rounded-xl bg-gradient-to-r from-brand-50/70 via-indigo-50/50 to-purple-50/70 dark:from-surface-800/90 dark:via-surface-800/60 dark:to-brand-950/40 border border-brand-200/80 dark:border-brand-900/60">
            <div className="flex items-center gap-3.5">
              <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-brand-600 text-white shadow-md shadow-brand-500/20">
                <FolderGit2 className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-base font-semibold text-surface-900 dark:text-white">
                    {owner}/{repo}
                  </h2>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono bg-surface-200/80 dark:bg-surface-700 text-surface-700 dark:text-surface-300">
                    <GitBranch className="w-3 h-3 text-brand-500" />
                    {branch || 'main'}
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                    <CheckCircle2 className="w-3 h-3" />
                    Indexed & Ready
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-surface-500 dark:text-surface-400 mt-1">
                  <span className="flex items-center gap-1">
                    <FileCode2 className="w-3.5 h-3.5 text-brand-500" />
                    {totalFiles} source files
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5 text-indigo-500" />
                    {indexedChunks} vector chunks
                  </span>
                  <span>•</span>
                  <a
                    href={`https://github.com/${owner}/${repo}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-brand-600 dark:text-brand-400 hover:underline"
                  >
                    View on GitHub
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2.5 self-end md:self-auto">
              <button
                type="button"
                onClick={onDisconnect}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium text-surface-700 dark:text-surface-300 bg-white dark:bg-surface-800 hover:bg-surface-100 dark:hover:bg-surface-700 border border-surface-200 dark:border-surface-700 shadow-sm transition-colors"
              >
                <X className="w-3.5 h-3.5" />
                Disconnect
              </button>
            </div>
          </div>
        ) : (
          /* Case 2: Input and Loading State */
          <div className="space-y-4">
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2.5">
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-surface-400">
                  <FolderGit2 className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={inputUrl}
                  onChange={(e) => setInputUrl(e.target.value)}
                  placeholder="Paste GitHub repository URL, e.g. https://github.com/fastapi/fastapi (or with /tree/branch)"
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/80 text-sm text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition-all disabled:opacity-50"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !inputUrl.trim()}
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white font-medium text-sm shadow-md shadow-brand-500/20 active:scale-[0.99] transition-all disabled:opacity-50 disabled:pointer-events-none"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Indexing Repo...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Load & Index</span>
                  </>
                )}
              </button>
            </form>

            {/* Quick-Pick Popular Example Repos */}
            {!isLoading && (
              <div className="flex items-center gap-2 flex-wrap text-xs">
                <span className="text-surface-500 dark:text-surface-400 font-medium">
                  Try an example:
                </span>
                {POPULAR_REPOS.map((sample) => (
                  <button
                    key={sample.name}
                    type="button"
                    onClick={() => handleSelectExample(sample.url)}
                    className="px-2.5 py-1 rounded-lg bg-surface-100 dark:bg-surface-800 hover:bg-brand-50 dark:hover:bg-brand-950/40 text-surface-700 dark:text-surface-300 hover:text-brand-600 dark:hover:text-brand-400 border border-surface-200 dark:border-surface-700 transition-colors"
                  >
                    {sample.name}
                  </button>
                ))}
              </div>
            )}

            {/* Step-by-Step Indexing Progress Bar */}
            {isLoading && (
              <div className="p-4 rounded-xl bg-surface-50 dark:bg-surface-800/60 border border-surface-200 dark:border-surface-700/80 space-y-3">
                <div className="flex items-center justify-between text-xs font-medium">
                  <div className="flex items-center gap-2 text-brand-600 dark:text-brand-400">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Analyzing codebase and building vector representations...</span>
                  </div>
                  {totalFiles > 0 && (
                    <span className="text-surface-500 dark:text-surface-400">
                      {totalFiles} files detected • {indexedChunks} chunks created
                    </span>
                  )}
                </div>

                {/* Progress Steps Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
                  {STEPS.map((step) => {
                    const state = getStepState(step.key);
                    return (
                      <div
                        key={step.key}
                        className={`p-2.5 rounded-lg border text-left transition-all ${
                          state === 'completed'
                            ? 'bg-emerald-50/70 border-emerald-200 dark:bg-emerald-950/30 dark:border-emerald-800/50 text-emerald-800 dark:text-emerald-300'
                            : state === 'current'
                            ? 'bg-brand-50 border-brand-300 dark:bg-brand-950/40 dark:border-brand-700 text-brand-700 dark:text-brand-300 ring-2 ring-brand-500/20'
                            : 'bg-white dark:bg-surface-800/40 border-surface-200 dark:border-surface-700/60 text-surface-400'
                        }`}
                      >
                        <div className="flex items-center gap-1.5 mb-1">
                          {state === 'completed' ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                          ) : state === 'current' ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin text-brand-600 dark:text-brand-400" />
                          ) : (
                            <div className="w-3.5 h-3.5 rounded-full border border-surface-300 dark:border-surface-600" />
                          )}
                          <span className="text-xs font-semibold">{step.label}</span>
                        </div>
                        <p className="text-[10px] line-clamp-1 opacity-80">{step.desc}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Error Message Display */}
            {error && (
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-300 text-xs">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400 flex-shrink-0" />
                  <span>{error}</span>
                </div>
                <button
                  type="button"
                  onClick={() => onLoad(inputUrl)}
                  className="inline-flex items-center gap-1 text-xs font-medium text-rose-700 dark:text-rose-300 hover:underline ml-2"
                >
                  <RefreshCw className="w-3 h-3" />
                  Retry
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
