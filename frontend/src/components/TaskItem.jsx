import React, { useState } from 'react';

const TaskItem = ({ task, onUpdate, onDelete, onStartEdit }) => {
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleStatusChange = async (e) => {
    const newStatus = e.target.value;
    setIsUpdatingStatus(true);
    try {
      await onUpdate(task.id, { status: newStatus });
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleDelete = async () => {
    const confirmDelete = window.confirm(`Are you sure you want to delete "${task.title}"?`);
    if (!confirmDelete) return;

    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsDeleting(false);
    }
  };

  const formattedDate = new Date(task.created_at).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  const isDone = task.status === 'COMPLETED';

  return (
    <div className={`task-item ${isDone ? 'completed' : ''}`}>
      <div className="task-item-header">
        <h3 className={`task-title ${isDone ? 'strikethrough' : ''}`}>{task.title}</h3>
        <div className="task-badges">
          <span className={`badge badge-priority-${task.priority}`}>
            {task.priority}
          </span>
          <span className={`badge badge-status-${task.status}`}>
            {task.status.replace('_', ' ')}
          </span>
        </div>
      </div>

      {task.description && <p className="task-desc">{task.description}</p>}

      <div className="task-footer">
        <span className="task-date">Created: {formattedDate}</span>

        <div className="task-actions">
          {/* Quick status dropdown */}
          <select
            className="status-select"
            value={task.status}
            onChange={handleStatusChange}
            disabled={isUpdatingStatus || isDeleting}
            title="Update task status"
          >
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
          </select>

          {/* Edit button */}
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => onStartEdit(task)}
            disabled={isDeleting}
            title="Edit task title and details"
          >
            ✏️ Edit
          </button>

          {/* Delete button */}
          <button
            type="button"
            className="btn btn-danger btn-sm"
            onClick={handleDelete}
            disabled={isDeleting}
            title="Delete this task"
          >
            {isDeleting ? 'Deleting...' : '🗑️ Delete'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskItem;
