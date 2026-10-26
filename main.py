import argparse
import sys
import os

# 確保專案根目錄納入系統路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.job_scraper import run_scraper
from src.data_cleaner import run_data_cleaner
from src.skill_extractor import run_skill_extractor
from src.report_generator import generate_market_report, print_cli_dashboard


def run_pipeline(steps: list):
    """根據指定的步驟依序執行 ETL Pipeline"""
    print("🚀 [Pipeline Orchestrator] 開始執行工作流程...\n")

    if "scrape" in steps:
        print("📌 Step 1: 執行職缺抓取器 (Job Scraper)...")
        run_scraper()
        print("-" * 50)

    if "clean" in steps:
        print("📌 Step 2: 執行資料清理器 (Data Cleaner)...")
        run_data_cleaner()
        print("-" * 50)

    if "extract" in steps:
        print("📌 Step 3: 執行技能提取器 (Skill Extractor)...")
        run_skill_extractor()
        print("-" * 50)

    if "report" in steps:
        print("📌 Step 4: 產出市場需求分析報告 (Report Generator)...")
        report = generate_market_report()
        print_cli_dashboard(report)

    print("🎉 [Pipeline Orchestrator] 流程執行完畢！")


def main():
    parser = argparse.ArgumentParser(
        description="Career & Market Intelligence Pipeline Orchestrator",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--all", action="store_true",
        help="執行完整的 ETL 全流程 (Scrape -> Clean -> Extract -> Report)"
    )
    parser.add_argument(
        "--scrape", action="store_true",
        help="Step 1: 抓取目標平台職缺數據"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Step 2: 清理職缺數據與去重 (Deduplication)"
    )
    parser.add_argument(
        "--extract", action="store_true",
        help="Step 3: 提取關鍵技能標籤 (Regex Match)"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Step 4: 產出市場技能需求 dashboard"
    )

    args = parser.parse_args()

    # 若未指定任何參數，預設顯示 Help
    if not any([args.all, args.scrape, args.clean, args.extract, args.report]):
        parser.print_help()
        sys.exit(0)

    steps = []
    if args.all:
        steps = ["scrape", "clean", "extract", "report"]
    else:
        if args.scrape:
            steps.append("scrape")
        if args.clean:
            steps.append("clean")
        if args.extract:
            steps.append("extract")
        if args.report:
            steps.append("report")

    run_pipeline(steps)


if __name__ == "__main__":
    main()