import json
import os
from datetime import datetime
import requests

CONFIG_PATH = os.path.join("config", "search_buckets.json")
RAW_DATA_DIR = os.path.join("data", "raw")


def load_config():
    """載入搜尋策略 Config"""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"找不到 Config 檔案: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_greenhouse_jobs(company_slug):
    """從 Greenhouse 公開 API 抓取職缺 (無需 API Key)"""
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for item in data.get("jobs", []):
                jobs.append({
                    "raw_id": f"gh_{item.get('id')}",
                    "company": company_slug,
                    "title": item.get("title"),
                    "location": item.get("location", {}).get("name", "Unknown"),
                    "url": item.get("absolute_url"),
                    "description": item.get("content"),  # Raw HTML/Text JD
                    "source": "greenhouse",
                    "fetched_at": datetime.utcnow().isoformat()
                })
            print(f"  [Greenhouse] {company_slug}: 成功抓取 {len(jobs)} 份職缺")
            return jobs
        else:
            print(f"  [Greenhouse] {company_slug}: HTTP {response.status_code}")
    except Exception as e:
        print(f"  [Greenhouse] {company_slug} 失敗: {e}")
    return []


def fetch_lever_jobs(company_slug):
    """從 Lever 公開 API 抓取職缺 (無需 API Key)"""
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for item in data:
                # 組合 Description 與 text requirements
                content = item.get("descriptionHtml", "") + "\n" + str(item.get("lists", ""))
                jobs.append({
                    "raw_id": f"lever_{item.get('id')}",
                    "company": company_slug,
                    "title": item.get("text"),
                    "location": item.get("categories", {}).get("location", "Unknown"),
                    "url": item.get("hostedUrl"),
                    "description": content,  # Raw HTML/Text JD
                    "source": "lever",
                    "fetched_at": datetime.utcnow().isoformat()
                })
            print(f"  [Lever] {company_slug}: 成功抓取 {len(jobs)} 份職缺")
            return jobs
        else:
            print(f"  [Lever] {company_slug}: HTTP {response.status_code}")
    except Exception as e:
        print(f"  [Lever] {company_slug} 失敗: {e}")
    return []


def run_collector():
    """執行 Step 1 主邏輯"""
    print("🚀 [Step 1] 開始抓取 ATS Raw Jobs...")
    config = load_config()
    all_raw_jobs = []

    # 1. 抓取 Target Greenhouse 公司
    gh_companies = config.get("ats_targets", {}).get("greenhouse_companies", [])
    for comp in gh_companies:
        all_raw_jobs.extend(fetch_greenhouse_jobs(comp))

    # 2. 抓取 Target Lever 公司
    lever_companies = config.get("ats_targets", {}).get("lever_companies", [])
    for comp in lever_companies:
        all_raw_jobs.extend(fetch_lever_jobs(comp))

    # 3. 儲存成 Raw JSON 快照
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"jobs_raw_{today_str}.json"
    output_path = os.path.join(RAW_DATA_DIR, output_filename)

    # 亦寫入一個 latest 快照方便 next step 讀取
    latest_path = os.path.join(RAW_DATA_DIR, "jobs_raw_latest.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_raw_jobs, f, ensure_ascii=False, indent=2)

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(all_raw_jobs, f, ensure_ascii=False, indent=2)

    print(f"✅ 完成！共抓取 {len(all_raw_jobs)} 個職缺，快照已儲存至: {output_path}")
    return output_path


if __name__ == "__main__":
    # 支援獨立執行 Debug
    run_collector()