"""
    sphinxnotes.snippet.keyword
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions for keywords extraction.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Optional
from abc import ABC, abstractclassmethod
import string
from collections import Counter

class Extractor(ABC):
    """Keyword extractor abstract class."""

    @abstractclassmethod
    def extract(self, text:str, top_n:int=10) -> List[Tuple[str,float]]:
        """Return keywords (and their rank) of given text."""
        pass


class FrequencyExtractor(Extractor):
    """
    Keyword extractor based on frequency statistic.

    TODO: extract date, time
    """

    def __init__(self):
        # Import NLP libs here to prevent import overhead
        from langid import rank
        from jieba import cut_for_search
        from pypinyin import lazy_pinyin
        from stopwordsiso import stopwords
        from wordsegment import load, segment

        load()
        self._detect_langs = rank
        self._tokenize_zh_cn = cut_for_search
        self._tokenize_en = segment
        self._pinyin = lazy_pinyin
        self._stopwords = stopwords

        self._punctuation = string.punctuation + "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."

    def extract(self, text:str, top_n:int=10) -> List[Tuple[str,float]]:
        # TODO: zh -> en
        # Normalize
        text = self.normalize(text)
        # Tokenize
        words = self.tokenize(text)
        # Invalid token removal
        words = self.strip_invalid_token(words)
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


    def normalize(self, text:str) -> str:
        # Convert text to lowercase
        text = text.lower()
        # Remove punctuation (both english and chinese)
        text = text.translate(text.maketrans('', '', self._punctuation))
        # White spaces removals
        text = text.strip()
        # Replace newline to whitespace
        text = text.replace('\n', ' ')
        return text


    def tokenize(self, text:str) -> List[str]:
        # Get top most 5 langs
        langs = self._detect_langs(text)[:5]
        tokens = [text]
        new_tokens = []
        for lang in langs:
            for token in tokens:
                if lang[0] == 'zh':
                    new_tokens += self._tokenize_zh_cn(token)
                elif lang[0] == 'en':
                    new_tokens += self._tokenize_en(token)
                else:
                    new_tokens += token.split(' ')
            tokens = new_tokens
            new_tokens = []
        return tokens


    def trans_to_pinyin(self, word:str) -> Optional[str]:
        return ' '.join(self._pinyin(word, errors='ignore'))


    def strip_stopwords(self, words:List[str]) -> List[str]:
        stw = self._stopwords(['en', 'zh'])
        new_words = []
        for word in words:
            if not word in stw:
                new_words.append(word)
        return new_words


    def strip_invalid_token(self, tokens:List[str]) -> List[str]:
        return [token for token in tokens if token  != '']


class TextRankExtractor(Extractor):
    """Keyword extractor based on text rank algorithm."""

    def __init__(self):
        # Import NLP libs here to prevent import overhead
        from langid import classify
        from jieba.analyse import textrank
        from summa.keywords import keywords

        self._detect_lang = classify
        self._textrank_zh_cn = textrank
        self._textrank_en = keywords


    def extract(self, text:str, top_n:int=10) -> List[Tuple[str,float]]:
        lang = self._detect_lang(text)
        if lang[0] == 'zh':
            return self._textrank_zh_cn(text, topK=top_n, withWeight=True)
        else:
            return self._textrank_en(text, scores=True)[:top_n]
