import os
import sqlite3
import sys
import tempfile
import unittest

# 將專案根目錄加入 PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.normalizer import clean_html, generate_job_id, init_db, normalize_and_upsert


class TestNormalizer(unittest.TestCase):

    def test_clean_html(self):
        """測試 HTML 清理函數能正確去除 Tag 與轉義字符"""
        raw_html = "