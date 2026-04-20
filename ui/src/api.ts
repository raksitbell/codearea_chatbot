import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface OllamaConfig {
  url: string;
  model: string;
}

export interface HealthStatus {
  status: string;
}

export interface TestConnectionResult {
    connected: boolean;
    models?: string[];
    models_count?: number;
    error?: string;
    message?: string;
}

export const getOllamaConfig = () => api.get<OllamaConfig>('/api/config/ollama');
export const updateOllamaConfig = (config: OllamaConfig) => api.post('/api/config/ollama', config);
export const getAvailableModels = () => api.get<{ models: string[] }>('/api/config/models');
export const getHealthCheck = () => api.get<HealthStatus>('/api/health');
export const testConnection = (config: OllamaConfig) => api.post<TestConnectionResult>('/api/config/test-connection', config);
