import json
import os
import sqlite3

DB_PATH = os.path.join("data", "jobs.db")
MY_SKILLS_PATH = os.path.join("config", "my_skills.json")


def load_my_skills(my_skills_path: str = MY_SKILLS_PATH) -> set:
    """載入個人核心技能 profile，並轉為小寫的 set 以利無痛比對"""
    if not os.path.exists(my_skills_path):
        return set()

    try:
        with open(my_skills_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            skills = []
            for category_skills in data.get("skills", {}).values():
                skills.extend(category_skills)
            return {s.lower() for s in skills}
    except Exception as e:
        print(f"⚠️ 載入 my_skills.json 失敗: {e}")
        return set()


def generate_market_report(db_path: str = DB_PATH, my_skills_path: str = MY_SKILLS_PATH) -> dict:
    """讀取 SQLite 數據，計算市場 Skill 頻率與個人 Skills 的對比 (Match/Gap)"""
    if not os.path.exists(db_path):
        print(f"❌ 找不到資料庫檔案: {db_path}")
        return {}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 檢查是否存在 extracted_skills 欄位
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [row[1] for row in cursor.fetchall()]
    if "extracted_skills" not in columns:
        print("❌ jobs 表尚未包含 extracted_skills 欄位，請先執行 skill_extractor.py")
        conn.close()
        return {}

    cursor.execute("SELECT extracted_skills FROM jobs WHERE is_active = 1 AND extracted_skills IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    total_jobs = len(rows)
    if total_jobs == 0:
        print("ℹ️ 資料庫中尚無有效的 extracted_skills 數據。")
        return {}

    skill_counts = {}
    for (skills_json,) in rows:
        try:
            skills = json.loads(skills_json)
            for skill in skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        except json.JSONDecodeError:
            continue

    my_skills_set = load_my_skills(my_skills_path)

    # 組合統計結果
    report_data = []
    for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_jobs) * 100
        # 比對是否在 my_skills 內 (部分匹配/完全匹配)
        is_my_skill = any(my_s in skill.lower() or skill.lower() in my_s for my_s in my_skills_set)
        
        report_data.append({
            "skill": skill,
            "count": count,
            "percentage": percentage,
            "is_my_skill": is_my_skill
        })

    return {
        "total_jobs": total_jobs,
        "skills": report_data
    }


def print_cli_dashboard(report_data: dict):
    """印出乾淨、漂亮的 CLI 字符 Console 儀表板"""
    if not report_data or "skills" not in report_data:
        print("⚠️ 無可顯示的 Report 數據。")
        return

    total_jobs = report_data["total_jobs"]
    skills = report_data["skills"]

    print("\n" + "=" * 68)
    print(f"📊 CAREER & MARKET INTELLIGENCE DASHBOARD (Total Jobs: {total_jobs})")
    print("=" * 68)
    print(f"{'SKILL NAME':<25} | {'MY PROFILE':<12} | {'JOBS COUNT':<10} | {'DEMAND %':<8}")
    print("-" * 68)

    for item in skills:
        skill = item["skill"]
        status = "✅ MATCH" if item["is_my_skill"] else "❌ GAP"
        count = item["count"]
        pct = f"{item['percentage']:.1f}%"
        print(f"{skill:<25} | {status:<12} | {count:<10} | {pct:<8}")

    print("=" * 68 + "\n")


if __name__ == "__main__":
    report = generate_market_report()
    print_cli_dashboard(report)