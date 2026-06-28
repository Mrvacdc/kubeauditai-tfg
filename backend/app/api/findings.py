from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter(prefix="/findings", tags=["Findings"])


@router.get("/{finding_id}", response_model=MessageResponse)
def get_finding_placeholder(finding_id: int):
    return MessageResponse(message=f"Finding detail placeholder for finding_id={finding_id}.")
