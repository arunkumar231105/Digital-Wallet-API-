from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.auth import get_current_user
from app.database import get_db
from app.models import Transaction, User, Wallet
from app.schemas import (
    AmountRequest,
    BalanceResponse,
    TransactionResponse,
    TransferRequest,
    WalletResponse,
)
from app.utils.email import send_transfer_email
from app.utils.logger import log_transaction_event
from app.utils.redis_cache import cache_delete, cache_get_json, cache_set_json


router = APIRouter(prefix="/wallet", tags=["wallet"])

def validate_amount_gt_zero(amount: Decimal):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")


def get_user_wallet(db: Session, user_id: int) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


def get_day_window():
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


def get_daily_total(db: Session, wallet_id: int, tx_type: str) -> Decimal:
    start, end = get_day_window()
    total = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.wallet_id == wallet_id,
            Transaction.type == tx_type,
            Transaction.timestamp >= start,
            Transaction.timestamp < end,
            Transaction.status == "SUCCESS",
        )
        .scalar()
    )
    return Decimal(total)


@router.post("/create", response_model=WalletResponse)
def create_wallet(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    balance_key = f"wallet_balance:{current_user.id}"

    if wallet:
        cached_balance = cache_get_json(balance_key)
        if cached_balance is not None:
            return {
                "id": wallet.id,
                "user_id": wallet.user_id,
                "balance": Decimal(str(cached_balance)),
            }

        cache_set_json(balance_key, str(wallet.balance), 60)
        return wallet

    wallet = Wallet(user_id=current_user.id, balance=Decimal("0.00"))
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    cache_set_json(balance_key, str(wallet.balance), 60)
    return wallet


@router.post("/withdraw", response_model=BalanceResponse)
def withdraw(
    payload: AmountRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = None
    try:
        db.rollback()
        with db.begin():
            wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).with_for_update().first()
            if wallet is None:
                raise HTTPException(status_code=404, detail="Wallet not found")

            validate_amount_gt_zero(payload.amount)
            if current_user.is_frozen:
                raise HTTPException(status_code=403, detail="Account is frozen")

            today_withdraw_total = get_daily_total(db, wallet.id, "withdraw")
            if today_withdraw_total + payload.amount > Decimal("100"):
                raise HTTPException(status_code=400, detail="Daily withdraw limit exceeded")

            if Decimal(wallet.balance) < payload.amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")

            wallet.balance = Decimal(wallet.balance) - payload.amount
            db.add(Transaction(wallet_id=wallet.id, type="withdraw", amount=payload.amount, status="SUCCESS"))

        response_data = {"balance": str(wallet.balance)}

        cache_set_json(f"wallet_balance:{current_user.id}", str(wallet.balance), 60)
        cache_delete(f"wallet_transactions:{current_user.id}")

        background_tasks.add_task(
            log_transaction_event,
            f"Withdraw SUCCESS for user_id={current_user.id} amount={payload.amount}",
        )
        return response_data
    except Exception:
        db.rollback()

        if wallet is not None:
            try:
                with db.begin():
                    db.add(Transaction(wallet_id=wallet.id, type="withdraw", amount=payload.amount, status="FAILED"))
                cache_delete(f"wallet_transactions:{current_user.id}")
            except Exception:
                db.rollback()

        background_tasks.add_task(
            log_transaction_event,
            f"Withdraw FAILED for user_id={current_user.id} amount={payload.amount}",
        )
        raise


@router.post("/transfer", response_model=BalanceResponse)
def transfer(
    payload: TransferRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sender_wallet = None
    receiver_user = None
    receiver_wallet = None

    try:
        db.rollback()
        with db.begin():
            validate_amount_gt_zero(payload.amount)
            if current_user.is_frozen:
                raise HTTPException(status_code=403, detail="Account is frozen")

            receiver_user = db.query(User).filter(User.email == payload.email, User.is_active == True).first()
            if receiver_user is None:
                raise HTTPException(status_code=404, detail="Recipient not found")
            if receiver_user.is_frozen:
                raise HTTPException(status_code=403, detail="Account is frozen")
            if receiver_user.id == current_user.id:
                raise HTTPException(status_code=400, detail="Cannot transfer to self")

            locked_wallets = (
                db.query(Wallet)
                .filter(Wallet.user_id.in_([current_user.id, receiver_user.id]))
                .order_by(Wallet.user_id.asc())
                .with_for_update()
                .all()
            )
            wallet_map = {w.user_id: w for w in locked_wallets}
            sender_wallet = wallet_map.get(current_user.id)
            receiver_wallet = wallet_map.get(receiver_user.id)

            if sender_wallet is None:
                raise HTTPException(status_code=404, detail="Wallet not found")
            if receiver_wallet is None:
                raise HTTPException(status_code=404, detail="Recipient wallet not found")

            today_transfer_total = get_daily_total(db, sender_wallet.id, "transfer_out")
            if today_transfer_total + payload.amount > Decimal("100"):
                raise HTTPException(status_code=400, detail="Daily transfer limit exceeded")

            if Decimal(sender_wallet.balance) < payload.amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")

            sender_wallet.balance = Decimal(sender_wallet.balance) - payload.amount
            receiver_wallet.balance = Decimal(receiver_wallet.balance) + payload.amount

            db.add(
                Transaction(
                    wallet_id=sender_wallet.id,
                    sender_id=current_user.id,
                    receiver_id=receiver_user.id,
                    type="transfer_out",
                    amount=payload.amount,
                    status="SUCCESS",
                )
            )
            db.add(
                Transaction(
                    wallet_id=receiver_wallet.id,
                    sender_id=current_user.id,
                    receiver_id=receiver_user.id,
                    type="transfer_in",
                    amount=payload.amount,
                    status="SUCCESS",
                )
            )

        response_data = {"balance": str(sender_wallet.balance)}

        cache_set_json(f"wallet_balance:{current_user.id}", str(sender_wallet.balance), 60)
        cache_set_json(f"wallet_balance:{receiver_user.id}", str(receiver_wallet.balance), 60)
        cache_delete(f"wallet_transactions:{current_user.id}")
        cache_delete(f"wallet_transactions:{receiver_user.id}")

        background_tasks.add_task(
            send_transfer_email,
            receiver_user.email,
            str(payload.amount),
        )
        background_tasks.add_task(
            log_transaction_event,
            f"Transfer SUCCESS for user_id={current_user.id} receiver_id={receiver_user.id} amount={payload.amount}",
        )

        return response_data
    except Exception:
        db.rollback()

        if sender_wallet is not None:
            try:
                with db.begin():
                    db.add(
                        Transaction(
                            wallet_id=sender_wallet.id,
                            sender_id=current_user.id,
                            receiver_id=receiver_user.id if receiver_user else None,
                            type="transfer_out",
                            amount=payload.amount,
                            status="FAILED",
                        )
                    )
                cache_delete(f"wallet_transactions:{current_user.id}")
            except Exception:
                db.rollback()

        background_tasks.add_task(
            log_transaction_event,
            f"Transfer FAILED for user_id={current_user.id} amount={payload.amount}",
        )
        raise


@router.get("/transactions", response_model=list[TransactionResponse])
def transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tx_key = f"wallet_transactions:{current_user.id}"
    cached_transactions = cache_get_json(tx_key)
    if cached_transactions is not None:
        return cached_transactions

    wallet = get_user_wallet(db, current_user.id)

    sender_user = aliased(User)
    receiver_user = aliased(User)

    rows = (
        db.query(Transaction, sender_user.name, receiver_user.name)
        .outerjoin(sender_user, Transaction.sender_id == sender_user.id)
        .outerjoin(receiver_user, Transaction.receiver_id == receiver_user.id)
        .filter(Transaction.wallet_id == wallet.id)
        .order_by(Transaction.timestamp.desc())
        .all()
    )

    response = []
    for tx, sender_name, receiver_name in rows:
        counterparty_name = None
        if tx.type == "transfer_out":
            counterparty_name = receiver_name
        elif tx.type == "transfer_in":
            counterparty_name = sender_name

        response.append(
            {
                "id": tx.id,
                "wallet_id": tx.wallet_id,
                "type": tx.type,
                "amount": str(tx.amount),
                "timestamp": tx.timestamp.isoformat(),
                "counterparty_name": counterparty_name,
            }
        )

    cache_set_json(tx_key, response, 60)
    return response
