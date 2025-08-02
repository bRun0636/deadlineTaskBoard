import React from 'react';
import { useQuery } from 'react-query';
import { boardsAPI } from '../../services/api';
import BoardCard from '../../components/Board/BoardCard';
import { AlertCircle } from 'lucide-react';

const PublicBoardsPage = () => {
  const { data: boards, isLoading } = useQuery('publicBoards', () => boardsAPI.getPublic(), {
    refetchOnWindowFocus: false,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">Публичные доски</h1>
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
        </div>
      ) : boards?.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {boards.map((board) => (
            <BoardCard key={board.id} board={board} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
            Нет публичных досок
          </h3>
        </div>
      )}
    </div>
  );
};

export default PublicBoardsPage; 