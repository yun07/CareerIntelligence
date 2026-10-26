import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime

RAW_JSON_PATH = os.path.join("data", "raw", "jobs_raw_latest.json")
DB_PATH = os.path.join("data", "jobs.db")


def clean_html(raw_html: str) -> str:
    """清理 HTML 標籤與多餘空白，轉為乾淨的 Plain Text"""
    if not raw_html:
        return ""
    # 移除 HTML Tags
    text = re.sub(r"<[^>]+>", " ", raw_html)
    # 解碼常見 HTML Entities
    text = text.replace(" ", " ").replace("&", "&").replace("<", "<").replace(">", ">")
    # 清理重複空白與換行
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generate_job_id(url: str) -> str:
    """以 URL 產生穩定的 MD5 Hash ID，確保同一個 Job 永遠有相同 ID"""
    return hashlib.md5(url.strip().encode("utf-8")).hexdigest()


def init_db(db_path: str = DB_PATH):
    """初始化 SQLite Schema (若 Table 不存在則建立)"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 建立 jobs 表 (包含 first_seen / last_seen 及 is_active 狀態)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            url TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            source TEXT,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()


def normalize_and_upsert(raw_data_path: str = RAW_JSON_PATH, db_path: str = DB_PATH):
    """讀取 Raw JSON，清洗數據並執行 SQLite Upsert"""
    if not os.path.exists(raw_data_path):
        print(f"❌ 找不到 Raw Data 檔案: {raw_data_path}")
        return 0, 0

    init_db(db_path)

    with open(raw_data_path, "r", encoding="utf-8") as f:
        raw_jobs = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    inserted_count = 0
    updated_count = 0
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for item in raw_jobs:
        url = item.get("url")
        if not url:
            continue

        job_id = generate_job_id(url)
        company = item.get("company", "Unknown").strip()
        title = item.get("title", "Unknown").strip()
        location = item.get("location", "Unknown").strip()
        cleaned_desc = clean_html(item.get("description", ""))
        source = item.get("source", "unknown")

        # 檢查 Job 是否已存在於 DB
        cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,))
        exists = cursor.fetchone()

        if exists:
            # 舊 Job：更新 last_seen 時間與內容 (若有變化)
            cursor.execute("""
                UPDATE jobs 
                SET last_seen = ?, description = ?, is_active = 1
                WHERE id = ?
            """, (now_str, cleaned_desc, job_id))
            updated_count += 1
        else:
            # 新 Job：插入新紀錄
            cursor.execute("""
                INSERT INTO jobs (id, company, title, location, url, description, source, first_seen, last_seen, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (job_id, company, title, location, url, cleaned_desc, source, now_str, now_str))
            inserted_count += 1

    conn.commit()
    conn.close()

    print(f"✅ [Step 2 Normalizer] 處理完成！新增: {inserted_count} 筆, 更新: {updated_count} 筆 (DB: {db_path})")
    return inserted_count, updated_count


if __name__ == "__main__":
    normalize_and_upsert()