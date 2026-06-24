from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import MemoryActionResponse, MemoryClearRequest
from app.services.memory_service import clear_memories, delete_memory, disable_memory, list_memories

router = APIRouter()


@router.get("/memory")
def get_memories(
    session_id: str = Query(...), skill_id: Optional[str] = None, include_disabled: bool = False
):
    return {
        "session_id": session_id,
        "skill_id": skill_id,
        "memories": list_memories(session_id, skill_id, include_disabled),
    }


@router.delete("/memory/{memory_id}", response_model=MemoryActionResponse)
def remove_memory(memory_id: str):
    if not delete_memory(memory_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return MemoryActionResponse(affected_count=1)


@router.post("/memory/{memory_id}/disable", response_model=MemoryActionResponse)
def mark_memory_disabled(memory_id: str):
    if not disable_memory(memory_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return MemoryActionResponse(affected_count=1)


@router.post("/memory/clear", response_model=MemoryActionResponse)
def clear_memory_scope(request: MemoryClearRequest):
    return MemoryActionResponse(affected_count=clear_memories(request.session_id, request.skill_id))
