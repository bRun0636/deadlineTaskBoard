import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Layout from './components/Layout/Layout';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import BoardPage from './pages/Board/BoardPage';
import BoardsPage from './pages/Board/BoardsPage';
import ProfilePage from './pages/Profile/ProfilePage';
import NotFoundPage from './pages/NotFound/NotFoundPage';
import PublicBoardsPage from './pages/Board/PublicBoardsPage';
import UserProfilePage from './pages/Profile/UserProfilePage';
import AdminPage from './pages/Admin/AdminPage';
import OrdersPage from './pages/Orders/OrdersPage';
import ChatPage from './pages/Chat/ChatPage';
import ChatsListPage from './pages/Chat/ChatsListPage';
import 'react-toastify/dist/ReactToastify.css';
import { ToastContainer } from 'react-toastify';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <>
      <Routes>
        {/* Публичные маршруты */}
        <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/dashboard" />} />
        <Route path="/register" element={!user ? <RegisterPage /> : <Navigate to="/dashboard" />} />
        
        {/* Защищенные маршруты */}
        <Route path="/" element={user ? <Layout /> : <Navigate to="/login" />}>
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="boards" element={<BoardsPage />} />
          <Route path="board/:boardId" element={<BoardPage />} />
          <Route path="orders" element={<OrdersPage />} />
          <Route path="chats" element={<ChatsListPage />} />
          <Route path="chat/:orderId" element={<ChatPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="public-boards" element={<PublicBoardsPage />} />
          <Route path="user/:userId" element={<UserProfilePage />} />
          <Route path="admin" element={<AdminPage />} />
        </Route>
        
        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </>
  );
}

export default App;
