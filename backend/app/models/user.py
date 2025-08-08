from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from passlib.context import CryptContext
import enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(enum.Enum):
    CUSTOMER = "customer"  # Заказчик
    EXECUTOR = "executor"  # Исполнитель
    ADMIN = "admin"        # Администратор

class JuridicalType(enum.Enum):
    INDIVIDUAL = "individual"  # Физическое лицо
    LLC = "llc"               # ООО
    IP = "ip"                 # ИП

class PaymentType(enum.Enum):
    CARD = "card"              # Банковская карта
    CASH = "cash"              # Наличные
    BANK_TRANSFER = "bank_transfer"  # Банковский перевод
    CRYPTO = "crypto"          # Криптовалюта

class NotificationType(enum.Enum):
    EMAIL = "email"            # Email уведомления
    SMS = "sms"                # SMS уведомления
    TELEGRAM = "telegram"      # Telegram уведомления
    PUSH = "push"              # Push уведомления

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Основная информация
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    
    # Telegram информация
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    telegram_username = Column(String(50), nullable=True)
    
    # Профессиональная информация
    juridical_type = Column(String(20), nullable=True)
    payment_types = Column(String, nullable=True)  # JSON string
    prof_level = Column(String(20), nullable=True)  # junior, middle, senior, expert
    skills = Column(String, nullable=True)  # JSON string
    bio = Column(String, nullable=True)
    resume_url = Column(String(255), nullable=True)
    profile_photo_url = Column(String(255), nullable=True)
    
    # Настройки
    notification_types = Column(String, nullable=True)  # JSON string
    rating = Column(Float, default=0.0, nullable=True)
    completed_tasks = Column(Integer, default=0, nullable=True)
    total_earnings = Column(Float, default=0.0, nullable=True)
    
    # Статусы
    is_active = Column(Boolean, default=True)
    is_registered = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    
    # Роль
    role = Column(String(20), default=UserRole.EXECUTOR.value)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    boards = relationship("Board", foreign_keys="Board.creator_id", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assigned_to")
    created_tasks = relationship("Task", foreign_keys="Task.creator_id", back_populates="created_by")
    # Новые связи для заказов и предложений
    created_orders = relationship("Order", foreign_keys="Order.creator_id", back_populates="creator")
    proposals = relationship("Proposal", foreign_keys="Proposal.user_id", back_populates="executor")
    # Связи для сообщений (добавляются после загрузки всех моделей)
    # sent_messages = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    # received_messages = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    def set_payment_types_list(self, payment_types_list):
        """Устанавливает список типов оплаты как JSON строку"""
        import json
        if payment_types_list:
            self.payment_types = json.dumps(payment_types_list)
        else:
            self.payment_types = None
    
    def get_payment_types_list(self):
        """Получает список типов оплаты из JSON строки"""
        import json
        if self.payment_types:
            try:
                return json.loads(self.payment_types)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_notification_types_list(self, notification_types_list):
        """Устанавливает список типов уведомлений как JSON строку"""
        import json
        if notification_types_list:
            self.notification_types = json.dumps(notification_types_list)
        else:
            self.notification_types = None
    
    def get_notification_types_list(self):
        """Получает список типов уведомлений из JSON строки"""
        import json
        if self.notification_types:
            try:
                return json.loads(self.notification_types)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_skills_list(self, skills_list):
        """Устанавливает список навыков как JSON строку"""
        import json
        if skills_list:
            self.skills = json.dumps(skills_list)
        else:
            self.skills = None
    
    def get_skills_list(self):
        """Получает список навыков из JSON строки"""
        import json
        if self.skills:
            try:
                return json.loads(self.skills)
            except json.JSONDecodeError:
                return []
        return [] 