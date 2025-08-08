import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { Plus, Search } from "lucide-react";
import { boardsAPI } from "../../services/api";
import BoardCard from "../../components/Board/BoardCard";
import CreateBoardModal from "../../components/Board/CreateBoardModal";
import toast from "react-hot-toast";

const BoardsPage = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("all"); // all, public, private

  const queryClient = useQueryClient();

  const {
    data: boards = [],
    isLoading,
    error,
    refetch,
  } = useQuery(
    "boards",
    async () => {
      const result = await boardsAPI.getAll();
      return result;
    },
    {
      onError: (error) => {
        toast.error("Ошибка при загрузке досок");
      },
    }
  );

  // Мутация для удаления доски
  const deleteBoardMutation = useMutation(
    (boardId) => boardsAPI.delete(boardId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries("boards");
        toast.success("Доска удалена");
      },
      onError: (error) => {
        // Если доска не найдена (404), возможно пользователь находится на странице доски
        if (error.response?.status === 404) {
          toast.error("Доска уже была удалена");
        } else {
          toast.error("Ошибка при удалении доски");
        }
      },
    }
  );

  // Убеждаемся, что boards - это массив
  const boardsArray = Array.isArray(boards) ? boards : [];

  const filteredBoards = boardsArray.filter((board) => {
    const matchesSearch =
      board.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      board.description?.toLowerCase().includes(searchTerm.toLowerCase());

    if (filter === "public") return matchesSearch && board.is_public;
    if (filter === "private") return matchesSearch && !board.is_public;
    return matchesSearch;
  });

  const handleDeleteBoard = (boardId) => {
    if (window.confirm("Вы уверены, что хотите удалить эту доску? Все задачи и колонки будут также удалены.")) {
      deleteBoardMutation.mutate(boardId);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
            Ошибка загрузки
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Не удалось загрузить доски
          </p>
          <button onClick={() => refetch()} className="btn btn-primary">
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              Мои доски
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Управляйте своими досками и задачами
            </p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="h-5 w-5" />
            Создать доску
          </button>
        </div>

        {/* Поиск и фильтры */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по названию или описанию..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10 w-full"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="input"
            >
              <option value="all">Все доски</option>
              <option value="public">Публичные</option>
              <option value="private">Приватные</option>
            </select>
          </div>
        </div>
      </div>

      {/* Список досок */}
      {filteredBoards.length === 0 ? (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-4">
              <Plus className="h-12 w-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {searchTerm || filter !== "all"
                ? "Доски не найдены"
                : "У вас пока нет досок"}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {searchTerm || filter !== "all"
                ? "Попробуйте изменить поисковый запрос или фильтры"
                : "Создайте свою первую доску для управления задачами"}
            </p>
            {!searchTerm && filter === "all" && (
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="btn btn-primary"
              >
                Создать первую доску
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredBoards.map((board) => (
            <BoardCard 
              key={board.id} 
              board={board} 
              onDelete={handleDeleteBoard}
            />
          ))}
        </div>
      )}

      {/* Модальное окно создания доски */}
      <CreateBoardModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};

export default BoardsPage;
