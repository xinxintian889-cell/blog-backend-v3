#密码加密实现
from passlib.context import CryptContext

#具体使用什么算法加密，是底层基础设施的事
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

class PasswordHasher:
    #明文->乱码hash值（注册或该密码时候调用）
    def hash(self,password:str)->str:
        return pwd_context.hash(password)
    #明文和hash值比对（登录时候调用）
    def verify(self,plain_password:str,hashed_password:str)->bool:
        return pwd_context.verify(plain_password,hashed_password)