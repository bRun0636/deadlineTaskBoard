-- Инициализация базы данных для Deadline Task Board

-- Создание enum типов (если не существуют)
DO $$ BEGIN
    CREATE TYPE userrole AS ENUM ('customer', 'executor', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE juridicaltype AS ENUM ('individual', 'llc', 'ip');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE paymenttype AS ENUM ('card', 'cash', 'bank_transfer', 'crypto');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notificationtype AS ENUM ('new_tasks', 'task_updates', 'messages', 'payments', 'system');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE taskstatus AS ENUM ('todo', 'in_progress', 'done', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE tasktype AS ENUM ('bug', 'feature', 'improvement', 'task');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE orderstatus AS ENUM ('open', 'in_progress', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE orderpriority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE proposalstatus AS ENUM ('pending', 'accepted', 'rejected', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    
    -- Основная информация
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    phone VARCHAR(20),
    country VARCHAR(50),
    
    -- Telegram информация
    telegram_id INTEGER UNIQUE,
    telegram_username VARCHAR(50),
    
    -- Профессиональная информация
    juridical_type juridicaltype,
    payment_types TEXT,  -- JSON string
    prof_level VARCHAR(20),  -- junior, middle, senior, expert
    skills TEXT,  -- JSON string
    bio TEXT,
    resume_url VARCHAR(255),
    profile_photo_url VARCHAR(255),
    
    -- Настройки
    notification_types TEXT,  -- JSON string
    rating FLOAT DEFAULT 0.0,
    completed_tasks INTEGER DEFAULT 0,
    total_earnings FLOAT DEFAULT 0.0,
    
    -- Статусы
    is_active BOOLEAN DEFAULT TRUE,
    is_registered BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_banned BOOLEAN DEFAULT FALSE,
    
    -- Роль
    role userrole DEFAULT 'executor',
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE
);

-- Создание индексов для таблицы users
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

-- Создание таблицы досок
CREATE TABLE IF NOT EXISTS boards (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    creator_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Создание таблицы участников досок
CREATE TABLE IF NOT EXISTS board_members (
    id SERIAL PRIMARY KEY,
    board_id INTEGER REFERENCES boards(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',  -- owner, admin, member
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(board_id, user_id)
);

-- Создание таблицы колонок
CREATE TABLE IF NOT EXISTS columns (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    order_index INTEGER NOT NULL,
    board_id INTEGER REFERENCES boards(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Создание таблицы задач
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status taskstatus DEFAULT 'todo',
    type tasktype DEFAULT 'task',
    priority INTEGER DEFAULT 1,
    budget FLOAT,
    due_date TIMESTAMP WITH TIME ZONE,
    tags VARCHAR,
    column_id INTEGER REFERENCES columns(id) ON DELETE CASCADE,
    board_id INTEGER REFERENCES boards(id) ON DELETE CASCADE,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assignee_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    parent_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Создание таблицы заказов
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    budget FLOAT NOT NULL,
    deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    priority orderpriority DEFAULT 'MEDIUM',
    status orderstatus DEFAULT 'open',
    tags VARCHAR,
    creator_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    assigned_executor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Создание таблицы предложений
CREATE TABLE IF NOT EXISTS proposals (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    price FLOAT NOT NULL,
    description TEXT NOT NULL,
    status proposalstatus DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    estimated_duration INTEGER
);

-- Создание таблицы сообщений
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    receiver_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Добавление внешнего ключа для sender_id с именем как в текущей БД
ALTER TABLE messages
    ADD CONSTRAINT messages_user_id_fkey 
    FOREIGN KEY (sender_id) 
    REFERENCES users(id) ON DELETE CASCADE;

-- Создание таблицы рейтингов
CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    to_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(from_user_id, to_user_id, order_id)
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS ix_boards_creator_id ON boards(creator_id);
CREATE INDEX IF NOT EXISTS ix_board_members_board_id ON board_members(board_id);
CREATE INDEX IF NOT EXISTS ix_board_members_user_id ON board_members(user_id);
CREATE INDEX IF NOT EXISTS ix_columns_board_id ON columns(board_id);
CREATE INDEX IF NOT EXISTS ix_tasks_column_id ON tasks(column_id);
CREATE INDEX IF NOT EXISTS ix_tasks_board_id ON tasks(board_id);
CREATE INDEX IF NOT EXISTS ix_tasks_creator_id ON tasks(creator_id);
CREATE INDEX IF NOT EXISTS ix_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS ix_orders_creator_id ON orders(creator_id);
CREATE INDEX IF NOT EXISTS ix_orders_assigned_executor_id ON orders(assigned_executor_id);
CREATE INDEX IF NOT EXISTS ix_proposals_order_id ON proposals(order_id);
CREATE INDEX IF NOT EXISTS ix_proposals_user_id ON proposals(user_id);
CREATE INDEX IF NOT EXISTS ix_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS ix_messages_receiver_id ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS ix_messages_order_id ON messages(order_id);
CREATE INDEX IF NOT EXISTS ix_ratings_from_user_id ON ratings(from_user_id);
CREATE INDEX IF NOT EXISTS ix_ratings_to_user_id ON ratings(to_user_id);
CREATE INDEX IF NOT EXISTS ix_ratings_order_id ON ratings(order_id); 