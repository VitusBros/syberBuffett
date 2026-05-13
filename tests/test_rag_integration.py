"""Test RAG integration with SkillExecutor."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.skill_executor import SkillExecutor

class VerboseMockLLM:
    """Mock LLM that prints the full prompt to show RAG context."""
    def generate(self, prompt: str) -> str:
        print("\n" + "="*60)
        print("📝 FULL PROMPT SENT TO LLM:")
        print("="*60)
        print(prompt)
        print("="*60)
        return "\n[模拟回复] 基于上述上下文，这是一笔好生意。我喜欢它的品牌护城河。"

if __name__ == "__main__":
    executor = SkillExecutor("/workspace", llm_client=VerboseMockLLM())
    
    # Test RAG retrieval
    print("🧪 Testing RAG with query: '可口可乐的护城河是什么？'")
    response = executor.run("buffett", "可口可乐的护城河是什么？")
    print("\n✅ Final Response:", response)
