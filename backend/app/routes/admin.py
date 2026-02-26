from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, require_admin, verify_password
from app.database import get_db
from app.models import Transaction, User, Wallet
from app.schemas import (
    AdminDepositRequest,
    FreezeUserRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    TokenResponse,
    TransactionResponse,
    UserListResponse,
    UserStatusRequest,
)
from app.utils.email import send_admin_deposit_email, send_freeze_email, send_unfreeze_email
from app.utils.logger import log_transaction_event
from app.utils.redis_cache import cache_delete, cache_set_json


router = APIRouter(prefix="/admin", tags=["admin"])


def validate_amount_gt_zero(amount: Decimal):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def admin_register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.flush()

    wallet = Wallet(user_id=user.id, balance=Decimal("0.00"))
    db.add(wallet)
    db.commit()

    return {"message": "Admin registered successfully"}


@router.post("/login", response_model=TokenResponse)
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not user.is_active or not user.is_admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/deposit", response_model=MessageResponse)
def admin_deposit(
    payload: AdminDepositRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    target_user = None
    target_wallet = None

    try:
        validate_amount_gt_zero(payload.amount)
        if admin_user.is_frozen:
            raise HTTPException(status_code=403, detail="Account is frozen")

        target_user = db.query(User).filter(User.email == payload.email).first()
        if target_user is None or not target_user.is_active:
            raise HTTPException(status_code=404, detail="User not found")
        if target_user.is_frozen:
            raise HTTPException(status_code=403, detail="Account is frozen")

        target_wallet = db.query(Wallet).filter(Wallet.user_id == target_user.id).first()
        if target_wallet is None:
            raise HTTPException(status_code=404, detail="Wallet not found")

        db.rollback()
        with db.begin():
            target_wallet.balance = Decimal(target_wallet.balance) + payload.amount
            tx = Transaction(wallet_id=target_wallet.id, type="deposit", amount=payload.amount, status="SUCCESS")
            db.add(tx)

        cache_set_json(f"wallet_balance:{target_user.id}", str(target_wallet.balance), 60)
        cache_delete(f"wallet_transactions:{target_user.id}")

        background_tasks.add_task(
            send_admin_deposit_email,
            target_user.email,
            str(payload.amount),
        )
        background_tasks.add_task(
            log_transaction_event,
            f"Admin deposit SUCCESS admin_id={admin_user.id} user_id={target_user.id} amount={payload.amount}",
        )

        return {"message": "Deposit successful"}
    except Exception:
        db.rollback()
        if target_wallet is not None:
            try:
                db.add(Transaction(wallet_id=target_wallet.id, type="deposit", amount=payload.amount, status="FAILED"))
                db.commit()
                cache_delete(f"wallet_transactions:{target_user.id}")
            except Exception:
                db.rollback()

        background_tasks.add_task(
            log_transaction_event,
            f"Admin deposit FAILED admin_id={admin_user.id} email={payload.email} amount={payload.amount}",
        )
        raise


@router.post("/deactivate-user", response_model=MessageResponse)
def deactivate_user(
    payload: UserStatusRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Admin cannot deactivate themselves")

    user.is_active = False
    db.commit()
    return {"message": "User deactivated"}


@router.post("/activate-user", response_model=MessageResponse)
def activate_user(
    payload: UserStatusRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()
    return {"message": "User activated"}


@router.get("/users", response_model=list[UserListResponse])
def list_users(admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    return users


@router.post("/freeze-user", response_model=MessageResponse)
def freeze_user(
    payload: FreezeUserRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Admin cannot freeze themselves")

    user.is_frozen = True
    db.commit()
    background_tasks.add_task(send_freeze_email, user.email)
    return {"message": "User frozen"}


@router.post("/unfreeze-user", response_model=MessageResponse)
def unfreeze_user(
    payload: FreezeUserRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_frozen = False
    db.commit()
    background_tasks.add_task(send_unfreeze_email, user.email)
    return {"message": "User unfrozen"}


@router.get("/user-transactions", response_model=list[TransactionResponse])
def user_transactions(email: str, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    rows = db.query(Transaction).filter(Transaction.wallet_id == wallet.id).order_by(Transaction.timestamp.desc()).all()
    return rows
