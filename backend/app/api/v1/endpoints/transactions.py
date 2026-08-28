from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.services.transaction_service import TransactionService
from backend.app.schemas.schemas import TransactionCreate

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("")
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    failure_code: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
):
    """List transactions with multi-filtering and pagination."""
    items, total = await TransactionService.get_transactions(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        payment_method=payment_method,
        failure_code=failure_code,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch complete transaction context, risk assessment, and recovery case history."""
    return await TransactionService.get_transaction_by_id(db, transaction_id)


@router.post("")
async def create_transaction(data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    """Ingest a new transaction."""
    tx = await TransactionService.create_transaction(db, data)
    return {"status": "SUCCESS", "id": tx.id}
