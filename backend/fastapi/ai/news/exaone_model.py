# 기본 모델
# EXAONE-3.5-2.4B-Instruct 모델을 로드합니다.

'''
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

torch_dtype = torch.bfloat16 if device == "cuda" else torch.float32

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch_dtype,
    trust_remote_code=True,
    device_map="auto" if device == "cuda" else None
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
'''

# 양자화 모델
# EXAONE-3.5-2.4B-Instruct-AWQ 모델을 로드합니다.

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct-AWQ"
device = "cuda" if torch.cuda.is_available() else "cpu"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    trust_remote_code=True,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_name)