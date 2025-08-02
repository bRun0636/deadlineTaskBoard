import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, Eye, EyeOff, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

const BoardCard = ({ board, onDelete }) => {
  return (
    <div className="card p-6 hover:shadow-md transition-shadow duration-200 relative group">
      <Link to={`/board/${board.id}`} className="block">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {board.title}
            </h3>
            
            {board.description && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                {board.description}
              </p>
            )}
            
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                <span>
                  {format(new Date(board.created_at), 'dd MMM yyyy', { locale: ru })}
                </span>
              </div>
              
              <div className="flex items-center gap-1">
                {board.is_public ? (
                  <Eye className="h-4 w-4" />
                ) : (
                  <EyeOff className="h-4 w-4" />
                )}
                <span>{board.is_public ? 'Публичная' : 'Приватная'}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
            <Users className="h-4 w-4" />
            <span>1</span>
          </div>
        </div>
      </Link>
      
      {onDelete && (
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onDelete(board.id);
          }}
          className="absolute top-2 right-2 p-2 text-gray-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
          title="Удалить доску"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      )}
    </div>
  );
};

export default BoardCard; 