from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ArticleCreate(BaseModel):
    title:str
    content:str
    author_id:int
class ArticleResponse(BaseModel):
    id:int
    title:str
    content:str
    author_id:int
    created_at:datetime

    model_config=ConfigDict(from_attributes=True)