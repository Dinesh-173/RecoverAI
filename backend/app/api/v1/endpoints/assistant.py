from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.logging import logger
from backend.app.core.security import require_role
from backend.app.schemas.schemas import AssistantChatRequest, AssistantChatResponse
from backend.app.services.assistant_service import IntelligenceAssistantService

router = APIRouter(prefix="/assistant", tags=["Intelligence Assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
async def assistant_chat(
    request: AssistantChatRequest,
    db: AsyncSession = Depends(get_db),
    user_role: str = Depends(require_role(["VIEWER", "MERCHANT_OPERATOR", "MERCHANT_ADMIN", "ADMIN"])),
    x_merchant_id: str = Header("merch_default", alias="X-Merchant-ID"),
):
    """
    POST /api/v1/assistant/chat
    Context-aware, tool-governed RecoverAI Intelligence Assistant.

    Provides read-only, evidence-based responses for dashboard metrics, ML recoverability scores,
    Policy Engine rules, recovery cases, and simulation workflows.
    Enforces strict FinTech safety rules prohibiting autonomous financial payment execution.
    """
    try:
        response = await IntelligenceAssistantService.process_chat(
            db=db,
            request=request,
            merchant_id=x_merchant_id,
            user_role=user_role,
        )
        return response
    except Exception as e:
        logger.error(f"Assistant API error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your query. Please try again."
        )
