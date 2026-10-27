'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Square,
  Trash2,
  Download,
  CornerDownLeft,
} from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  onClear: () => void;
  onExport: () => void;
  isLoading: boolean;
  disabled: boolean;
  placeholder?: string;
  hasMessages: boolean;
}

export function ChatInput({
  onSend,
  onStop,
  onClear,
  onExport,
  isLoading,
  disabled,
  placeholder = 'Ask anything about this repository (e.g., "Where is authentication handled?")...',
  hasMessages,
}: ChatInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180,
      )}px`;
    }
  }, [text]);

  const handleSubmit = () => {
    if (text.trim() && !disabled && !isLoading) {
      onSend(text.trim());
      setText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-white/90 dark:bg-surface-900/90 backdrop-blur-md border-t border-surface-200 dark:border-surface-800 transition-colors p-4">
      <div className="max-w-4xl mx-auto space-y-2.5">
        {/* Input container */}
        <div className="relative rounded-2xl border border-surface-300 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/90 focus-within:ring-2 focus-within:ring-brand-500/30 focus-within:border-brand-500 transition-all shadow-sm">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={
              disabled
                ? 'Load and index a repository first to start asking questions...'
                : placeholder
            }
            className="w-full px-4 pt-3.5 pb-12 rounded-2xl bg-transparent resize-none text-sm text-surface-900 dark:text-surface-100 placeholder-surface-400 focus:outline-none disabled:opacity-50"
          />

          {/* Action buttons inside textarea footer */}
          <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between pointer-events-none">
            {/* Left side hint */}
            <div className="flex items-center gap-1.5 text-[11px] text-surface-400 pointer-events-auto">
              <CornerDownLeft className="w-3 h-3" />
              <span className="hidden sm:inline">Press Enter to send, Shift+Enter for new line</span>
            </div>

            {/* Right side buttons */}
            <div className="flex items-center gap-2 pointer-events-auto">
              {isLoading ? (
                <button
                  type="button"
                  onClick={onStop}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-medium shadow-sm transition-all"
                  title="Stop generating"
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                  <span>Stop</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={disabled || !text.trim()}
                  className="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-brand-600 hover:bg-brand-700 text-white disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-brand-500/20 active:scale-95 transition-all"
                  title="Send message"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Global Chat Toolbar */}
        {hasMessages && (
          <div className="flex items-center justify-between text-xs px-1 text-surface-500 dark:text-surface-400">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClear}
                className="inline-flex items-center gap-1 hover:text-rose-600 dark:hover:text-rose-400 transition-colors"
                title="Clear current conversation"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear chat</span>
              </button>
              <span>•</span>
              <button
                type="button"
                onClick={onExport}
                className="inline-flex items-center gap-1 hover:text-brand-600 dark:hover:text-brand-400 transition-colors"
                title="Download chat history as Markdown"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export as Markdown</span>
              </button>
            </div>
            <span className="text-[11px] opacity-70">Powered by Gemini 2.5 Flash & BAAI/bge-small-en</span>
          </div>
        )}
      </div>
    </div>
  );
}
