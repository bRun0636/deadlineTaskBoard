# Импортируем все схемы
from .user import UserResponse, UserCreate, UserUpdate, UserRole
from .order import OrderResponse, OrderCreate, OrderUpdate, OrderStatus, OrderPriority, OrderWithCustomer, OrderWithProposals
from .proposal import ProposalResponse, ProposalCreate, ProposalUpdate, ProposalStatus, ProposalWithExecutor, ProposalWithOrder

__all__ = [
    "UserResponse", "UserCreate", "UserUpdate", "UserRole",
    "OrderResponse", "OrderCreate", "OrderUpdate", "OrderStatus", "OrderPriority",
    "OrderWithCustomer", "OrderWithProposals",
    "ProposalResponse", "ProposalCreate", "ProposalUpdate", "ProposalStatus",
    "ProposalWithExecutor", "ProposalWithOrder"
] 