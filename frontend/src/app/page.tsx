'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Code2,
  FolderGit2,
  Sparkles,
  Bot,
  Layers,
  ArrowRight,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { useRepository } from '@/hooks/useRepository';
import { useChat } from '@/hooks/useChat';
import { Header } from '@/components/Header';
import { RepositoryLoader } from '@/components/RepositoryLoader';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { SuggestedQuestions } from '@/components/SuggestedQuestions';
import { RepositoryExplorer } from '@/components/RepositoryExplorer';

export default function HomePage() {
  const { theme, toggleTheme } = useTheme();
  const repo = useRepository();
  const chat = useChat(repo.isConnected ? repo.repositoryId : null);

  const [isExplorerOpen, setIsExplorerOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat when new messages or chunks arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat.messages]);

  // Export conversation as downloadable Markdown file
  const handleExportChat = () => {
    if (!chat.messages.length) return;

    let markdown = `# Chat with Code — Analysis Report\n\n`;
    if (repo.owner && repo.repo) {
      markdown += `**Repository**: [${repo.owner}/${repo.repo}](https://github.com/${repo.owner}/${repo.repo}) (${repo.branch || 'main'})\n`;
      markdown += `**Files Indexed**: ${repo.totalFiles} | **Chunks**: ${repo.indexedChunks}\n\n`;
    }
    markdown += `**Date**: ${new Date().toLocaleString()}\n\n---\n\n`;

    chat.messages.forEach((msg) => {
      markdown += `### ${msg.role === 'user' ? '👤 User' : '🤖 Code Assistant'}\n\n`;
      markdown += `${msg.content}\n\n`;
      if (msg.sources && msg.sources.length > 0) {
        markdown += `**Sources Referenced**:\n`;
        msg.sources.forEach((s) => {
          markdown += `- \`${s.file_path}\`${s.start_line ? ` (Lines ${s.start_line}-${s.end_line})` : ''} — [GitHub Link](${s.github_url})\n`;
        });
        markdown += `\n`;
      }
      markdown += `---\n\n`;
    });

    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chat-with-code-${repo.repo || 'export'}-${Date.now()}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Navigation Header */}
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        repositoryId={repo.repositoryId}
        owner={repo.owner}
        repo={repo.repo}
        branch={repo.branch}
        hasActiveRepo={repo.isConnected}
        onOpenExplorer={() => setIsExplorerOpen(true)}
      />

      {/* Repository Selector & Status Bar */}
      <RepositoryLoader
        url={repo.url}
        owner={repo.owner}
        repo={repo.repo}
        branch={repo.branch}
        status={repo.status}
        totalFiles={repo.totalFiles}
        indexedChunks={repo.indexedChunks}
        isLoading={repo.isLoading}
        error={repo.error}
        isConnected={repo.isConnected}
        onLoad={repo.loadRepository}
        onDisconnect={() => {
          repo.disconnect();
          chat.clearMessages();
        }}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col justify-between max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* State 1: No Repository Loaded (Hero Welcome) */}
        {!repo.isConnected && !repo.isLoading && (
          <div className="my-auto py-12 flex flex-col items-center text-center max-w-2xl mx-auto space-y-6">
            <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-purple-600 text-white shadow-xl shadow-brand-500/25 ring-4 ring-brand-500/10">
              <Code2 className="w-8 h-8" />
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-surface-900 dark:text-white">
                Understand Any Codebase in Seconds
              </h1>
              <p className="text-sm sm:text-base text-surface-600 dark:text-surface-400 leading-relaxed">
                Connect any public GitHub repository to index its code structure, extract semantic AST blocks, and query your codebase using Gemini 2.5 Flash and dense embeddings.
              </p>
            </div>

            {/* Feature Highlights */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full pt-4">
              <div className="p-4 rounded-xl border border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-850 shadow-sm text-left">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 mb-2">
                  <Zap className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-semibold text-surface-900 dark:text-white mb-1">
                  Semantic Code Search
                </h4>
                <p className="text-[11px] text-surface-500 dark:text-surface-400">
                  Dense 384d BAAI embeddings locate matching functions, classes, and logic.
                </p>
              </div>

              <div className="p-4 rounded-xl border border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-850 shadow-sm text-left">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 mb-2">
                  <Layers className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-semibold text-surface-900 dark:text-white mb-1">
                  Accurate Citations
                </h4>
                <p className="text-[11px] text-surface-500 dark:text-surface-400">
                  Direct GitHub permalinks with exact file paths, line numbers, and snippets.
                </p>
              </div>

              <div className="p-4 rounded-xl border border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-850 shadow-sm text-left">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 mb-2">
                  <Sparkles className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-semibold text-surface-900 dark:text-white mb-1">
                  Gemini 2.5 Flash
                </h4>
                <p className="text-[11px] text-surface-500 dark:text-surface-400">
                  High-speed streaming responses with comprehensive code explanations.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* State 2: Repo Connected, No Messages (Starter Prompts) */}
        {repo.isConnected && chat.messages.length === 0 && (
          <SuggestedQuestions
            repoName={`${repo.owner}/${repo.repo}`}
            onSelect={(q) => chat.sendMessage(q)}
          />
        )}

        {/* State 3: Active Conversation Message Feed */}
        {chat.messages.length > 0 && (
          <div className="w-full max-w-4xl mx-auto space-y-4 my-4 flex-1">
            {chat.messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                onRetry={msg.role === 'assistant' ? chat.retryLast : undefined}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Bottom Chat Input Bar */}
        <div className="w-full mt-auto">
          <ChatInput
            onSend={chat.sendMessage}
            onStop={chat.stopGeneration}
            onClear={chat.clearMessages}
            onExport={handleExportChat}
            isLoading={chat.isLoading}
            disabled={!repo.isConnected}
            hasMessages={chat.messages.length > 0}
          />
        </div>
      </main>

      {/* Slide-Over Repository Explorer Drawer */}
      <RepositoryExplorer
        isOpen={isExplorerOpen}
        onClose={() => setIsExplorerOpen(false)}
        repoState={repo}
      />
    </div>
  );
}
