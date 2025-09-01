from pydantic import BaseModel
from typing import List

class MatrixResponse(BaseModel):
    distances: List[List[int]]  # meters
    durations: List[List[int]]  # seconds
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "distances": [[0, 1200], [1180, 0]],
                "durations": [[0, 300], [290, 0]],
                "count": 2
            }
        }
