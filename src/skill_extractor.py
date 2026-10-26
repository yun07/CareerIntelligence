import json
import os
import re
import sqlite3

DB_PATH = os.path.join("data", "jobs.db")

# 預設關鍵字規則庫 (支援 Word Boundary `\b` 避免誤判)
# 例如：獨立匹配 "c" 會錯配 "cat"，所以要特別定義 `\bC\b` 或 `\bC\+\+\b`
DEFAULT_SKILL_PATTERNS = {
    # 核心引擎與工具
    "Unreal Engine": [r"\bunreal engine\b", r"\bue4\b", r"\bue5\b"],
    "Houdini": [r"\bhoudini\b", r"\bhda\b"],
    "Unity": [r"\bunity\b", r"\bunity3d\b"],
    "Maya": [r"\bmaya\b"],
    "Blender": [r"\bblender\b"],
    "Substance": [r"\bsubstance\b", r"\bsubstance designer\b", r"\bsubstance painter\b"],
    # 程式語言與腳本
    "Python": [r"\bpython\b", r"\bpython3\b"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "VEX": [r"\bvex\b"],
    "HLSL / GLSL": [r"\bhlsl\b", r"\bglsl\b", r"\bshaderdev\b"],
    # 技術美術領域 (Tech Art Domains)
    "Procedural Generation": [r"\bprocedural\b", r"\bpcg\b", r"\bprocedural generation\b"],
    "Synthetic Data": [r"\bsynthetic data\b", r"\bcomputer vision\b", r"\bdataset generation\b"],
    "Shaders / Rendering": [r"\bshader\b", r"\bshaders\b", r"\brendering\b", r"\bray tracing\b"],
    "Rigging / Animation": [r"\brigging\b", r"\bcharacter rigging\b", r"\bcontrol rig\b"],
    "Pipeline Automation": [r"\bpipeline\b", r"\bautomation\b", r"\btooling\b", r"\bci/cd\b"],
    "PyTorch / AI": [r"\bpytorch\b", r"\btensorflow\b", r"\bdeep learning\b"]
}


def extract_skills_from_text(text: str, skill_patterns: dict = DEFAULT_SKILL_PATTERNS) -> list:
    """使用 Regex 在內文中匹配關鍵字，回傳 Deduplicated 的技能標籤 List"""
    if not text:
        return []

    matched_skills = []
    text_lower = text.lower()

    for skill, patterns in skill_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matched_skills.append(skill)
                break  # 只要匹配到其中一個 Pattern 就跳出，避免重複計數

    return sorted(list(set(matched_skills)))


def ensure_skills_column_exists(cursor):
    """動態升級 SQLite Schema：若 jobs 表缺乏 extracted_skills 欄位則自動新增"""
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [row[1] for row in cursor.fetchall()]
    if "extracted_skills" not in columns:
        cursor.execute("ALTER TABLE jobs ADD COLUMN extracted_skills TEXT")


def run_skill_extractor(db_path: str = DB_PATH) -> int:
    """對 SQLite 內所有 active 職缺提取技能，並將結果儲存為 JSON String"""
    if not os.path.exists(db_path):
        print(f"❌ 找不到資料庫檔案: {db_path}")
        return 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    ensure_skills_column_exists(cursor)

    # 抓取尚未提取過技能或有標籤更新需求的 active 職缺
    cursor.execute("SELECT id, description FROM jobs WHERE is_active = 1")
    rows = cursor.fetchall()

    processed_count = 0
    for job_id, description in rows:
        skills = extract_skills_from_text(description)
        skills_json = json.dumps(skills, ensure_ascii=False)

        cursor.execute("""
            UPDATE jobs
            SET extracted_skills = ?
            WHERE id = ?
        """, (skills_json, job_id))
        processed_count += 1

    conn.commit()
    conn.close()

    print(f"✅ [Step 3 Skill Extractor] 完成！共解析 {processed_count} 筆職缺技能標籤 (DB: {db_path})")
    return processed_count


if __name__ == "__main__":
    run_skill_extractor()