import uuid
from typing import Optional

from fastapi import Header


async def get_session_id(x_session_id: Optional[str] = Header(None)) -> Optional[uuid.UUID]:
    if x_session_id:
        try:
            return uuid.UUID(x_session_id)
        except ValueError:
            pass
    return None
