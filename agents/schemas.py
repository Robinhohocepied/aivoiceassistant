from typing import Optional

from pydantic import BaseModel


class Extraction(BaseModel):
    name: Optional[str] = None
    reason: Optional[str] = None
    preferred_time: Optional[str] = None

