from dataclasses import dataclass
from datetime import datetime

@dataclass
class Article:
    id:int | None
    title:str
    content:str
    author_id:int
    author_name:str = ""
    created_at:datetime | None = None
    