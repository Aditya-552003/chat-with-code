/* ─── API Types ─────────────────────────────────────── */

export type IndexingStatus =
  | 'queued'
  | 'loading'
  | 'chunking'
  | 'embedding'
  | 'indexing'
  | 'completed'
  | 'failed';

export type MessageRole = 'user' | 'assistant' | 'system';

export interface HealthResponse {
  status: string;
  version: string;
  gemini_configured: boolean;
  github_configured: boolean;
}

export interface RepositoryLoadRequest {
  repository_url: string;
  branch?: string | null;
}

export interface IndexingJob {
  job_id: string;
  repository_id: string;
  status: IndexingStatus;
  progress_message: string;
  total_files: number;
  indexed_chunks: number;
  error_message: string | null;
}

export interface RepositoryInfo {
  repository_id: string;
  owner: string;
  repo: string;
  branch: string;
  github_url: string;
  status: IndexingStatus;
  total_files: number;
  indexed_chunks: number;
  error_message?: string | null;
}

export interface SourceReference {
  file_path: string;
  language: string | null;
  snippet: string;
  start_line: number | null;
  end_line: number | null;
  github_url: string;
  relevance_score: number | null;
}

export interface ChatRequest {
  repository_id: string;
  conversation_id: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  sources: SourceReference[];
  retrieval_time_ms: number | null;
  generation_time_ms: number | null;
}

export interface ConversationMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources: SourceReference[];
  timestamp: string;
}

export interface Conversation {
  conversation_id: string;
  repository_id: string;
  messages: ConversationMessage[];
  created_at: string;
}

/* ─── App State Types ──────────────────────────────── */

export interface AppState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  sourcePanelOpen: boolean;
}

export interface RepositoryState {
  url: string;
  owner: string;
  repo: string;
  branch: string;
  repositoryId: string;
  status: IndexingStatus;
  totalFiles: number;
  indexedChunks: number;
  jobId: string | null;
  error: string | null;
  isLoading: boolean;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources: SourceReference[];
  timestamp: Date;
  isStreaming?: boolean;
}
