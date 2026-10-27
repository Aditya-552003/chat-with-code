import { useState, useCallback, useRef } from 'react';
import type { ChatMessage, SourceReference } from '@/types';
import * as api from '@/services/api';

function generateId(): string {
  return crypto.randomUUID?.() || Date.now().toString(36) + Math.random().toString(36).slice(2);
}

export function useChat(repositoryId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSources, setActiveSources] = useState<SourceReference[]>([]);
  const conversationIdRef = useRef<string>(generateId());
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!repositoryId || !content.trim() || isLoading) return;

      setError(null);

      // Add user message
      const userMsg: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: content.trim(),
        sources: [],
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);

      // Add placeholder assistant message
      const assistantId = generateId();
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: 'assistant',
        content: '',
        sources: [],
        timestamp: new Date(),
        isStreaming: true,
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setIsLoading(true);

      try {
        const controller = api.streamMessage(
          {
            repository_id: repositoryId,
            conversation_id: conversationIdRef.current,
            message: content.trim(),
          },
          {
            onChunk: (text) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: m.content + text } : m,
                ),
              );
            },
            onSources: (sources) => {
              setMessages((prev) =>
                prev.map((m) => (m.id === assistantId ? { ...m, sources } : m)),
              );
              setActiveSources(sources);
            },
            onDone: () => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, isStreaming: false } : m,
                ),
              );
              setIsLoading(false);
            },
            onError: (errMsg) => {
              setError(errMsg);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: m.content || (errMsg ? `⚠️ ${errMsg}` : 'Failed to generate response.'), isStreaming: false }
                    : m,
                ),
              );
              setIsLoading(false);
            },
          },
        );
        abortRef.current = controller;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setIsLoading(false);
      }
    },
    [repositoryId, isLoading],
  );

  const stopGeneration = useCallback(() => {
    abortRef.current?.abort();
    setIsLoading(false);
    setMessages((prev) =>
      prev.map((m) => (m.isStreaming ? { ...m, isStreaming: false } : m)),
    );
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setActiveSources([]);
    setError(null);
    conversationIdRef.current = generateId();
    // Clear on server too (best-effort)
    if (conversationIdRef.current) {
      api.clearConversation(conversationIdRef.current).catch(() => {});
    }
  }, []);

  const retryLast = useCallback(() => {
    const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUserMsg) {
      // Remove last assistant message
      setMessages((prev) => {
        const idx = prev.length - 1;
        if (idx >= 0 && prev[idx].role === 'assistant') {
          return prev.slice(0, idx);
        }
        return prev;
      });
      sendMessage(lastUserMsg.content);
    }
  }, [messages, sendMessage]);

  return {
    messages,
    isLoading,
    error,
    activeSources,
    conversationId: conversationIdRef.current,
    sendMessage,
    stopGeneration,
    clearMessages,
    retryLast,
    setError,
  };
}
