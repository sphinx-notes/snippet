"""
    sphinxnotes.khufu.snippet.keyword
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions for keywords extraction.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from typing import List, Tuple, Optional
from abc import ABC, abstractclassmethod
import string
from collections import Counter

import langdetect
import jieba
import jieba.analyse
from pypinyin import lazy_pinyin
import summa
from stopwordsiso import stopwords

class Extractor(ABC):
    """Keyword extractor abstract class."""

    @abstractclassmethod
    def extract(self, text:str, top_n:int=10) -> List[Tuple[str,float]]:
        """Return keywords (and their rank) of given text."""
        pass


class FrequencyExtractor(Extractor):
    """Keyword extractor based on frequency statistic."""

    def extract(self, text:str, top_n:int=10) -> List[Tuple[str,float]]:
        # TODO: zh -> en
        # Normalize
        text = self.normalize(text)
        # Tokenize
        words = self.tokenize(text)
        # Stopwords removal
        words = self.strip_stopwords(words)
        # Get top 5 words as keyword
        keywords = Counter(words).most_common(top_n)
        # Convert int rank to float
        for i, tup in enumerate(keywords):
            word, rank = tup
            keywords[i] = (word, rank * 1.0)
        # Generate a pinyin version
        keywords_pinyin = []
        for word, rank in keywords:
            pinyin = self.trans_to_pinyin(word)
            if pinyin:
                keywords_pinyin.append((pinyin, rank))
        return keywords + keywords_pinyin


    @staticmethod
    def normalize(text:str) -> str:
        punctuation =  string.punctuation + "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
        # Convert text to lowercase
        text = text.lower()
        # Remove punctuation (both english and chinese)
        text = text.translate(text.maketrans('', '', punctuation))
        # White spaces removals
        text = text.strip()
        # Replace newline to whitespace
        text = text.replace('\n', ' ')
        return text


    @staticmethod
    def tokenize(text:str) -> List[str]:
        def _tokenize(tokens:List[str]) -> List[str]:
            # Recursive tokenize to deal with multiple language text
            new_tokens = []
            for token in tokens:
                try:
                    lang = langdetect.detect(token)
                except Exception:
                    pass
                else:
                    if lang == 'zh-cn':
                        new_tokens += jieba.cut_for_search(token)
                    else:
                        new_tokens += token.split(' ')
            return new_tokens
        tokens = [text]
        while True:
            new_tokens = _tokenize(tokens)
            if len(new_tokens) == len(tokens):
                break
            tokens = new_tokens
        return new_tokens


    @staticmethod
    def trans_to_pinyin(word:str) -> Optional[str]:
        return ' '.join(lazy_pinyin(word, errors='ignore'))


    @staticmethod
    def strip_stopwords(words:List[str]) -> List[str]:
        stw = stopwords(['en', 'zh'])
        new_words = []
        for word in words:
            if not word in stw:
                new_words.append(word)
        return new_words


class TextRankExtractor(Extractor):
    """Keyword extractor based on text rank algorithm."""

    def extract(self, text:str, top_n:int=10) -> List[Tuple[str,float]]:
        lang = langdetect.detect(text)
        if lang == 'zh-cn':
            return jieba.analyse.textrank(text, topK=top_n, withWeight=True)
        else:
            return summa.keywords.keywords(text, scores=True)[:top_n]
