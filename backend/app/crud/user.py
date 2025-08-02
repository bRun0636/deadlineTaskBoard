from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional

class UserCRUD:
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user: UserCreate) -> User:
        hashed_password = User.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = User.get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def delete(self, db: Session, user_id: int) -> bool:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username)
        if not user:
            return None
        if not User.verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_superusers(self, db: Session):
        return db.query(User).filter(User.is_superuser == True).all()
    
    def get_customers(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).filter(User.role == UserRole.CUSTOMER).offset(skip).limit(limit).all()
    
    def get_executors(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).filter(User.role == UserRole.EXECUTOR).offset(skip).limit(limit).all()
    
    def update_admin(self, db: Session, user_id: int, user_update: dict) -> Optional[User]:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        for field, value in user_update.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user

user_crud = UserCRUD() 