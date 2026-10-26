import json
import os
import sqlite3
import sys
import tempfile
import unittest

# 將專案根目錄加入 PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.skill_extractor import extract_skills_from_text, run_skill_extractor


class TestSkillExtractor(unittest.TestCase):

    def test_extract_skills_from_text(self):
        """測試技能提取邏輯與關鍵字邊界匹配"""
        sample_jd = """
        We are seeking a Senior Technical Artist with deep knowledge of Unreal Engine (UE5) 
        and Houdini for procedural environment creation. High-level Python and VEX scripting 
        skills required. Experience with Synthetic Data or C++ pipeline tools is a big plus.
        """
        extracted = extract_skills_from_text(sample_jd)

        # 斷言預期出現的技能標籤
        self.assertIn("Unreal Engine", extracted)
        self.assertIn("Houdini", extracted)
        self.assertIn("Python", extracted)
        self.assertIn("VEX", extracted)
        self.assertIn("Procedural Generation", extracted)
        self.assertIn("Synthetic Data", extracted)
        self.assertIn("C++", extracted)

        # 斷言未出現在內文的技能
        self.assertNotIn("Unity", extracted)
        self.assertNotIn("Blender", extracted)

    def test_word_boundary_isolation(self):
        """測試單字邊界，確保像 C/CPP 不會誤判或漏抓"""
        text = "Strong C++ and Python 3 developer."
        extracted = extract_skills_from_text(text)
        self.assertIn("C++", extracted)
        self.assertIn("Python", extracted)

    def test_run_skill_extractor_db_flow(self):
        """測試完整的 SQLite 讀取、提取與寫入 extracted_skills 流程"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

            # 1. 建立測試 SQLite 資料庫並寫入 dummy 數據
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE jobs (
                    id TEXT PRIMARY KEY,
                    company TEXT,
                    title TEXT,
                    description TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            cursor.execute("""
                INSERT INTO jobs (id, company, title, description)
                VALUES ('job_001', 'Test Studio', 'TA Engineer', 'Must master UE5, Houdini and Python.')
            """)
            conn.commit()
            conn.close()

            # 2. 執行 Extractor
            count = run_skill_extractor(db_path=db_path)
            self.assertEqual(count, 1)

            # 3. 驗證欄位是否已自動建立且資料正確寫入
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT extracted_skills FROM jobs WHERE id = 'job_001'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)

            skills = json.loads(row[0])
            self.assertIn("Unreal Engine", skills)
            self.assertIn("Houdini", skills)
            self.assertIn("Python", skills)
            conn.close()

            # 清理臨時檔
            os.remove(db_path)


if __name__ == "__main__":
    unittest.main()