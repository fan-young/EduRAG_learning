"""mysql_qa 核心流程的离线测试。"""

import sys
import types
import unittest


try:
    import jieba  # noqa: F401
except ImportError:
    jieba_module = types.ModuleType("jieba")
    jieba_module.lcut = lambda text: list(text)
    sys.modules["jieba"] = jieba_module

try:
    import rank_bm25  # noqa: F401
except ImportError:
    rank_bm25_module = types.ModuleType("rank_bm25")

    class FakeBM25Okapi:
        def __init__(self, documents):
            self.documents = documents

        def get_scores(self, query):
            query_tokens = set(query)
            return [
                10.0 * len(query_tokens.intersection(document))
                for document in self.documents
            ]

    rank_bm25_module.BM25Okapi = FakeBM25Okapi
    sys.modules["rank_bm25"] = rank_bm25_module

try:
    import redis  # noqa: F401
except ImportError:
    redis_module = types.ModuleType("redis")
    redis_exceptions_module = types.ModuleType("redis.exceptions")

    class RedisError(Exception):
        pass

    redis_module.StrictRedis = object
    redis_exceptions_module.RedisError = RedisError
    sys.modules["redis"] = redis_module
    sys.modules["redis.exceptions"] = redis_exceptions_module

try:
    import pymysql  # noqa: F401
except ImportError:
    pymysql_module = types.ModuleType("pymysql")

    class MySQLError(Exception):
        pass

    pymysql_module.connect = lambda **kwargs: None
    pymysql_module.MySQLError = MySQLError
    sys.modules["pymysql"] = pymysql_module

try:
    import pandas  # noqa: F401
except ImportError:
    pandas_module = types.ModuleType("pandas")
    sys.modules["pandas"] = pandas_module

from mysql_qa.retrieval.bm25_search import BM25Search
from mysql_qa.main import MySQLQASystem


class FakeRedisClient:
    def __init__(self):
        self.data = {}
        self.answers = {}

    def get_data(self, key):
        return self.data.get(key)

    def set_data(self, key, value):
        self.data[key] = value
        return True

    def get_answer(self, question):
        return self.answers.get(question)

    def set_answer(self, question, answer):
        self.answers[question] = answer
        return True


class FakeMysqlClient:
    def __init__(self):
        self.questions = ["Python好学吗", "Redis有什么作用"]
        self.answers = {
            "Python好学吗": "Python入门相对友好。",
            "Redis有什么作用": "Redis可用于高速缓存。",
        }
        self.fetch_answer_calls = 0

    def fetch_questions(self):
        return self.questions

    def fetch_answer(self, question):
        self.fetch_answer_calls += 1
        return self.answers.get(question)


class BM25SearchTest(unittest.TestCase):
    def setUp(self):
        self.redis = FakeRedisClient()
        self.mysql = FakeMysqlClient()
        self.search = BM25Search(self.redis, self.mysql)

    def test_loads_questions_and_writes_cache(self):
        self.assertEqual(self.search.original_questions, self.mysql.questions)
        self.assertIn(BM25Search.ORIGINAL_QUESTIONS_KEY, self.redis.data)
        self.assertIn(BM25Search.TOKENIZED_QUESTIONS_KEY, self.redis.data)

    def test_bm25_match_reads_mysql_and_caches_answer(self):
        answer, needs_rag = self.search.search("Python好学吗", threshold=0.85)

        self.assertEqual(answer, "Python入门相对友好。")
        self.assertFalse(needs_rag)
        self.assertEqual(self.redis.answers["Python好学吗"], answer)

    def test_cached_answer_skips_mysql(self):
        self.redis.answers["Python好学吗"] = "缓存答案"

        answer, needs_rag = self.search.search("Python好学吗")

        self.assertEqual(answer, "缓存答案")
        self.assertFalse(needs_rag)
        self.assertEqual(self.mysql.fetch_answer_calls, 0)

    def test_unmatched_or_empty_query_needs_rag(self):
        answer, needs_rag = self.search.search("完全无关的问题", threshold=0.99)
        self.assertIsNone(answer)
        self.assertTrue(needs_rag)

        answer, needs_rag = self.search.search("   ")
        self.assertIsNone(answer)
        self.assertTrue(needs_rag)


class FakeSearch:
    def __init__(self, result):
        self.result = result

    def search(self, query, threshold):
        return self.result


class ClosableMysqlClient(FakeMysqlClient):
    def __init__(self):
        super().__init__()
        self.closed = False

    def close(self):
        self.closed = True


class MySQLQASystemTest(unittest.TestCase):
    def test_query_returns_answer_or_fallback_and_closes(self):
        mysql = ClosableMysqlClient()
        system = MySQLQASystem(
            mysql_client=mysql,
            redis_client=FakeRedisClient(),
            search=FakeSearch(("命中答案", False)),
        )
        self.assertEqual(system.query("问题"), "命中答案")

        system.bm25_search = FakeSearch((None, True))
        self.assertEqual(system.query("新问题"), "SQL中未找到答案")

        system.close()
        self.assertTrue(mysql.closed)


if __name__ == "__main__":
    unittest.main()
