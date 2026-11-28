"""使用 BM25 在高频 FAQ 中检索答案。"""

import numpy as np
from rank_bm25 import BM25Okapi

from base.logger import logger
from mysql_qa.utils.preprocess import preprocess_text


class BM25Search:
    """整合 Redis、MySQL 与 BM25 的 FAQ 检索器。"""

    ORIGINAL_QUESTIONS_KEY = "qa_original_questions"
    TOKENIZED_QUESTIONS_KEY = "qa_tokenized_questions"

    def __init__(self, redis_client, mysql_client):
        self.redis_client = redis_client
        self.mysql_client = mysql_client
        self.original_questions = []
        self.questions = []
        self.bm25 = None
        self._load_data()

    @staticmethod
    def _normalize_questions(rows):
        """兼容数据库返回的 ``[(question,)]`` 和 ``[question]``。"""
        normalized = []
        for row in rows or []:
            question = row[0] if isinstance(row, (tuple, list)) else row
            if isinstance(question, str) and question.strip():
                normalized.append(question.strip())
        return normalized

    def _load_data(self):
        original_questions = self.redis_client.get_data(
            self.ORIGINAL_QUESTIONS_KEY
        )
        tokenized_questions = self.redis_client.get_data(
            self.TOKENIZED_QUESTIONS_KEY
        )

        if original_questions and tokenized_questions:
            self.original_questions = self._normalize_questions(original_questions)
            self.questions = tokenized_questions

        if (
            not self.original_questions
            or not self.questions
            or len(self.original_questions) != len(self.questions)
        ):
            self.original_questions = self._normalize_questions(
                self.mysql_client.fetch_questions()
            )
            if not self.original_questions:
                logger.warning("MySQL中没有可用于BM25检索的问题")
                self.questions = []
                return

            self.questions = [
                preprocess_text(question) for question in self.original_questions
            ]
            self.redis_client.set_data(
                self.ORIGINAL_QUESTIONS_KEY, self.original_questions
            )
            self.redis_client.set_data(
                self.TOKENIZED_QUESTIONS_KEY, self.questions
            )

        self.bm25 = BM25Okapi(self.questions)
        logger.info("BM25模型初始化成功，共加载 %s 个问题", len(self.questions))

    @staticmethod
    def _softmax(scores):
        scores = np.asarray(scores, dtype=float)
        if scores.size == 0:
            return scores
        exp_scores = np.exp(scores - np.max(scores))
        total = exp_scores.sum()
        return exp_scores / total if total else np.zeros_like(exp_scores)

    def search(self, query, threshold=0.85):
        """返回 ``(answer, needs_rag)``。

        ``needs_rag`` 为 ``True`` 表示 FAQ 未可靠命中，应交给后续 RAG。
        """
        if not isinstance(query, str) or not query.strip():
            logger.warning("无效查询: 查询必须是非空字符串")
            return None, True

        query = query.strip()
        cached_answer = self.redis_client.get_answer(query)
        if cached_answer is not None:
            return cached_answer, False

        if self.bm25 is None:
            logger.warning("BM25模型尚未加载，查询转交RAG")
            return None, True

        query_tokens = preprocess_text(query)
        if not query_tokens:
            return None, True

        try:
            scores = self.bm25.get_scores(query_tokens)
            normalized_scores = self._softmax(scores)
            best_index = int(np.argmax(normalized_scores))
            best_score = float(normalized_scores[best_index])

            if best_score >= threshold:
                matched_question = self.original_questions[best_index]
                answer = self.mysql_client.fetch_answer(matched_question)
                if answer:
                    self.redis_client.set_answer(query, answer)
                    logger.info(
                        "FAQ搜索成功，匹配问题: %s，相似度: %.3f",
                        matched_question,
                        best_score,
                    )
                    return answer, False

            logger.info(
                "FAQ未找到可靠答案，最高匹配度: %.3f，阈值: %.3f",
                best_score,
                threshold,
            )
            return None, True
        except Exception as exc:
            logger.exception("FAQ检索异常: %s", exc)
            return None, True
