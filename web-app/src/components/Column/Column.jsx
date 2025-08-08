import { useDrop } from 'react-dnd';
import { useState } from 'react';
import PropTypes from 'prop-types';
import TaskCard from '../TaskCard/TaskCard';
import { TaskType } from '../../types/dto/TaskDTO';
import './Column.css';

const Column = ({ title, tasks, columnId, onMoveTask, onAddTask }) => {
  const [, drop] = useDrop({
    accept: 'TASK',
    drop: (item) => {
      if (item.columnId !== columnId) {
        onMoveTask(item.id, item.columnId, columnId);
      }
    },
  });

  const [addingTask, setAddingTask] = useState(false);
  const [form, setForm] = useState({
    title: '',
    description: '',
    deadline: '',
    budget: '',
    priority: 3,
    tags: '',
    type: TaskType.PUBLIC,
    assignedTo: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    
    // Очищаем ошибку при изменении поля
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleTagChange = e => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
    setForm(prev => ({ ...prev, tags }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!form.title.trim()) {
      newErrors.title = 'Название задачи обязательно';
    }
    
    if (form.budget && (isNaN(form.budget) || Number(form.budget) < 0)) {
      newErrors.budget = 'Бюджет должен быть положительным числом';
    }
    
    if (form.deadline && new Date(form.deadline) < new Date()) {
      newErrors.deadline = 'Дедлайн не может быть в прошлом';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = e => {
    e.preventDefault();
    
    if (!validateForm()) {
      return false; // Явно возвращаем false для предотвращения отправки формы
    }

    try {
      onAddTask(columnId, {
        title: form.title.trim(),
        description: form.description.trim(),
        status: columnId,
        deadline: form.deadline ? new Date(form.deadline).toISOString() : null,
        budget: form.budget ? Number(form.budget) : null,
        priority: Number(form.priority),
        tags: form.tags,
        type: form.type,
        assignedTo: form.assignedTo.trim() || null,
        createdAt: new Date().toISOString(),
        rating: null,
        boardId: "default-board",
        parentId: null
      });
      
      setForm({ 
        title: '',
        description: '',
        deadline: '',
        budget: '',
        priority: 3,
        tags: '',
        type: TaskType.PUBLIC,
        assignedTo: ''
      });
      setErrors({});
      setAddingTask(false);
    } catch (error) {
      console.error('Error creating task:', error);
      // Используем более информативное сообщение об ошибке
      const errorMessage = error.response?.data?.detail || 'Произошла ошибка при создании задачи. Попробуйте еще раз.';
      alert(errorMessage);
    }
    
    return false; // Дополнительная защита от отправки формы
  };

  return (
    <div ref={drop} className="column">
      <h2 className="column-title">{title}</h2>
      {tasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          columnId={columnId}
          onMoveTask={onMoveTask}
        />
      ))}

      {!addingTask && (
        <button className="add-task-btn" onClick={() => setAddingTask(true)}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Добавить задачу
        </button>
      )}

      {addingTask && (
        <form className="add-task-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <label>Название*</label>
            <input
              type="text"
              name="title"
              placeholder="Название задачи"
              value={form.title}
              onChange={handleChange}
              className={errors.title ? 'error' : ''}
              required
            />
            {errors.title && <span className="error-message">{errors.title}</span>}
          </div>

          <div className="form-row">
            <label>Описание</label>
            <textarea
              name="description"
              placeholder="Описание задачи"
              value={form.description}
              onChange={handleChange}
              rows={3}
            />
          </div>

          <div className="form-row">
            <label>Дедлайн</label>
            <input
              type="date"
              name="deadline"
              value={form.deadline}
              onChange={handleChange}
              className={errors.deadline ? 'error' : ''}
            />
            {errors.deadline && <span className="error-message">{errors.deadline}</span>}
          </div>

          <div className="form-row">
            <label>Бюджет (₽)</label>
            <input
              type="number"
              name="budget"
              placeholder="Бюджет"
              value={form.budget}
              onChange={handleChange}
              min={0}
              className={errors.budget ? 'error' : ''}
            />
            {errors.budget && <span className="error-message">{errors.budget}</span>}
          </div>

          <div className="form-row">
            <label>Приоритет</label>
            <select name="priority" value={form.priority} onChange={handleChange}>
              {[1,2,3,4,5].map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label>Теги (через запятую)</label>
            <input
              type="text"
              name="tags"
              placeholder="feature,bug,enhancement"
              value={form.tags}
              onChange={handleTagChange}
            />
          </div>

          <div className="form-row">
            <label>Тип задачи</label>
            <select name="type" value={form.type} onChange={handleChange}>
              <option value={TaskType.PUBLIC}>Публичная</option>
              <option value={TaskType.PRIVATE}>Приватная</option>
            </select>
          </div>

          <div className="form-row">
            <label>Исполнитель</label>
            <input
              type="text"
              name="assignedTo"
              placeholder="Имя пользователя"
              value={form.assignedTo}
              onChange={handleChange}
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="submit-btn">Создать задачу</button>
            <button 
              type="button" 
              className="cancel-btn"
              onClick={() => {
                setAddingTask(false);
                setErrors({});
                setForm({ 
                  title: '',
                  description: '',
                  deadline: '',
                  budget: '',
                  priority: 3,
                  tags: '',
                  type: TaskType.PUBLIC,
                  assignedTo: ''
                });
              }}
            >
              Отмена
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

Column.propTypes = {
  title: PropTypes.string.isRequired,
  tasks: PropTypes.arrayOf(PropTypes.object).isRequired,
  columnId: PropTypes.string.isRequired,
  onMoveTask: PropTypes.func.isRequired,
  onAddTask: PropTypes.func.isRequired,
};

export default Column;