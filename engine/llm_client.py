import os
from openai import OpenAI

class SenseNovaLLM:
    """LLM Client for SenseNova (商汤科技) via OpenAI compatible interface."""
    
    def __init__(self, model: str = "sensenova-6.7-flash-lite"):
        api_key = os.getenv("SENSENOVA_API_KEY")
        if not api_key:
            raise ValueError("SENSENOVA_API_KEY environment variable not set")
            
        self.client = OpenAI(
            base_url="https://token.sensenova.cn/v1",
            api_key=api_key,
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generates a response from the SenseNova LLM.
        
        Args:
            prompt: The full system + user prompt to send.
            
        Returns:
            The generated text content.
        """
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            if resp.choices:
                return resp.choices[0].message.content
            return "[错误]: LLM 未返回内容"
        except Exception as e:
            return f"[错误]: LLM 调用失败 - {str(e)}"
