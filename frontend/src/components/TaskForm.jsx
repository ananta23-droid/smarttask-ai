import React, { useState } from 'react';

const TaskForm = ({ onTaskCreated, isCreating }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [status, setStatus] = useState('TODO');
  const [validationError, setValidationError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      setValidationError('Please provide a valid task title.');
      return;
    }

    setValidationError('');
    const success = await onTaskCreated({
      title: trimmedTitle,
      description: description.trim(),
      priority,
      status,
    });

    if (success) {
      setTitle('');
      setDescription('');
      setPriority('MEDIUM');
      setStatus('TODO');
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">
        <span>Create New Task</span>
        <span style={{ fontSize: '1.2rem' }}>📝</span>
      </h2>

      {validationError && (
        <div className="banner banner-error" style={{ marginBottom: '1rem', padding: '0.5rem 0.75rem' }}>
          <span>{validationError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="task-title">
            Task Title *
          </label>
          <input
            id="task-title"
            type="text"
            className="form-input"
            placeholder="e.g. Prepare DBMS presentation"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={isCreating}
            required
            maxLength={150}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="task-desc">
            Description
          </label>
          <textarea
            id="task-desc"
            className="form-textarea"
            placeholder="Provide context, deliverables, or checklist..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isCreating}
            maxLength={1000}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label" htmlFor="task-priority">
              Priority
            </label>
            <select
              id="task-priority"
              className="form-select"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={isCreating}
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="task-status">
              Status
            </label>
            <select
              id="task-status"
              className="form-select"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              disabled={isCreating}
            >
              <option value="TODO">To Do</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
            </select>
          </div>
        </div>

        <button
          id="btn-create-task"
          type="submit"
          className="btn btn-primary"
          disabled={isCreating || !title.trim()}
        >
          {isCreating ? 'Creating Task...' : '➕ Create Task'}
        </button>
      </form>
    </div>
  );
};

export default TaskForm;
