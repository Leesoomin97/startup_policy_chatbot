from pathlib import Path
from dotenv import load_dotenv
import os
import json
from datetime import date
from openai import OpenAI

# =========================
# 경로 고정 (이 파일 기준)
# =========================

PIPELINE_DIR = Path(__file__).resolve().parent        # data/pipeline
DATA_DIR = PIPELINE_DIR.parent                        # data
PROMPTS_DIR = DATA_DIR / "prompts"
OCR_DIR = DATA_DIR / "ocr"

# =========================
# .env 로드 (data/.env)
# =========================

load_dotenv(DATA_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")
print("API KEY LOADED:", api_key is not None)

if api_key is None:
    raise RuntimeError("OPENAI_API_KEY not found in data/.env")

client = OpenAI(api_key=api_key)

# =========================
# 입출력 경로
# =========================

MD_PATH = OCR_DIR / "program_001.md"
PROMPT_PATH = PROMPTS_DIR / "md_to_json.txt"
OUT_JSON_PATH = OCR_DIR / "program_001.json"

print("MD_PATH exists:", MD_PATH.exists())
print("PROMPT_PATH exists:", PROMPT_PATH.exists())

if not MD_PATH.exists():
    raise FileNotFoundError(f"Markdown file not found: {MD_PATH}")

if not PROMPT_PATH.exists():
    raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")

# =========================
# 파일 로드
# =========================

markdown_text = MD_PATH.read_text(encoding="utf-8")
prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

prompt = prompt_template.format(markdown_text=markdown_text)

# =========================
# LLM 호출
# =========================

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You extract structured JSON from policy documents."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0
)

raw_json = response.choices[0].message.content.strip()

# =========================
# JSON 파싱
# =========================

try:
    data = json.loads(raw_json)
except json.JSONDecodeError:
    raise ValueError("LLM output is not valid JSON:\n" + raw_json)

# =========================
# 수집일 자동 주입
# =========================

data["collected_date"] = str(date.today())

# =========================
# 저장
# =========================

OUT_JSON_PATH.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("JSON saved to:", OUT_JSON_PATH)
