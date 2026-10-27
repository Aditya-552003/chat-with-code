'use client';

import React from 'react';
import {
  Compass,
  Cpu,
  KeyRound,
  PackageCheck,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
  repoName?: string;
}

const QUESTIONS = [
  {
    icon: Compass,
    title: 'Architecture Overview',
    prompt: 'Can you provide a high-level architectural overview of this project and explain how its core modules interact?',
  },
  {
    icon: Cpu,
    title: 'Entry Points & Workflows',
    prompt: 'Where is the main entry point of this application, and what happens step-by-step during startup or execution?',
  },
  {
    icon: KeyRound,
    title: 'Authentication & Config',
    prompt: 'How is configuration, environment variables, and authentication or security handled in this codebase?',
  },
  {
    icon: PackageCheck,
    title: 'Key Dependencies',
    prompt: 'What are the most critical third-party dependencies used in this repository and what roles do they serve?',
  },
  {
    icon: ShieldAlert,
    title: 'Potential Issues & Refactoring',
    prompt: 'Review the codebase architecture for potential edge cases, performance bottlenecks, or recommended improvements.',
  },
];

export function SuggestedQuestions({ onSelect, repoName }: SuggestedQuestionsProps) {
  return (
    <div className="w-full max-w-4xl mx-auto py-8 px-4">
      <div className="text-center mb-6">
        <h3 className="text-base font-semibold text-surface-800 dark:text-surface-200">
          Repository Indexed & Searchable
        </h3>
        <p className="text-xs text-surface-500 dark:text-surface-400 mt-1">
          {repoName ? `Ask anything about ${repoName} or pick a starter question:` : 'Pick a starter prompt below or write your own:'}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {QUESTIONS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => onSelect(item.prompt)}
              className="flex flex-col text-left p-4 rounded-xl border border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-850 hover:bg-brand-50/50 dark:hover:bg-brand-950/20 hover:border-brand-300 dark:hover:border-brand-800 shadow-sm transition-all group"
            >
              <div className="flex items-center justify-between w-full mb-2">
                <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-brand-100 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400">
                  <Icon className="w-4 h-4" />
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-surface-400 group-hover:text-brand-600 dark:group-hover:text-brand-400 group-hover:translate-x-0.5 transition-all" />
              </div>
              <h4 className="text-xs font-semibold text-surface-900 dark:text-surface-100 mb-1">
                {item.title}
              </h4>
              <p className="text-[11px] text-surface-500 dark:text-surface-400 line-clamp-2 leading-relaxed">
                {item.prompt}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
