from dataclasses import dataclass
from datetime import datetime

@dataclass
class Comment:
    id:int | None
    content:str
    article_id:int
    user_id:int
    user_name:str
    created_at:datetime | None = None
    