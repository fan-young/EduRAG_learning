"""
需求： 封装一个日志获取工具，用于项目中所有模块的日志处理。需要在控制台和文件中分类
思路：
1. 确保日志目录存在，不存在创建
2. 创建日志记录器: Logger
    2.1 获取Logger对象
    2.2 设置日志级别为所有控制器最低的(设置全局的日志级别)
3. 创建控制台控制器：StreamHandler
    3.1 创建控制台处理器对象
    3.2 设置日志级别为INFO
4. 创建文件处理器:FileHandler，并指定目录
    4.1 创建文件处理对象
    4.2 设置日志级别为DEBUG
5. 定义并设置日志格式：
    5.1 定义日志格式：logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    5.2 设置处理器日志格式
6. 把处理器添加到logger中

"""
import os.path
import logging


def setup_logger(logger_name, logger_file='logs/app.log'):
    # 1. 确保日志目录存在，不存在创建
    # logger_file 是日志的文件名，所以我们先取到它所在的目录 os.path.pathj
    dirname = os.path.dirname(logger_file)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    # 2. 创建日志记录器: Logger
    # 2.1 获取Logger对象
    logger = logging.getLogger(logger_name)
    # 2.2 设置日志级别为所有控制器最低的(设置全局的日志级别)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # 3. 创建控制台控制器：StreamHandler
        # 3.1 创建控制台处理器对象
        stream_handler = logging.StreamHandler()
        # 3.2 设置日志级别为INFO
        stream_handler.setLevel(logging.INFO)
        # 4. 创建文件处理器:FileHandler，并指定目录
        # 4.1 创建文件处理对象
        # TODO 需要注意，非特殊情况，mode一定不要写w
        file_handler = logging.FileHandler(logger_file, mode='a', encoding='utf-8')
        # 4.2 设置日志级别为DEBUG
        # TODO 实际工作中INFO就可以， DEBUG更多是用于本地调试代码的时候使用
        file_handler.setLevel(logging.DEBUG)
        # 5. 定义并设置日志格式：
        # 5.1 定义日志格式：logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        # 5.2 设置处理器日志格式
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        # 6. 把处理器添加到logger中
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger('EduRAG')
print("当前工作目录：", os.getcwd())
print("logger.py 所在目录：", os.path.dirname(os.path.abspath(__file__)))
