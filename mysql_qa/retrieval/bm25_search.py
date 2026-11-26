"""
需求：封装一个BM25搜索工具，用于从文档集合中搜索与用户问题最相似的文档。
思路：
1. 接收文档集合和匹配阈值
2. 对文档集合进行分词
3. 根据分词结果创建BM25模型
4. 对用户查询进行分词
5. 计算查询与每个文档的BM25得分
6. 获取得分最高的文档
7. 得分达到阈值时返回文档和得分，否则返回None和得分

"""
import jieba
from rank_bm25 import BM25L


class BM25Search:
    def __init__(self, documents, threshold=0.85):
        # 1. 接收文档集合和匹配阈值
        if not documents:
            raise ValueError("documents不能为空")
        if threshold < 0:
            raise ValueError("threshold不能小于0")

        self.documents = documents
        self.threshold = threshold

        # 2. 对文档集合进行分词
        tokenized_documents = []
        for document in self.documents:
            if not isinstance(document, str) or not document.strip():
                raise ValueError("documents中的每个文档都必须是非空字符串")
            tokenized_documents.append(self._tokenize(document))

        # 3. 根据分词结果创建BM25模型
        # BM25L在小型文档集上不容易出现负分，更适合当前的问答场景
        self.bm25 = BM25L(tokenized_documents)

    @staticmethod
    def _tokenize(text):
        # 转成小写后分词，并过滤空白内容
        words = jieba.lcut(text.lower())
        return [word.strip() for word in words if word.strip()]

    def search(self, query):
        # 4. 对用户查询进行分词
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query必须是非空字符串")
        tokenized_query = self._tokenize(query)

        # 5. 计算查询与每个文档的BM25得分
        scores = self.bm25.get_scores(tokenized_query)

        # 6. 获取得分最高的文档
        best_index = max(range(len(scores)), key=lambda index: scores[index])
        best_document = self.documents[best_index]
        best_score = float(scores[best_index])

        # 7. 得分达到阈值时返回文档和得分
        if best_score >= self.threshold:
            return best_document, best_score

        return None, best_score
