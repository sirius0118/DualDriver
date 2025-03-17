from __future__ import annotations

import bentoml
from annotated_types import Ge, Le
from typing_extensions import Annotated
import torch

MAX_TOKENS = 1024
PROMPT_TEMPLATE = """<s>[INST]
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.

{user_prompt} [/INST] """

# MODEL_ID = "facebook/opt-6.7b"


@bentoml.service(
    resources={"cpu": "80"},
    workers=1
)
class LLMServer:
    def __init__(self) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer  
        # device = "cuda" if torch.cuda.is_available() else "cpu"
        model_path = "./opt1.3b"  
        # model_path = "./opt350m"  
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device("cpu")

        # 输入样例  
        # text = "Hello, how are you today? "  

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)  # 假设分词器与模型兼容，这里直接使用了预训练的分词器  
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)  # 从本地加载模型  

    @bentoml.api
    def generate(self,
        prompt: str = "Explain superconductors like I'm five years old",
        max_tokens: Annotated[int, Ge(128), Le(MAX_TOKENS)] = MAX_TOKENS,
    ) -> torch.Tensor:
        # 准备输入文本  
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(input_ids, max_length=max_tokens, num_beams=1, early_stopping=True,no_repeat_ngram_size=2) 
        return outputs[0]
        # generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)  
        # return generated_text