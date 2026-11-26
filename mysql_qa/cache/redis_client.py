# 该脚本用于: Redis缓存技术.

"""
需求：实现redis库的读写操作
思路步骤：
1. 初始化redis连接对象
2. 实现写入数据通用方法
3. 实现获取数据通用方法
4. 实现获取答案的方法
5. 实现设置答案的方法
"""
from redis import StrictRedis

from base.config import config
from base.logger import logger
import json

"""
redis客户端，要实现以下几个功能：

1. 初始化
2. get_data: 读取redis，对json字符串的数据进行反序列化
3. set_data: 将list<str>格式的数据进行序列化转成json字符串，存入redis
4. get_answer: 根据问题读取答案, key:answer:问题
5. set_answer: 缓存问题和答案对，key:answer:问题

"""


class RedisClient(object):
    def __init__(self):
        self.redis = StrictRedis(host=config.REDIS_HOST
                                 , port=config.REDIS_PORT
                                 , db=config.REDIS_DB
                                 # TODO 如果遇到了返回值是编码（非正常字符串）
                                 , decode_responses=True
                                 , encoding='utf-8'
                                 , password=config.REDIS_PASSWORD
                                 )

    def get_data(self, key):
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            result = json.loads(value)
            logger.info(f"获取数据成功！value: {key}, result: {result}")
            return result
        except Exception as e:
            logger.error(f'获取数据失败! error: {e}')
            return []

    def set_data(self, key, value):
        try:
            self.redis.set(key, json.dumps(value))
            logger.info(f"写入数据成功！value: {key}")
        except Exception as e:
            logger.error(f'写入数据失败！ {key} error: {e}')

    def get_answer(self, question):
        try:
            key = f"answer:{question}"
            value = self.redis.get(key)
            if value is None:
                return None
            logger.info(f"获取数据成功！value: {key}, result: {value}")
            return value
        except Exception as e:
            logger.error(f'获取数据失败！error: {e}')
            return None

    def set_answer(self, question, answer):
        try:
            key = f"answer:{question}"
            self.redis.set(key, answer)
            logger.info(f"写入数据成功！value: {key}, answer: {answer}")
        except Exception as e:
            logger.error(f'写入数据失败！ error: {e}')
