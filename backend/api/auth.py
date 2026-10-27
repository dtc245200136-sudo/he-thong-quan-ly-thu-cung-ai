from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import verify_password, get_password_hash, create_access_token, get_current_user, require_roles
from backend.core.config import settings
from backend.models.user import User, UserRole
from backend.schemas.auth_dto import Token, LoginRequest, RegisterRequest, ResetPasswordRequest, UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/auth", tags=["Xác thực & Phân quyền (Auth & RBAC)"])

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username.strip()).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản này đã bị tạm khóa"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "id": user.id},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register")
def register(reg_data: RegisterRequest, db: Session = Depends(get_db)):
    username = reg_data.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên đăng nhập.")
    if len(reg_data.password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 6 ký tự.")
    
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Tên đăng nhập '{username}' đã được sử dụng. Vui lòng chọn tên khác.")
    
    # Check email duplicate if provided
    if reg_data.email and reg_data.email.strip():
        email_existing = db.query(User).filter(User.email == reg_data.email.strip()).first()
        if email_existing:
            raise HTTPException(status_code=400, detail=f"Email '{reg_data.email}' đã được đăng ký tài khoản.")

    # Validate role (Cho phép CUSTOMER, STAFF, RECEPTIONIST. Mặc định là CUSTOMER nếu đăng ký công khai)
    allowed_roles = [UserRole.CUSTOMER.value, UserRole.STAFF.value, UserRole.RECEPTIONIST.value]
    role = reg_data.role if reg_data.role in allowed_roles else UserRole.CUSTOMER.value

    new_user = User(
        username=username,
        hashed_password=get_password_hash(reg_data.password),
        full_name=reg_data.full_name.strip() if reg_data.full_name else username,
        role=role,
        phone=reg_data.phone.strip() if reg_data.phone else None,
        email=reg_data.email.strip() if reg_data.email else None,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Nếu là Khách Hàng (CUSTOMER) và có SĐT, kiểm tra/tạo PetOwner để đồng bộ hồ sơ
    if role == UserRole.CUSTOMER.value and new_user.phone:
        from backend.models.owner import PetOwner
        existing_owner = db.query(PetOwner).filter(PetOwner.phone == new_user.phone).first()
        if not existing_owner:
            new_owner = PetOwner(
                full_name=new_user.full_name,
                phone=new_user.phone,
                email=new_user.email,
                address="Đăng ký tài khoản Khách Hàng",
                notes="Khách hàng tạo tài khoản trực tuyến"
            )
            db.add(new_owner)
            db.commit()

    # Automatically issue token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username, "role": new_user.role, "id": new_user.id},
        expires_delta=access_token_expires
    )

    role_vn = "Khách Hàng"
    if role == UserRole.STAFF.value: role_vn = "Kỹ thuật viên"
    if role == UserRole.RECEPTIONIST.value: role_vn = "Lễ tân"

    return {
        "success": True,
        "message": f"🎉 Chào mừng {new_user.full_name}! Bạn đã đăng ký tài khoản {role_vn} thành công!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "phone": new_user.phone,
            "email": new_user.email,
            "is_active": new_user.is_active
        }
    }

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    username = data.username.strip()
    user = db.query(User).filter(User.username == username).first()
    
    # If not found by username, try finding by phone or email
    if not user and data.verify_info:
        v_info = data.verify_info.strip()
        user = db.query(User).filter((User.phone == v_info) | (User.email == v_info)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản tương ứng với thông tin đã nhập.")

    # If verify_info provided, check if it matches either email or phone
    if data.verify_info and data.verify_info.strip():
        v_info = data.verify_info.strip()
        if (user.phone != v_info) and (user.email != v_info):
            raise HTTPException(status_code=400, detail="Thông tin xác minh (SĐT hoặc Email) không trùng khớp với hồ sơ tài khoản.")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 6 ký tự.")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    return {
        "success": True,
        "message": f"✅ Đặt lại mật khẩu thành công cho tài khoản '{user.username}'! Vui lòng đăng nhập bằng mật khẩu mới."
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "RECEPTIONIST"]))
):
    return db.query(User).order_by(User.id.desc()).all()

@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    """Admin cấp tài khoản mới cho Khách Hàng, Lễ Tân, Kỹ Thuật Viên hoặc Admin"""
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Tên đăng nhập '{user_data.username}' đã tồn tại")
    
    new_user = User(
        username=user_data.username.strip(),
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name.strip(),
        role=user_data.role,
        phone=user_data.phone.strip() if user_data.phone else None,
        email=user_data.email.strip() if user_data.email else None,
        is_active=user_data.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Đồng bộ PetOwner nếu cấp tài khoản Khách Hàng
    if new_user.role == UserRole.CUSTOMER.value and new_user.phone:
        from backend.models.owner import PetOwner
        existing_owner = db.query(PetOwner).filter(PetOwner.phone == new_user.phone).first()
        if not existing_owner:
            new_owner = PetOwner(
                full_name=new_user.full_name,
                phone=new_user.phone,
                email=new_user.email,
                address="Được cấp tài khoản bởi Quản Trị Viên",
                notes="Tài khoản Khách Hàng được Admin cấp"
            )
            db.add(new_owner)
            db.commit()

    return new_user

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    """Admin đổi vai trò / cấp quyền cho tài khoản"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản người dùng.")
    
    new_role = role_data.get("role")
    if new_role not in [UserRole.ADMIN.value, UserRole.RECEPTIONIST.value, UserRole.STAFF.value, UserRole.CUSTOMER.value]:
        raise HTTPException(status_code=400, detail="Vai trò không hợp lệ.")
    
    user.role = new_role
    db.commit()
    return {"success": True, "message": f"Đã cấp quyền '{new_role}' cho tài khoản {user.username}"}

@router.put("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    """Admin kích hoạt hoặc khóa tài khoản"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản của chính mình.")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    
    user.is_active = not user.is_active
    db.commit()
    status_str = "Kích hoạt" if user.is_active else "Tạm khóa"
    return {"success": True, "message": f"Đã {status_str} tài khoản {user.username}", "is_active": user.is_active}
