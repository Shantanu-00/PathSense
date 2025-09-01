from pydantic import BaseModel
from typing import Optional

class Intent(BaseModel):
    business_type: Optional[str] = None
    location: Optional[str] = None
    action: Optional[str] = None
