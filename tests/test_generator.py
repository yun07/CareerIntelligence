import json
import os
import sqlite3
import sys
import tempfile
import unittest

# 將專案根目錄加入 PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.report_generator import generate_market_report, load_my_skills


class TestReportGenerator(unittest.TestCase):

    def test_load_my_skills(self):
        """測試 my_skills.json 的載入與集合轉化"""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False, encoding="utf-8") as tmp_json:
            json_path = tmp_json.name
            sample_profile = {
                "skills": {
                    "engine": ["Unreal Engine 5", "Houdini"],
                    "scripting": ["Python"]
                }
            }
            json.dump(sample_profile, tmp_json)
            tmp_json.flush()

            skills_set = load_my_skills(json_path)
            self.assertIn("unreal engine 5", skills_set)
            self.assertIn("houdini", skills_set)
            self.assertIn("python", skills_set)

            os.remove(json_path)

    def test_generate_market_report_calculation(self):
        """測試 SQL 聚合後的 Skill 頻率與 Match/Gap 邏輯計算"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db, \
             tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False, encoding="utf-8") as tmp_json:
            
            db_path = tmp_db.name
            json_path = tmp_json.name

            # 1. 寫入模擬 my_skills
            json.dump({"skills": {"core": ["Unreal Engine", "Python"]}}, tmp_json)
            tmp_json.flush()

            # 2. 建立測試 DB (寫入 2 筆 Jobs extracted_skills)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE jobs (
                    id TEXT PRIMARY KEY,
                    extracted_skills TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            cursor.execute("INSERT INTO jobs VALUES ('1', '[\"Unreal Engine\", \"Python\", \"Houdini\"]', 1)")
            cursor.execute("INSERT INTO jobs VALUES ('2', '[\"Unreal Engine\", \"C++\"]', 1)")
            conn.commit()
            conn.close()

            # 3. 產出 Report
            report = generate_market_report(db_path=db_path, my_skills_path=json_path)

            self.assertEqual(report["total_jobs"], 2)
            skills = report["skills"]

            # Unreal Engine 出現 2 次 (100%) -> MATCH
            ue_item = next(s for s in skills if s["skill"] == "Unreal Engine")
            self.assertEqual(ue_item["count"], 2)
            self.assertEqual(ue_item["percentage"], 100.0)
            self.assertTrue(ue_item["is_my_skill"])

            # Houdini 出現 1 次 (50%) -> GAP (因為不在 my_skills)
            houdini_item = next(s for s in skills if s["skill"] == "Houdini")
            self.assertEqual(houdini_item["count"], 1)
            self.assertEqual(houdini_item["percentage"], 50.0)
            self.assertFalse(houdini_item["is_my_skill"])

            # 清理臨時檔
            os.remove(db_path)
            os.remove(json_path)


if __name__ == "__main__":
    unittest.main()