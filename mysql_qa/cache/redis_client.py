"""Redis 缓存客户端。"""

import json

from redis import StrictRedis
from redis.exceptions import RedisError

from base.config import config
from base.logger import logger


class RedisClient:
    """封装 FAQ 数据和查询答案的 Redis 读写。"""

    def __init__(self, client=None):
        self.redis = client or StrictRedis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
            encoding="utf-8",
            password=config.REDIS_PASSWORD,
        )
        self.client = self.redis
        logger.info("Redis客户端初始化成功")

    def get_data(self, key):
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            result = json.loads(value)
            logger.info(f"获取数据成功！value: {key}, result: {result}")
            return result
        except (RedisError, TypeError, json.JSONDecodeError) as exc:
            logger.error("Redis获取数据失败: %s", exc)
            return None

    def set_data(self, key, value):
        try:
            self.redis.set(key, json.dumps(value, ensure_ascii=False))
            logger.info("Redis写入数据成功: %s", key)
            return True
        except (RedisError, TypeError) as exc:
            logger.error("Redis写入数据失败: %s, error: %s", key, exc)
            return False

    def get_answer(self, question):
        try:
            key = f"answer:{question}"
            value = self.redis.get(key)
            if value is None:
                return None
            logger.info(f"获取数据成功！value: {key}, result: {value}")
            return value
        except RedisError as exc:
            logger.error("Redis获取答案失败: %s", exc)
            return None

    def set_answer(self, question, answer):
        try:
            key = f"answer:{question}"
            if config.REDIS_EXPIRE > 0:
                self.redis.setex(key, config.REDIS_EXPIRE, answer)
            else:
                self.redis.set(key, answer)
            logger.info("Redis写入答案成功: %s", key)
            return True
        except RedisError as exc:
            logger.error("Redis写入答案失败: %s", exc)
            return False
