import { useState, useCallback, useRef, useEffect } from 'react';
import type { RepositoryState, IndexingStatus } from '@/types';
import * as api from '@/services/api';

const INITIAL_STATE: RepositoryState = {
  url: '',
  owner: '',
  repo: '',
  branch: '',
  repositoryId: '',
  status: 'queued' as IndexingStatus,
  totalFiles: 0,
  indexedChunks: 0,
  jobId: null,
  error: null,
  isLoading: false,
};

export function useRepository() {
  const [state, setState] = useState<RepositoryState>(INITIAL_STATE);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => stopPolling, [stopPolling]);

  const loadRepository = useCallback(
    async (url: string) => {
      stopPolling();
      setState((s) => ({
        ...s,
        url,
        isLoading: true,
        error: null,
        status: 'queued',
      }));

      try {
        const job = await api.loadRepository({ repository_url: url });
        setState((s) => ({
          ...s,
          repositoryId: job.repository_id,
          jobId: job.job_id,
          status: job.status,
          totalFiles: job.total_files,
          indexedChunks: job.indexed_chunks,
          isLoading: job.status !== 'completed' && job.status !== 'failed',
        }));

        // Parse owner/repo from repository_id
        const parts = job.repository_id.split('-');
        if (parts.length >= 2) {
          setState((s) => ({
            ...s,
            owner: parts[0],
            repo: parts[1],
            branch: parts.slice(2).join('-') || 'main',
          }));
        }

        if (job.status === 'completed') {
          setState((s) => ({ ...s, isLoading: false }));
          return;
        }

        if (job.status === 'failed') {
          setState((s) => ({
            ...s,
            isLoading: false,
            error: job.error_message || 'Indexing failed',
          }));
          return;
        }

        // Poll for status
        pollRef.current = setInterval(async () => {
          try {
            const status = await api.getJobStatus(job.job_id);
            setState((s) => ({
              ...s,
              status: status.status,
              totalFiles: status.total_files,
              indexedChunks: status.indexed_chunks,
              error: status.error_message,
            }));

            if (status.status === 'completed' || status.status === 'failed') {
              stopPolling();
              setState((s) => ({
                ...s,
                isLoading: false,
                error: status.status === 'failed' ? status.error_message : null,
              }));
            }
          } catch {
            stopPolling();
            setState((s) => ({
              ...s,
              isLoading: false,
              error: 'Lost connection while monitoring indexing.',
            }));
          }
        }, 2000);
      } catch (err) {
        const message = err instanceof api.ApiError ? err.message : 'Failed to load repository';
        setState((s) => ({ ...s, isLoading: false, error: message }));
      }
    },
    [stopPolling],
  );

  const disconnect = useCallback(() => {
    stopPolling();
    setState(INITIAL_STATE);
  }, [stopPolling]);

  const isConnected = state.status === 'completed' && !!state.repositoryId;

  return { ...state, isConnected, loadRepository, disconnect };
}
