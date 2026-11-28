"""中文问题文本预处理。"""

import jieba

from base.logger import logger


def preprocess_text(text):
    """将非空文本转为适合 BM25 的小写词元列表。"""
    if not isinstance(text, str) or not text.strip():
        logger.warning("文本预处理失败: 输入必须是非空字符串")
        return []

    words = jieba.lcut(text.lower().strip())
    return [word.strip() for word in words if word.strip()]
