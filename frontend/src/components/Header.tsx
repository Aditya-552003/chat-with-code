'use client';

import React, { useState, useEffect } from 'react';
import {
  Code2,
  Sparkles,
  Github,
  Sun,
  Moon,
  FolderGit2,
  Activity,
  Layers,
} from 'lucide-react';
import * as api from '@/services/api';
import type { HealthResponse } from '@/types';

interface HeaderProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  repositoryId?: string;
  owner?: string;
  repo?: string;
  branch?: string;
  onOpenExplorer?: () => void;
  hasActiveRepo?: boolean;
}

export function Header({
  theme,
  onToggleTheme,
  repositoryId,
  owner,
  repo,
  branch,
  onOpenExplorer,
  hasActiveRepo,
}: HeaderProps) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    const check = async () => {
      try {
        const res = await api.checkHealth();
        if (mounted) {
          setHealth(res);
          setIsBackendOnline(res.status === 'ok');
        }
      } catch {
        if (mounted) {
          setIsBackendOnline(false);
        }
      }
    };

    check();
    const interval = setInterval(check, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-surface-200/80 dark:border-surface-800/80 bg-white/80 dark:bg-surface-900/80 backdrop-blur-md transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-purple-500 text-white shadow-md shadow-brand-500/20 ring-1 ring-white/20">
            <Code2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-surface-900 to-surface-700 dark:from-white dark:to-surface-200 bg-clip-text text-transparent">
                Chat with Code
              </span>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold tracking-wide uppercase px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20">
                <Sparkles className="w-3 h-3" />
                RAG 2.0
              </span>
            </div>
            <p className="text-xs text-surface-500 dark:text-surface-400 hidden sm:block">
              Intelligent repository-aware codebase analysis
            </p>
          </div>
        </div>

        {/* Center: Active Repo Indicator (if connected) */}
        {hasActiveRepo && owner && repo && (
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-100 dark:bg-surface-800/80 border border-surface-200 dark:border-surface-700/80 text-xs">
            <FolderGit2 className="w-3.5 h-3.5 text-brand-500" />
            <span className="font-semibold text-surface-800 dark:text-surface-200">
              {owner}/{repo}
            </span>
            <span className="text-surface-400 dark:text-surface-500">@</span>
            <span className="text-surface-600 dark:text-surface-300 font-mono bg-surface-200 dark:bg-surface-700 px-1.5 py-0.5 rounded text-[10px]">
              {branch || 'main'}
            </span>
            {onOpenExplorer && (
              <button
                type="button"
                onClick={onOpenExplorer}
                className="ml-1 text-xs text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
                title="View repository files"
              >
                <Layers className="w-3 h-3" />
                Files
              </button>
            )}
          </div>
        )}

        {/* Right Actions */}
        <div className="flex items-center gap-2.5">
          {/* Backend Health Status Badge */}
          <div
            className={`hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
              isBackendOnline === true
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800/60'
                : isBackendOnline === false
                ? 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800/60'
                : 'bg-surface-100 text-surface-600 border-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:border-surface-700'
            }`}
            title={
              isBackendOnline === true
                ? `FastAPI Backend Online (Gemini: ${health?.gemini_configured ? 'Active' : 'Missing Key'})`
                : 'FastAPI Backend Offline — check if backend is running on :8000'
            }
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isBackendOnline === true
                  ? 'bg-emerald-500 animate-pulse'
                  : isBackendOnline === false
                  ? 'bg-rose-500'
                  : 'bg-amber-400'
              }`}
            />
            <Activity className="w-3 h-3" />
            <span className="text-[11px]">
              {isBackendOnline === true ? 'API Live' : isBackendOnline === false ? 'API Offline' : 'Checking'}
            </span>
          </div>

          {/* Theme Toggle Button */}
          <button
            type="button"
            onClick={onToggleTheme}
            aria-label="Toggle color theme"
            className="p-2 rounded-lg text-surface-600 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors border border-surface-200 dark:border-surface-700/80"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-surface-700" />}
          </button>

          {/* GitHub Star Link */}
          <a
            href="https://github.com/Aditya-552003/chat-with-code"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-surface-700 dark:text-surface-200 bg-surface-100 dark:bg-surface-800 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors border border-surface-200 dark:border-surface-700/80"
          >
            <Github className="w-4 h-4" />
            <span className="hidden sm:inline">Star on GitHub</span>
          </a>
        </div>
      </div>
    </header>
  );
}
