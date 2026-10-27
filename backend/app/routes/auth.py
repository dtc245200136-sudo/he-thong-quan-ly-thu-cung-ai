from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User
from ..schemas import UserLogin, UserRegister, UserResponse, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(reg_data: UserRegister, db: Session = Depends(get_db)):
    # 1. Check existing username
    existing_user = db.query(User).filter(User.username == reg_data.username.strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập này đã được sử dụng! Vui lòng chọn tên khác."
        )

    # 2. Check existing email if provided
    if reg_data.email:
        existing_email = db.query(User).filter(User.email == reg_data.email.strip()).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Địa chỉ Email này đã được đăng ký!"
            )

    # 3. Create new user
    new_user = User(
        username=reg_data.username.strip(),
        full_name=reg_data.full_name.strip(),
        email=reg_data.email.strip() if reg_data.email else None,
        role=reg_data.role if reg_data.role in ["admin", "receptionist", "staff"] else "receptionist",
        password_hash=reg_data.password,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_str = f"petcare-token-{new_user.username}-{new_user.role}"
    return TokenResponse(
        access_token=token_str,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username.strip()).first()
    if not user or user.password_hash != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác!"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị tạm khóa!"
        )

    token_str = f"petcare-token-{user.username}-{user.role}"
    return TokenResponse(
        access_token=token_str,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    """Return current user info from Bearer token.
    Token format: petcare-token-<username>-<role>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không có token xác thực. Vui lòng đăng nhập lại!"
        )
    token = authorization.removeprefix("Bearer ").strip()
    # Parse token: petcare-token-<username>-<role>
    parts = token.split("-")
    # Format: petcare-token-<username>-<role> => parts[0]="petcare", [1]="token", [2]=username, [3]=role
    if len(parts) < 4 or parts[0] != "petcare" or parts[1] != "token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ!"
        )
    # username may contain hyphens itself, so join parts[2:-1] for username, last part for role
    role = parts[-1]
    username = "-".join(parts[2:-1])

    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khóa!"
        )
    return UserResponse.model_validate(user)


@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).filter(User.is_active == True).all()
