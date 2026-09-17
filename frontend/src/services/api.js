import axios from 'axios';

// Base API configuration pointing to the FastAPI backend
const rawBaseUrl =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000';

const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

/**
 * Fetch all tasks from the backend.
 */
export const getTasks = async () => {
  const response = await apiClient.get('/api/tasks');
  return response.data;
};

/**
 * Fetch a single task by ID.
 */
export const getTask = async (taskId) => {
  const response = await apiClient.get(`/api/tasks/${taskId}`);
  return response.data;
};

/**
 * Create a new task.
 */
export const createTask = async (taskData) => {
  const response = await apiClient.post('/api/tasks', taskData);
  return response.data;
};

/**
 * Update an existing task.
 */
export const updateTask = async (taskId, updateData) => {
  const response = await apiClient.put(`/api/tasks/${taskId}`, updateData);
  return response.data;
};

/**
 * Delete a task by ID.
 */
export const deleteTask = async (taskId) => {
  const response = await apiClient.delete(`/api/tasks/${taskId}`);
  return response.data;
};

/**
 * Request an AI summary, ranking, and actionable recommendation for tasks.
 */
export const summarizeTasks = async (tasks) => {
  const response = await apiClient.post('/api/ai/summarize', { tasks });
  return response.data;
};

/**
 * Check backend service and database health.
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;
