'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  User,
  Bot,
  Copy,
  Check,
  RotateCcw,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '@/types';
import { SourceCard } from './SourceCard';

interface ChatMessageProps {
  message: ChatMessageType;
  onRetry?: () => void;
}

export function ChatMessage({ message, onRetry }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(true);

  const isUser = message.role === 'user';
  const hasSources = message.sources && message.sources.length > 0;

  const handleCopyMessage = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`group w-full py-4 px-4 sm:px-6 rounded-2xl transition-colors ${
        isUser
          ? 'bg-brand-50/60 dark:bg-brand-950/20 border border-brand-100 dark:border-brand-900/30'
          : 'bg-white dark:bg-surface-850 border border-surface-200/80 dark:border-surface-800 shadow-sm'
      }`}
    >
      <div className="flex items-start gap-3.5">
        {/* Avatar */}
        <div
          className={`flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-xl shadow-sm ${
            isUser
              ? 'bg-gradient-to-tr from-brand-600 to-indigo-600 text-white'
              : 'bg-gradient-to-tr from-purple-600 via-indigo-600 to-brand-500 text-white ring-1 ring-white/20'
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Content Body */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-surface-900 dark:text-surface-100">
                {isUser ? 'You' : 'Code Assistant'}
              </span>
              <span className="text-[10px] text-surface-400 dark:text-surface-500">
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>

            {/* Actions (Copy / Retry) */}
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                type="button"
                onClick={handleCopyMessage}
                className="p-1 rounded text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
                title="Copy message"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              {!isUser && onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className="p-1 rounded text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
                  title="Regenerate response"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Message Markdown */}
          <div className="prose prose-sm dark:prose-invert max-w-none text-surface-800 dark:text-surface-200 leading-relaxed break-words">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || '');
                  const language = match ? match[1] : '';

                  if (!inline && language) {
                    return (
                      <div className="relative my-3 rounded-xl overflow-hidden border border-surface-700/80 shadow-md">
                        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-900 border-b border-surface-700/80 text-[11px] font-mono text-surface-300">
                          <span>{language}</span>
                          <button
                            type="button"
                            onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                            className="p-1 rounded hover:bg-surface-800 text-surface-400 hover:text-white transition-colors"
                            title="Copy code"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                        <SyntaxHighlighter
                          style={oneDark}
                          language={language}
                          PreTag="div"
                          customStyle={{
                            margin: 0,
                            padding: '1rem',
                            fontSize: '0.8rem',
                            background: '#0d1117',
                          }}
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      </div>
                    );
                  }

                  return (
                    <code
                      className="px-1.5 py-0.5 rounded bg-surface-100 dark:bg-surface-800 text-brand-600 dark:text-brand-300 font-mono text-xs"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>

            {message.isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-brand-500 animate-pulse align-middle" />
            )}
          </div>

          {/* Source Citations Accordion */}
          {hasSources && (
            <div className="mt-4 pt-3 border-t border-surface-200 dark:border-surface-800">
              <div
                onClick={() => setShowSources(!showSources)}
                className="flex items-center justify-between cursor-pointer py-1 text-xs font-semibold text-surface-600 dark:text-surface-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors select-none"
              >
                <div className="flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-brand-500" />
                  <span>
                    Referenced Sources ({message.sources.length})
                  </span>
                </div>
                {showSources ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </div>

              {showSources && (
                <div className="mt-2 space-y-2">
                  {message.sources.map((source, idx) => (
                    <SourceCard key={`${source.file_path}-${idx}`} source={source} index={idx} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
