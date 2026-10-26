import os
import sys
import unittest
from unittest.mock import patch

# 將專案根目錄加入 PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_pipeline, main


class TestMainOrchestrator(unittest.TestCase):

    @patch("main.run_scraper")
    @patch("main.run_data_cleaner")
    @patch("main.run_skill_extractor")
    @patch("main.generate_market_report")
    @patch("main.print_cli_dashboard")
    def test_run_pipeline_all_steps(
        self, mock_print, mock_report, mock_extract, mock_clean, mock_scrape
    ):
        """測試全流程串接，確保每個子模組依序被調用"""
        steps = ["scrape", "clean", "extract", "report"]
        run_pipeline(steps)

        mock_scrape.assert_called_once()
        mock_clean.assert_called_once()
        mock_extract.assert_called_once()
        mock_report.assert_called_once()
        mock_print.assert_called_once()

    @patch("main.run_skill_extractor")
    @patch("main.generate_market_report")
    @patch("main.print_cli_dashboard")
    def test_run_pipeline_selective_steps(
        self, mock_print, mock_report, mock_extract
    ):
        """測試選擇性執行 (僅執行 Extract 與 Report)"""
        steps = ["extract", "report"]
        run_pipeline(steps)

        mock_extract.assert_called_once()
        mock_report.assert_called_once()
        mock_print.assert_called_once()

    @patch("sys.argv", ["main.py", "--all"])
    @patch("main.run_pipeline")
    def test_main_cli_arg_all(self, mock_run_pipeline):
        """測試命令行參數 --all 是否正確解讀為四個全步驟"""
        main()
        mock_run_pipeline.assert_called_once_with(["scrape", "clean", "extract", "report"])

    @patch("sys.argv", ["main.py", "--extract", "--report"])
    @patch("main.run_pipeline")
    def test_main_cli_arg_selective(self, mock_run_pipeline):
        """測試命令行組合參數 --extract --report 是否正確解析"""
        main()
        mock_run_pipeline.assert_called_once_with(["extract", "report"])


if __name__ == "__main__":
    unittest.main()