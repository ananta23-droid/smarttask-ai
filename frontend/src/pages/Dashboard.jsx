import React, { useState, useEffect, useCallback } from 'react';
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  summarizeTasks,
  checkHealth,
} from '../services/api';
import TaskForm from '../components/TaskForm';
import TaskList from '../components/TaskList';

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [isCreatingTask, setIsCreatingTask] = useState(false);

  // Health and System State
  const [serverHealth, setServerHealth] = useState(null);

  // Alert and Feedback State
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // AI State
  const [aiResult, setAiResult] = useState(null);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [aiError, setAiError] = useState('');

  // Edit Modal State
  const [editingTask, setEditingTask] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editPriority, setEditPriority] = useState('MEDIUM');
  const [editStatus, setEditStatus] = useState('TODO');
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  // Clear feedback messages after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // Check health and load tasks
  const loadTasksAndHealth = useCallback(async () => {
    setIsLoadingTasks(true);
    setErrorMessage('');
    try {
      const [tasksData, healthData] = await Promise.allSettled([
        getTasks(),
        checkHealth(),
      ]);

      if (tasksData.status === 'fulfilled') {
        setTasks(tasksData.value);
      } else {
        const errorDetail =
          tasksData.reason?.response?.data?.detail ||
          'Failed to connect to backend server. Please verify the backend is running and CORS/network settings are correct.';
        setErrorMessage(errorDetail);
      }
      if (healthData.status === 'fulfilled') 
        {
          setServerHealth(healthData.value);
        } 
      else{
           setServerHealth({ status: 'offline', database: 'disconnected' });
          }

     
    } catch (err) {
      setErrorMessage('Unexpected error loading data.');
    } finally {
      setIsLoadingTasks(false);
    }
  }, []);

  useEffect(() => {
    loadTasksAndHealth();
  }, [loadTasksAndHealth]);

  // Create Task Handler
  const handleCreateTask = async (taskPayload) => {
    setIsCreatingTask(true);
    setErrorMessage('');
    try {
      const created = await createTask(taskPayload);
      setTasks((prev) => [created, ...prev]);
      setSuccessMessage(`Task "${created.title}" successfully created!`);
      return true;
    } catch (err) {
      const detail =
        err.response?.data?.detail ||
        (Array.isArray(err.response?.data?.detail)
          ? err.response.data.detail.map((d) => d.msg).join(', ')
          : 'Failed to create task. Please check your inputs.');
      setErrorMessage(detail);
      return false;
    } finally {
      setIsCreatingTask(false);
    }
  };

  // Update Task Handler
  const handleUpdateTask = async (taskId, updateData) => {
    try {
      const updated = await updateTask(taskId, updateData);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
      setSuccessMessage('Task updated successfully.');
      return true;
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to update task.';
      setErrorMessage(detail);
      return false;
    }
  };

  // Delete Task Handler
  const handleDeleteTask = async (taskId) => {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      setSuccessMessage('Task deleted successfully.');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to delete task.';
      setErrorMessage(detail);
    }
  };

  // Edit Modal Handlers
  const handleStartEdit = (task) => {
    setEditingTask(task);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditPriority(task.priority);
    setEditStatus(task.status);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editTitle.trim()) {
      setErrorMessage('Title cannot be empty.');
      return;
    }

    setIsSavingEdit(true);
    const success = await handleUpdateTask(editingTask.id, {
      title: editTitle.trim(),
      description: editDescription.trim(),
      priority: editPriority,
      status: editStatus,
    });
    setIsSavingEdit(false);

    if (success) {
      setEditingTask(null);
    }
  };

  // AI Summarize Handler
  const handleSummarize = async () => {
    if (tasks.length === 0) {
      setAiError('Please create at least one task before requesting an AI summary.');
      return;
    }

    setIsSummarizing(true);
    setAiError('');
    try {
      const payload = tasks.map((t) => ({
        title: t.title,
        description: t.description,
        priority: t.priority,
        status: t.status,
      }));

      const result = await summarizeTasks(payload);
      setAiResult(result);
    } catch (err) {
      const detail =
        err.response?.data?.detail ||
        'AI summarization failed. Verify that your OPENROUTER_API_KEY is configured in backend/.env.';
      setAiError(detail);
    } finally {
      setIsSummarizing(false);
    }
  };

  const isBackendOnline =
    serverHealth?.status === 'ok' || serverHealth?.status === 'degraded';
  const isDbConnected = serverHealth?.database === 'connected';

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-badge">⚡ Full-Stack Task & AI Engine</div>
        <h1 className="app-title">SmartTask AI</h1>
        <p className="app-subtitle">
          Manage your tasks and let AI help you prioritize them.
        </p>

        {/* Backend & Database Health Indicator */}
        <div className="health-indicator">
          <span className={`status-dot ${isDbConnected ? 'active' : ''}`}></span>
          <span>
            FastAPI:{' '}
            <strong style={{ color: isBackendOnline ? '#38bdf8' : '#f87171' }}>
              {isBackendOnline ? 'ONLINE' : 'OFFLINE'}
            </strong>{' '}
            | MongoDB:{' '}
            <strong style={{ color: isDbConnected ? '#34d399' : '#f87171' }}>
              {isDbConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </strong>
          </span>
        </div>
      </header>

      {/* Global Alerts */}
      {errorMessage && (
        <div className="banner banner-error">
          <span>⚠️ {errorMessage}</span>
          <button
            type="button"
            className="banner-close"
            onClick={() => setErrorMessage('')}
          >
            ✕
          </button>
        </div>
      )}

      {successMessage && (
        <div className="banner banner-success">
          <span>✓ {successMessage}</span>
          <button
            type="button"
            className="banner-close"
            onClick={() => setSuccessMessage('')}
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Dashboard Layout */}
      <main className="dashboard-grid">
        {/* Left Column: Task Creation & AI Assistant */}
        <div className="dashboard-sidebar">
          <TaskForm
            onTaskCreated={handleCreateTask}
            isCreating={isCreatingTask}
          />

          {/* AI Prioritization Card */}
          <div className="card ai-card">
            <h2 className="card-title">
              <span>SmartTask AI Assistant</span>
              <span style={{ fontSize: '1.2rem' }}>✨</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.25rem' }}>
              Send your current tasks to the AI model to extract executive summaries, rank high-priority bottlenecks, and get an optimized execution order.
            </p>

            <button
              id="btn-ai-summarize"
              type="button"
              className="btn btn-ai"
              onClick={handleSummarize}
              disabled={isSummarizing || tasks.length === 0}
            >
              {isSummarizing ? '🧠 Analyzing Tasks...' : '✨ Summarize My Tasks'}
            </button>

            {aiError && (
              <div
                className="banner banner-error"
                style={{ marginTop: '1rem', padding: '0.6rem 0.8rem', fontSize: '0.85rem' }}
              >
                <span>{aiError}</span>
              </div>
            )}

            {/* AI Results Presentation */}
            {aiResult && (
              <div className="ai-result-box">
                <div className="ai-meta-block">
                  <div className="ai-meta-label">📊 Executive Summary</div>
                  <p className="ai-meta-content">{aiResult.summary}</p>
                </div>

                {aiResult.highest_priority_tasks?.length > 0 && (
                  <div className="ai-meta-block">
                    <div className="ai-meta-label">🔥 Highest Priority Focus</div>
                    <div>
                      {aiResult.highest_priority_tasks.map((taskName, idx) => (
                        <span key={idx} className="ai-pill-tag">
                          {taskName}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {aiResult.recommended_order?.length > 0 && (
                  <div className="ai-meta-block">
                    <div className="ai-meta-label">🎯 Recommended Execution Order</div>
                    <ol className="ai-ordered-list">
                      {aiResult.recommended_order.map((taskName, idx) => (
                        <li key={idx}>{taskName}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {aiResult.recommendation && (
                  <div className="ai-meta-block" style={{ marginBottom: 0 }}>
                    <div className="ai-meta-label">💡 AI Recommendation</div>
                    <div className="ai-recommendation-box">
                      {aiResult.recommendation}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Task List */}
        <div className="dashboard-content">
          <TaskList
            tasks={tasks}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask}
            onStartEdit={handleStartEdit}
            isLoading={isLoadingTasks}
          />
        </div>
      </main>

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="modal-overlay" onClick={() => setEditingTask(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Edit Task</h3>
              <button
                type="button"
                className="banner-close"
                onClick={() => setEditingTask(null)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveEdit}>
              <div className="form-group">
                <label className="form-label" htmlFor="edit-title">
                  Task Title *
                </label>
                <input
                  id="edit-title"
                  type="text"
                  className="form-input"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  disabled={isSavingEdit}
                  required
                  maxLength={150}
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="edit-desc">
                  Description
                </label>
                <textarea
                  id="edit-desc"
                  className="form-textarea"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  disabled={isSavingEdit}
                  maxLength={1000}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label" htmlFor="edit-priority">
                    Priority
                  </label>
                  <select
                    id="edit-priority"
                    className="form-select"
                    value={editPriority}
                    onChange={(e) => setEditPriority(e.target.value)}
                    disabled={isSavingEdit}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="edit-status">
                    Status
                  </label>
                  <select
                    id="edit-status"
                    className="form-select"
                    value={editStatus}
                    onChange={(e) => setEditStatus(e.target.value)}
                    disabled={isSavingEdit}
                  >
                    <option value="TODO">To Do</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="COMPLETED">Completed</option>
                  </select>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setEditingTask(null)}
                  disabled={isSavingEdit}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSavingEdit || !editTitle.trim()}
                >
                  {isSavingEdit ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
