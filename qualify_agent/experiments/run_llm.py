import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# 1. 프롬프트 로드
with open("prompt.md", "r", encoding="utf-8") as f:
    prompt = f.read()

# 2. 정책 데이터 로드
with open("policy_master.json", "r", encoding="utf-8") as f:
    policies = json.load(f)

# 3. apply_target이 있는 정책 중 무작위 5개 샘플링
valid_policies = [p for p in policies if p.get("apply_target")]
sampled_policies = random.sample(valid_policies, 5)

results = []

# 4. 정책별 LLM 호출
for p in sampled_policies:
    program_id = p["program_id"]
    apply_target = p["apply_target"]

    user_input = json.dumps(
        {
            "program_id": program_id,
            "apply_target": apply_target
        },
        ensure_ascii=False
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    # JSON 파싱 시도
    try:
        parsed = json.loads(content)
        parsed["__parse_success"] = True
    except json.JSONDecodeError:
        parsed = {
            "program_id": program_id,
            "raw_output": content,
            "__parse_success": False
        }

    results.append(parsed)

# 5. 결과 저장
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Done: output.json 생성 완료 (무작위 5개 정책)")
