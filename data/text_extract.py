import pdfplumber
import pytesseract
from PIL import Image

# tesseract 경로 명시
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

with pdfplumber.open("pdfs/program_001.pdf") as pdf:
    # ❗ page[1]부터 시작 (0은 표지)
    page = pdf.pages[1]

    image = page.to_image(resolution=300).original
    image.save("debug_page.png")  # 이미 검증됨

# 🔴 OCR 옵션이 핵심
text = pytesseract.image_to_string(
    image,
    lang="kor",
    config="--oem 3 --psm 6"
)

print("===== OCR RESULT =====")
print(repr(text))

from pathlib import Path

out_dir = Path("ocr")
out_dir.mkdir(exist_ok=True)

with open(out_dir / "program_001.txt", "w", encoding="utf-8") as f:
    f.write(text)

