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
from pathlib import Path


class Config:
    def __init__(self, config_file=None):
        project_root = Path(__file__).resolve().parent.parent
        self.config_file = Path(config_file) if config_file else project_root / 'config.ini'
        self.config = configparser.ConfigParser()
        if not self.config.read(self.config_file, encoding='utf-8'):
            raise FileNotFoundError(f'配置文件不存在: {self.config_file}')

        # MySQL 配置
        # MySQL 主机地址
        self.MYSQL_HOST = self.config.get('mysql', 'host')
        # MySQL 用户名
        self.MYSQL_PORT = self.config.getint('mysql', 'port')
        self.MYSQL_USER = self.config.get('mysql', 'user')
        # MySQL 密码
        self.MYSQL_PASSWORD = self.config.get('mysql', 'password')
        # MySQL 数据库名
        self.MYSQL_DATABASE = self.config.get('mysql', 'database')

        # Redis 配置
        # Redis 主机地址
        self.REDIS_HOST = self.config.get('redis', 'host')
        # Redis 端口
        self.REDIS_PORT = self.config.getint('redis', 'port')
        # Redis 密码
        self.REDIS_PASSWORD = self.config.get('redis', 'password', fallback='') or None
        # Redis 数据库编号
        self.REDIS_DB = self.config.getint('redis', 'db')
        self.REDIS_EXPIRE = self.config.getint('redis', 'expire', fallback=3600)
        # 日志文件路径
        log_file = Path(self.config.get('logger', 'log_file'))
        self.LOG_FILE = str(log_file if log_file.is_absolute() else project_root / log_file)


config = Config()

if __name__ == '__main__':
    conf = Config()
    print(conf.MYSQL_USER)
