import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# EXAONE 모델 로드
model_name = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16 if device=="cuda" else torch.float32,  # GPU 사용 시 bfloat16, 그렇지 않으면 float32 사용
    trust_remote_code=True,
    device_map="auto" if device=="cuda" else None
)

tokenizer = AutoTokenizer.from_pretrained(model_name)

def summarize_news_item(news_title: str, news_content: str, max_new_tokens: int = 512) -> str:
    """
    단일 뉴스 항목에 대한 요약문 생성
    - news_title: 뉴스 제목
    - news_content: 뉴스 내용
    - max_new_tokens: 생성될 최대 토큰 수
    """
    prompt = f"""
    다음 정보를 바탕으로 뉴스를 요약해서 정리해주세요.
    
    [입력 데이터]
    - 뉴스 제목: {news_title}
    - 뉴스 내용: {news_content}
    
    [작성 조건]
    - 생성되는 텍스트는 순수한 일반 텍스트 형식이어야 하며, 어떠한 마크다운 문법(예: **, ## 등)도 사용하지 말아주세요.
    - 군더더기 표현(중복·불필요한 수식) 없이 중요한 사실만 요약해야 합니다.
    - 지나치게 축약하여 의미가 손실되지 않도록 유의해주세요.
    - 5줄 이내로 핵심만 간결하게 요약해주세요.
    """

    messages = [
        {
            "role": "system",
            "content": "당신은 야구 뉴스를 요약해서 정리해주는 도우미입니다."
        },
        {"role": "user", "content": prompt}
    ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )
    
    output = model.generate(
        input_ids.to(device),
        eos_token_id=tokenizer.eos_token_id,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7
    )

    # 전체 결과에서 "[|assistant|]" 이후의 텍스트만 추출
    result = tokenizer.decode(output[0], skip_special_tokens=True)
    if "[|assistant|]" in result:
        result = result.split("[|assistant|]")[-1].strip()
    return result
