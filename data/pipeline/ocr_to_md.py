from pathlib import Path
from dotenv import load_dotenv
import os
from openai import OpenAI

# =========================
# 경로 고정 (이 파일 기준)
# =========================

PIPELINE_DIR = Path(__file__).resolve().parent        # data/pipeline
DATA_DIR = PIPELINE_DIR.parent                        # data
PROMPTS_DIR = DATA_DIR / "prompts"

# =========================
# .env 로드 (data/.env)
# =========================

ENV_PATH = DATA_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("OPENAI_API_KEY")
print("API KEY LOADED:", api_key is not None)

if api_key is None:
    raise RuntimeError("OPENAI_API_KEY not found in data/.env")

client = OpenAI(api_key=api_key)

# =========================
# 입력 / 출력 경로
# =========================

OCR_PATH = DATA_DIR / "ocr" / "program_001.txt"
PROMPT_PATH = PROMPTS_DIR / "ocr_to_md.txt"
OUT_MD_PATH = DATA_DIR / "ocr" / "program_001.md"

print("OCR_PATH:", OCR_PATH)
print("PROMPT_PATH:", PROMPT_PATH)
print("OCR_PATH exists:", OCR_PATH.exists())
print("PROMPT_PATH exists:", PROMPT_PATH.exists())

if not OCR_PATH.exists():
    raise FileNotFoundError(f"OCR file not found: {OCR_PATH}")

if not PROMPT_PATH.exists():
    raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")

# =========================
# 파일 로드
# =========================

ocr_text = OCR_PATH.read_text(encoding="utf-8")
prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

prompt = prompt_template.format(ocr_text=ocr_text)

# =========================
# LLM 호출
# =========================

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You convert noisy OCR text into clean, structured markdown."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0
)

markdown = response.choices[0].message.content

# =========================
# 결과 저장
# =========================

OUT_MD_PATH.write_text(markdown, encoding="utf-8")
print("Markdown saved to:", OUT_MD_PATH)
