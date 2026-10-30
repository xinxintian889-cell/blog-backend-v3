import uuid
import time
from redis.exceptions import WatchError

class RedisLock:
    def __init__(self,redis_client):
        self.redis=redis_client

    def acquire(self,lock_key: str,timeout: int = 5) -> str:
        """获取锁，返回一个唯一标识（用来解锁）"""
        identifier=str(uuid.uuid4())  #防止误解别人的锁
        end=time.time() + timeout
        while time.time() < timeout:
            #核心:NX表示只有当key 不存在的时候才设置成功，ex是过期时间防止死锁
            if self.redis.set(lock_key,identifier,nx=True,ex=timeout):
                return identifier
            time.sleep(0.1) #短暂休眠，避免疯狂重试耗尽
        return None

    def release(self,lock_key : str,identifier: str):
        """释放锁, 必须使用Lua 脚本保证原子性"""
        lua_script="""
        if redis.call('get',KEY[1]) == ARGV[1] then
            return redis.call('del',KEY[1])
        else
            return 0
        end
        """
        self.redis.eval(lua_script,1,lock_key,identifier)
        
            