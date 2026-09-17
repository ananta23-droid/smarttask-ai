import React, { useState } from 'react';
import TaskItem from './TaskItem';

const TaskList = ({ tasks, onUpdate, onDelete, onStartEdit, isLoading }) => {
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredTasks = tasks.filter((task) => {
    if (statusFilter === 'ALL') return true;
    return task.status === statusFilter;
  });

  if (isLoading && tasks.length === 0) {
    return (
      <div className="card">
        <div className="empty-state">
          <div className="empty-icon">⏳</div>
          <h3>Loading your tasks...</h3>
          <p>Connecting to backend and MongoDB.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="task-list-header">
        <h2 className="card-title" style={{ margin: 0 }}>
          <span>Your Tasks ({filteredTasks.length})</span>
        </h2>

        {/* Status Filters */}
        <div className="filter-bar">
          <button
            type="button"
            className={`filter-btn ${statusFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setStatusFilter('ALL')}
          >
            All ({tasks.length})
          </button>
          <button
            type="button"
            className={`filter-btn ${statusFilter === 'TODO' ? 'active' : ''}`}
            onClick={() => setStatusFilter('TODO')}
          >
            To Do
          </button>
          <button
            type="button"
            className={`filter-btn ${statusFilter === 'IN_PROGRESS' ? 'active' : ''}`}
            onClick={() => setStatusFilter('IN_PROGRESS')}
          >
            In Progress
          </button>
          <button
            type="button"
            className={`filter-btn ${statusFilter === 'COMPLETED' ? 'active' : ''}`}
            onClick={() => setStatusFilter('COMPLETED')}
          >
            Completed
          </button>
        </div>
      </div>

      {filteredTasks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No tasks found</h3>
          <p>
            {statusFilter === 'ALL'
              ? "You haven't created any tasks yet. Use the form on the left to get started!"
              : `No tasks currently in the "${statusFilter.replace('_', ' ')}" state.`}
          </p>
        </div>
      ) : (
        <div className="task-grid">
          {filteredTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onUpdate={onUpdate}
              onDelete={onDelete}
              onStartEdit={onStartEdit}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;
