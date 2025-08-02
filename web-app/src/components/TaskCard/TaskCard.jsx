import { useDrag } from 'react-dnd';
import PropTypes from 'prop-types';
import React from 'react';
import './TaskCard.css';
import { TaskStatus } from '../../types/dto/TaskDTO';

function formatDeadline(deadline) {
  if (!deadline) return null;
  const diffMs = new Date(deadline) - new Date();
  const daysLeft = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  return daysLeft >= 0 ? `${daysLeft} дн. осталось` : `Просрочено`;
}

const getStatusColor = (status) => {
  switch(status) {
    case TaskStatus.BACKLOG: return '#94a3b8';
    case TaskStatus.APPROVED: return '#60a5fa';
    case TaskStatus.CODING: return '#f59e0b';
    case TaskStatus.TESTING: return '#a78bfa';
    case TaskStatus.DEPLOYED: return '#10b981';
    default: return '#d1d5db';
  }
};

const TaskCard = React.memo(({ task, onMoveTask, columnId }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'TASK',
    item: { id: task.id, columnId },
    collect: monitor => ({
      isDragging: monitor.isDragging(),
    }),
  });

  // Проверяем, является ли assignedTo объектом
  const isAssignedToObject = task.assignedTo && typeof task.assignedTo === 'object';

  return (
    <div
      ref={drag}
      className={`task-card ${isDragging ? 'dragging' : ''}`}
      style={{ borderLeft: `4px solid ${getStatusColor(task.status)}` }}
    >
      <div className="task-header">
        <div className="task-title">{task.title}</div>
        <div className="task-type" data-type={task.type}>
          {task.type === 'private' ? 'Приватная' : 'Публичная'}
        </div>
      </div>

      <div className="task-meta">
        <div className="task-date">Создано: {task.date || task.createdAt.slice(0, 10)}</div>
        {task.deadline && (
          <div className={`task-deadline ${new Date(task.deadline) < new Date() ? 'overdue' : ''}`}>
            Дедлайн: {new Date(task.deadline).toLocaleDateString()} ({formatDeadline(task.deadline)})
          </div>
        )}
        {task.budget !== null && (
          <div className="task-budget">Бюджет: {task.budget.toLocaleString()} ₽</div>
        )}
        <div className="task-priority">
          Приоритет: 
          <span className="priority-stars">
            {[...Array(5)].map((_, i) => (
              <span key={i} className={i < task.priority ? 'active' : ''}>★</span>
            ))}
          </span>
        </div>
      </div>

      {task.description && (
        <div className="task-description">
          {task.description.length > 100 
            ? `${task.description.substring(0, 100)}...` 
            : task.description}
        </div>
      )}

      {task.tags && task.tags.length > 0 && (
        <div className="task-tags">
          {task.tags.map(tag => (
            <span key={tag} className={`tag ${tag.toLowerCase()}`}>
              {tag}
            </span>
          ))}
        </div>
      )}

      {isAssignedToObject && (
        <div className="task-assignee">
          <img 
            className="assignee-avatar" 
            src={task.assignedTo.avatarUrl || "/assets/avatars/default-avatar.jpg"} 
            alt={task.assignedTo.username} 
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "/assets/avatars/default-avatar.jpg";
            }}
          />
          <div className="assignee-info">
            <div>@{task.assignedTo.username}</div>
            <div>Рейтинг: {task.assignedTo.rating?.toFixed(1) || 'Н/Д'}</div>
            <div>Выполнено: {task.assignedTo.completedTasks || 0}</div>
          </div>
        </div>
      )}
    </div>
  );
});

TaskCard.propTypes = {
  task: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    status: PropTypes.string.isRequired,
    createdAt: PropTypes.string,
    deadline: PropTypes.string,
    budget: PropTypes.number,
    priority: PropTypes.number,
    tags: PropTypes.arrayOf(PropTypes.string),
    type: PropTypes.string,
    assignedTo: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        username: PropTypes.string,
        avatarUrl: PropTypes.string,
        rating: PropTypes.number,
        completedTasks: PropTypes.number,
      })
    ]),
  }).isRequired,
  onMoveTask: PropTypes.func.isRequired,
  columnId: PropTypes.string.isRequired,
};

TaskCard.displayName = 'TaskCard';

export default TaskCard;