"""Test Memory integration with SkillExecutor."""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Clean up test memory before run
test_memory_dir = "./test_memory_data"
if os.path.exists(test_memory_dir):
    import shutil
    shutil.rmtree(test_memory_dir)

from engine.skill_executor import SkillExecutor

class VerboseMockLLM:
    """Mock LLM that shows the prompt."""
    def generate(self, prompt: str) -> str:
        # Extract just the user question and memory part for display
        if "## 历史记忆" in prompt:
            mem_start = prompt.index("## 历史记忆")
            mem_section = prompt[mem_start:mem_start+300]
            print(f"\n📝 Memory Context injected:\n{mem_section}...")
        return "这是基于记忆和历史对话的回复。"

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Phase 3.5: 轻量记忆集成测试")
    print("=" * 60)
    
    executor = SkillExecutor("/workspace", llm_client=VerboseMockLLM())
    
    # 更新测试用的 skill.yaml 指向测试目录
    import yaml
    config_path = "/workspace/skills/buffett/skill.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    config['memory']['dir'] = test_memory_dir
    config['memory']['session_id'] = 'test_user_001'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)
    
    print("\n--- 第一轮对话 (首次) ---")
    resp1 = executor.run("buffett", "你怎么看比亚迪？")
    print(f"回复: {resp1}")
    
    print("\n--- 第二轮对话 (带记忆) ---")
    resp2 = executor.run("buffett", "那可口可乐呢？")
    print(f"回复: {resp2}")
    
    print("\n--- 第三轮对话 (更多记忆) ---")
    resp3 = executor.run("buffett", "回到我们之前说的比亚迪，它的护城河还在吗？")
    print(f"回复: {resp3}")
    
    # 验证记忆文件
    print("\n--- 验证记忆文件内容 ---")
    mem_file = os.path.join(test_memory_dir, "test_user_001.json")
    if os.path.exists(mem_file):
        with open(mem_file, 'r', encoding='utf-8') as f:
            mem_data = json.load(f)
        print(f"会话 ID: {mem_data['session_id']}")
        print(f"对话轮数: {len(mem_data['conversations'])}")
        print(f"提及公司: {mem_data['mentioned_companies']}")
        print(f"创建时间: {mem_data['created_at']}")
        print(f"最后更新: {mem_data['updated_at']}")
    
    # 恢复原始配置
    config['memory']['dir'] = './memory_data'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)
    
    print("\n✅ 记忆集成测试完成!")
