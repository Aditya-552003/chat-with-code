/**
 * API client for Chat with Code backend.
 * All API calls go through this module.
 */

import type {
  ChatRequest,
  ChatResponse,
  Conversation,
  HealthResponse,
  IndexingJob,
  RepositoryInfo,
  RepositoryLoadRequest,
  SourceReference,
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(body.detail || 'Request failed', res.status);
  }

  return res.json();
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/* ─── Health ───────────────────────────────────────── */

export async function checkHealth(): Promise<HealthResponse> {
  return request('/api/health');
}

/* ─── Repositories ─────────────────────────────────── */

export async function loadRepository(data: RepositoryLoadRequest): Promise<IndexingJob> {
  return request('/api/repositories/load', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getJobStatus(jobId: string): Promise<IndexingJob> {
  return request(`/api/repositories/jobs/${jobId}`);
}

export async function getRepository(repositoryId: string): Promise<RepositoryInfo> {
  return request(`/api/repositories/${repositoryId}`);
}

/* ─── Chat ─────────────────────────────────────────── */

export async function sendMessage(data: ChatRequest): Promise<ChatResponse> {
  return request('/api/chat', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export interface StreamCallbacks {
  onChunk: (text: string) => void;
  onSources: (sources: SourceReference[]) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export function streamMessage(
  data: ChatRequest,
  callbacks: StreamCallbacks,
): AbortController {
  const controller = new AbortController();
  const url = `${API_BASE}/api/chat/stream`;

  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        callbacks.onError(body.detail || 'Stream failed');
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) {
        callbacks.onError('Streaming not supported');
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            const eventType = line.slice(7).trim();
            // Next line should be data
            continue;
          }
          if (line.startsWith('data: ')) {
            const rawData = line.slice(6);
            try {
              const parsed = JSON.parse(rawData);
              // Determine event type from context
              if ('text' in parsed) {
                callbacks.onChunk(parsed.text);
              } else if ('sources' in parsed) {
                callbacks.onSources(parsed.sources);
              } else if ('error' in parsed) {
                callbacks.onError(parsed.error);
              } else if ('message' in parsed && parsed.message === 'complete') {
                callbacks.onDone();
              }
            } catch {
              // Skip malformed data
            }
          }
        }
      }

      callbacks.onDone();
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        callbacks.onError(err.message || 'Stream connection failed');
      }
    });

  return controller;
}

/* ─── Conversations ────────────────────────────────── */

export async function getConversation(conversationId: string): Promise<Conversation> {
  return request(`/api/conversations/${conversationId}`);
}

export async function clearConversation(conversationId: string): Promise<void> {
  await request(`/api/conversations/${conversationId}`, { method: 'DELETE' });
}

export async function exportConversation(conversationId: string): Promise<{ markdown: string }> {
  return request(`/api/conversations/${conversationId}/export`);
}
