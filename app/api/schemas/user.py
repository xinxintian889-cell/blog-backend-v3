from pydantic import BaseModel, ConfigDict
from datetime import datetime

#BaseModel主要什么作用
class UserRegister(BaseModel):
    username:str
    password:str
class UserResponse(BaseModel):
    id:int
    username:str
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)    #允许从SQLAlchemy对象转换
class UserLogin(BaseModel):
    username:str
    password:str