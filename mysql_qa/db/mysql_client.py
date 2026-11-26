# 该脚本用于: MySQL数据库的基础操作.

"""
需求：实现"基于mysql数据库构建问答系统"中mysql相关的操作，包括: 加载高频FAQ数据到mysql、拉取所有的问题、通过问题检索答案 功能
思路步骤：
1. 实现mysql连接初始化，拿到client对象
    1.1 基于配置文件，在构造方法中连接mysql，并拿到cursor对象
    1.2 实现close方法，用于断开连接
2. 实现高频FAQ数据加载mysql功能
    2.1 实现FAQ表建表操作
    2.2 实现读取csv文件并插入mysql的功能
3. 实现拉取所有问题的方法
4. 实现通过问题检索对应答案的方法
"""
"""
mysql-client模块

需要实现的功能列表：
1. 初始化Mysql客户端
2. 创建高频问答表
3. csv数据写入mysql
4. 读取所有的问题
5. 根据问题获取对应的答案

"""

from pymysql import connect, MySQLError
from base.config import config
from base.logger import logger
import pandas as pd


class MysqlClient:

    # 1. 初始化Mysql客户端
    def __init__(self):
        try:
            # mysql链接
            self.connect = connect(
                host=config.MYSQL_HOST
                , user=config.MYSQL_USER
                , password=config.MYSQL_PASSWORD
                , db=config.MYSQL_DATABASE
                , port=config.MYSQL_PORT
            )
            # mysql游标
            self.cursor = self.connect.cursor()
            logger.info("mysql初始化成功")
        except Exception as e:
            logger.error("mysql初始化失败: {}".format(e))
            raise

    # 2. 创建高频问答表
    def create_table(self):
        create_table_query = '''
                             CREATE TABLE IF NOT EXISTS jpkb \
                             ( \
                                 id           INT AUTO_INCREMENT PRIMARY KEY, \
                                 subject_name VARCHAR(20), \
                                 question     VARCHAR(1000), \
                                 answer       VARCHAR(1000) \
                             ) \
                             '''
        try:
            self.cursor.execute(create_table_query)
            self.connect.commit()
            logger.info("建表语句执行成功！")
        except Exception as e:
            logger.error("建表语句执行失败: {}".format(e))
            raise

    # 3. csv数据写入mysql
    def insert_data(self, csv_path):
        data_frame = pd.read_csv(csv_path)
        try:
            for _, row in data_frame.iterrows():
                question = row['问题']
                answer = row['答案']
                subject = row['学科名称']
                # 防注入
                # insert into jpkb (question, answer, subject_name) values ('a','a','a');drop table jpkb
                sql = 'insert into jpkb (question, answer, subject_name) values (%s, %s, %s)'
                self.cursor.execute(sql, (question, answer, subject))
            # 把这几百条数据的提交作为一次事务，要么全部成功，要不全部失败
            self.connect.commit()
            logger.info("输入导入成功，共：{}条".format(data_frame.count()))
        except Exception as e:
            # 事务回滚
            self.connect.rollback()
            logger.error("数据导入失败: {}".format(e))

    # 4. 读取所有的问题
    def fetch_questions(self):
        try:
            sql = "select question from jpkb"
            self.cursor.execute(sql)
            # tuple[tuple] -> [条数=467，列=1]
            results = self.cursor.fetchall()
            # row in results ：拿到每条数据（包含多个列）
            # row[0] ：拿到question列
            questions = [row[0] for row in results]
            logger.info("获取到了所有的问题：{}条".format(len(questions)))
            return questions
        except Exception as e:
            logger.error("获取所有的问题失败: {}".format(e))
            return []

    # 5. 根据问题获取对应的答案
    def fetch_answer(self, question):
        try:
            sql = "select answer from jpkb where question = %s"
            self.cursor.execute(sql, (question,))
            result = self.cursor.fetchone()
            if result:
                logger.info("获取问题: {} 对应的答案成功".format(question))
                return result[0]
            else:
                logger.error("没有找到问题对应的答案: {}".format(question))
                return None
        except Exception as e:
            logger.error("查询问题对应的答案失败: {}".format(e))
            return None


    def close(self):
        # 关闭数据库连接
        try:
            self.cursor.close()
            # 关闭连接
            self.connect.close()
            # 记录关闭成功
            logger.info("MySQL 连接已关闭")
        except MySQLError as e:
            # 记录关闭失败
            logger.error(f"关闭连接失败: {e}")



if __name__ == '__main__':
    mysql_client = MysqlClient()
    # mysql_client.create_table()
    # mysql_client.insert_data(
    #     '/Users/itheima/Documents/黑马/讲课/就业班/edu-rag/南京1期/学生端/04-代码/00001.项目代码_课上/integrated_qa_system/mysql_qa/data/JP学科知识问答.csv')

    # questions = mysql_client.fetch_questions()
    # print(questions)

    answer = mysql_client.fetch_answer("关联子查询的执行顺序是什么")
    print(answer)
