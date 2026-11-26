# 该脚本用于: 配置文件管理.

"""
需求：从配置文件中加载各类配置信息
思路步骤：
1. 创建配置解析器对象，并读取配置文件
2. 加载mysql配置
    2.1 host
    2.2 user
    2.3 password
    2.4 database
3. 加载redis配置
    3.1 host
    3.2 user
    3.3 password
    3.4 db
4. 加载日志路径
"""

# base/config.py
# 导入配置解析库
import configparser
import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    def __init__(self, config_file=None, env_file=None):
        project_root = Path(__file__).resolve().parent.parent
        env_path = Path(env_file) if env_file else project_root / '.env'
        load_dotenv(env_path, override=False)

        # 创建配置解析器
        self.config = configparser.ConfigParser()
        ini_path = Path(config_file) if config_file else project_root / 'config.ini'
        if ini_path.is_file():
            self.config.read(ini_path, encoding='utf-8')

        def get_value(section, option, env_name, fallback):
            env_value = os.getenv(env_name)
            if env_value is not None:
                return env_value
            return self.config.get(section, option, fallback=fallback)

        def get_int(section, option, env_name, fallback):
            value = get_value(section, option, env_name, fallback)
            try:
                return int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{env_name} 必须是整数，当前值为: {value!r}') from exc

        # MySQL 配置
        # MySQL 主机地址
        self.MYSQL_HOST = get_value('mysql', 'host', 'MYSQL_HOST', 'localhost')
        # MySQL 用户名
        self.MYSQL_PORT = get_int('mysql', 'port', 'MYSQL_PORT', 3306)
        self.MYSQL_USER = get_value('mysql', 'user', 'MYSQL_USER', 'root')
        # MySQL 密码
        self.MYSQL_PASSWORD = get_value('mysql', 'password', 'MYSQL_PASSWORD', '')
        # MySQL 数据库名
        self.MYSQL_DATABASE = get_value('mysql', 'database', 'MYSQL_DATABASE', 'subjects_kg')

        # Redis 配置
        # Redis 主机地址
        self.REDIS_HOST = get_value('redis', 'host', 'REDIS_HOST', 'localhost')
        # Redis 端口
        self.REDIS_PORT = get_int('redis', 'port', 'REDIS_PORT', 6379)
        # Redis 密码
        self.REDIS_PASSWORD = get_value('redis', 'password', 'REDIS_PASSWORD', '') or None
        # Redis 数据库编号
        self.REDIS_DB = get_int('redis', 'db', 'REDIS_DB', 0)
        # 日志文件路径
        log_file = Path(get_value('logger', 'log_file', 'LOGGER_FILE', 'logs/app.log'))
        self.LOG_FILE = str(log_file if log_file.is_absolute() else project_root / log_file)


config = Config()

if __name__ == '__main__':
    conf = Config()
    print(conf.MYSQL_USER)
