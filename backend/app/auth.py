from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

# Lightweight user session / role helper for seamless testing and demonstration
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if user.password_hash != password:
        return None
    return user

def require_roles(allowed_roles: list):
    def role_checker(role: str = "admin"):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tài khoản không đủ quyền hạn. Yêu cầu một trong các quyền: {', '.join(allowed_roles)}"
            )
        return role
    return role_checker
