from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    content:str
    article_id:int
    user_id:int
class CommentResponse(BaseModel):
    id:int
    content:str
    article_id:int
    user_id:int
    created_at:datetime
    username:Optional[str]=None

    model_config=ConfigDict(from_attributes=True)