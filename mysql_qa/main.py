"""MySQL FAQ 问答系统入口。"""

import sys
import time
from pathlib import Path

# 同时支持 ``python -m mysql_qa.main`` 和直接运行本文件。
if __package__ in (None, ""):
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from base.logger import logger
from mysql_qa.cache.redis_client import RedisClient
from mysql_qa.db.mysql_client import MySQLClient
from mysql_qa.retrieval.bm25_search import BM25Search


class MySQLQASystem:
    """统一编排 MySQL、Redis 和 BM25 查询流程。"""

    def __init__(self, mysql_client=None, redis_client=None, search=None):
        self.mysql_client = mysql_client or MySQLClient()
        self.redis_client = redis_client or RedisClient()
        self.bm25_search = search or BM25Search(
            self.redis_client, self.mysql_client
        )

    def query_with_status(self, query):
        """返回 ``(answer, needs_rag)``，供后续融合 RAG 使用。"""
        start_time = time.perf_counter()
        logger.info("开始处理查询: %s", query)

        answer, needs_rag = self.bm25_search.search(query, threshold=0.85)
        if answer:
            logger.info("FAQ返回答案: %s", answer)
        else:
            logger.info("FAQ未找到答案，需要调用RAG系统")

        logger.info("查询处理耗时: %.3f秒", time.perf_counter() - start_time)
        return answer, needs_rag

    def query(self, query):
        """处理一次查询；未命中 FAQ 时返回明确提示。"""
        answer, _ = self.query_with_status(query)
        return answer or "SQL中未找到答案"

    def close(self):
        """释放数据库连接。"""
        self.mysql_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def main():
    mysql_qa = None
    try:
        mysql_qa = MySQLQASystem()
        print("\n欢迎使用MySQL问答系统")
        print("输入查询进行回答，输入 exit 退出")

        while True:
            query = input("\n请输入查询: ").strip()
            if query.lower() == "exit":
                print("再见！")
                break
            if not query:
                print("请输入非空问题")
                continue
            print(f"答案: {mysql_qa.query(query)}")
    except (KeyboardInterrupt, EOFError):
        print("\n已退出MySQL问答系统")
    except Exception as exc:
        logger.exception("系统错误: %s", exc)
    finally:
        if mysql_qa is not None:
            mysql_qa.close()


if __name__ == "__main__":
    main()
