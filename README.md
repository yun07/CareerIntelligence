# 🚀 Career Intelligence System (MVP)

一個基於 **Data Engineering Pipeline** 架構的個人職涯與市場數據分析系統。
透過打 ATS API 收集 Raw JD，配合 SQLite 進行不可變數據持久化，並運用 Gemini API 進行個人技能 Match 評估與市場需求看板生成。
📂 目錄結構
Plaintext
career-intelligence/
├── config/
│   ├── my_skills.json          # 本人核心技能 Profile (Ground Truth)
│   ├── market_skills.json      # 市場動態 Taxonomy / 知識庫設定
│   ├── search_buckets.json     # ATS 公司清單與廣義搜尋關鍵字
│   └── prompt_templates.yaml   # LLM Skill Extraction 與 Match 分析 Prompt
├── data/
│   ├── raw/                    # 不可變 Raw JSON 快照
│   └── jobs.db                 # SQLite 數據庫 (jobs, evaluations, skills)
├── src/
│   ├── db.py                   # SQLite Schema 建立與 Upsert 通用邏輯
│   ├── jd_collector.py         # Step 1: 抓取 ATS Raw JSON
│   ├── normalizer.py           # Step 2: Clean Data & Hash Upsert 到 SQLite
│   ├── skill_extractor.py      # Step 3: Call LLM 比對 Match & 抽取 Market Skills
│   └── dashboard.py            # Step 4: 印出 Skill Matrix 與高 Match 職缺
├── .env                        # 環境變數 (API Key) [Do NOT commit]
├── .env.example
├── .gitignore
├── main.py                     # Pipeline 總入口
├── README.md
└── requirements.txt
🛠️ 快速開始 (Quick Start)
1. 安裝環境
Bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
2. 設定 API Key
複製 .env.example 為 .env，並填入你的 Gemini API Key：

Bash
cp .env.example .env
⚙️ 執行 Pipeline (Pipeline Commands)
系統設計採用 單一職責原則 (Single Responsibility)，可以全套執行，亦可針對個別步驟獨立 Debug：

一鍵全套執行 (Fetch → Normalize → Extract → Dashboard)
Bash
python main.py --all
獨立 Debug 各步驟 (方便排查故障)
Step 1: 抓取 Raw JD (不消耗 AI Token)

Bash
python main.py --step fetch
Step 2: 寫入/更新 SQLite (驗證 Data Normalization)

Bash
python main.py --step normalize
Step 3: 行 LLM 比對與 Skill 抽取

Bash
python main.py --step extract
Step 4: 查看 市場 Skill Dashboard & Match 排名

Bash
python main.py --step dashboard
🧪 時空重放 / 歷史重評估 (Time Travel Re-evaluation)
當你更新了 config/my_skills.json（例如學會了新技能），無需重新爬蟲，直接調用歷史 SQLite 數據重新評估：

Bash
python main.py --step extract --version v2.0
python main.py --step dashboard --version v2.0
🔍 Debug 常用 SQL 查詢
可以直接用 VS Code SQLite Viewer 或命令行開 data/jobs.db 排查：

SQL
-- 查看目前活躍 Jobs 數量
SELECT COUNT(*) FROM jobs WHERE is_active = 1;

-- 查看前 10 名市場最高需求技能 (Market Demand %)
SELECT skill_name, category, COUNT(*) as count 
FROM extracted_market_skills 
GROUP BY skill_name 
ORDER BY count DESC 
LIMIT 10;