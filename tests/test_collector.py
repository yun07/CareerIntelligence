import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 將專案根目錄加入 PYTHONPATH，確保可以 import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.jd_collector import fetch_greenhouse_jobs, fetch_lever_jobs, load_config


class TestJDCollector(unittest.TestCase):

    def test_load_config_exists(self):
        """測試 Config 能否正確載入"""
        config = load_config()
        self.assertIn("ats_targets", config)
        self.assertIn("greenhouse_companies", config["ats_targets"])

    @patch("src.jd_collector.requests.get")
    def test_fetch_greenhouse_jobs_success(self, mock_get):
        """測試 Greenhouse API 正常回應時的 解析 與 欄位結構"""
        # 1. 模擬 API 回傳的 Mock JSON Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jobs": [
                {
                    "id": 12345,
                    "title": "Senior Technical Artist",
                    "location": {"name": "London, UK"},
                    "absolute_url": "https://boards.greenhouse.io/epicgames/jobs/12345",
                    "content": "