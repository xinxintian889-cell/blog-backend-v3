from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id:int | None
    username:str
    password_hash:str

    def verify_password(self,raw_password:str,hasher)->bool:
        #纯业务逻辑：把我的输入和数据库里的哈希对比
        # 注意：具体的hasher也是外部传进来的（依赖注入）
        return hasher.verify(raw_password,self.password_hash)    