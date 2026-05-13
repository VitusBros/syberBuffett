import sys
import os
import importlib
# Add workspace root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.skill_loader import SkillLoader
from engine.domain_plugin import DefaultPlugin, DomainPlugin

# Lazy imports
from engine.rag_retriever import RAGRetriever
from engine.memory_manager import MemoryManager
from engine.llm_client import SenseNovaLLM

_rag_retriever_cls = None
_memory_manager_cls = None

def _get_rag_retriever_class():
    global _rag_retriever_cls
    if _rag_retriever_cls is None:
        from engine.rag_retriever import RAGRetriever
        _rag_retriever_cls = RAGRetriever
    return _rag_retriever_cls

def _get_memory_manager_class():
    global _memory_manager_cls
    if _memory_manager_cls is None:
        from engine.memory_manager import MemoryManager
        _memory_manager_cls = MemoryManager
    return _memory_manager_cls

class MockLLM:
    """Simulates an LLM response for testing purposes."""
    def generate(self, prompt: str) -> str:
        return "[模拟 LLM 回复]: 这是一个基于设定生成的回答..."

class SkillExecutor:
    """
    Orchestrates the Skill execution flow:
    Loader -> Plugin -> Prompt -> LLM -> Validation -> Output
    """
    
    def __init__(self, base_dir: str, llm_client=None):
        self.loader = SkillLoader(base_dir)
        if llm_client:
            self.llm = llm_client
        elif os.getenv("SENSENOVA_API_KEY"):
            self.llm = SenseNovaLLM()
            print("✅ Initialized SenseNova LLM")
        else:
            self.llm = MockLLM()
            print("⚠️ SENSENOVA_API_KEY not set, using Mock LLM")

    def _instantiate_plugin(self, role_name: str, data: dict) -> DomainPlugin:
        """Factory method: Try to load specific plugin, fallback to DefaultPlugin."""
        try:
            # Construct module name: plugins.{role}_plugin
            module_name = f"plugins.{role_name}_plugin"
            # Class name convention: {RoleName}Plugin (e.g., BuffettPlugin)
            class_name = f"{role_name.capitalize()}Plugin"
            
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            print(f"Loaded specialized plugin: {class_name}")
            return plugin_class(data['config'], data['persona'], data['framework'])
        except (ImportError, AttributeError):
            print(f"No specialized plugin found. Using DefaultPlugin for '{role_name}'.")
            return DefaultPlugin(data['config'], data['persona'], data['framework'])

    def run(self, role_name: str, user_input: str) -> str:
        print(f"\n--- Executing Role: {role_name} ---")
        
        # 1. Load Role Data
        data = self.loader.load_role(role_name)
        
        # 2. Instantiate Plugin
        plugin = self._instantiate_plugin(role_name, data)
        
        # 3. Build System Prompt
        system_prompt = plugin.build_system_prompt()
        
        # 4. Memory Context (if enabled)
        memory_context = ""
        memory_config = data['config'].get('memory', {})
        memory_manager = None
        if memory_config.get('enabled'):
            MemoryManager = _get_memory_manager_class()
            session_id = memory_config.get('session_id', 'default')
            memory_manager = MemoryManager(
                memory_dir=memory_config.get('dir', './memory_data'),
                session_id=session_id
            )
            memory_context = memory_manager.get_context_summary(
                max_turns=memory_config.get('max_history_turns', 3)
            )
            if memory_context:
                print(f"🧠 Memory enabled, loaded history for session: {session_id}")
            else:
                print("🧠 Memory enabled, but this is the first conversation.")
        
        # 5. RAG Retrieval (if enabled)
        rag_context = ""
        rag_config = data['config'].get('rag', {})
        if rag_config.get('enabled'):
            print(f"🔍 RAG enabled, retrieving context for: {user_input[:30]}...")
            RAGRetriever = _get_rag_retriever_class()
            retriever = RAGRetriever(
                db_path=rag_config.get('db_path', './chroma_data'),
                collection_name=rag_config.get('index', 'default')
            )
            rag_context = retriever.retrieve(user_input, top_k=rag_config.get('top_k', 3))
            if rag_context:
                print(f"📄 Retrieved {len(rag_context)} chars of context")
        
        # 6. Assemble Full Prompt
        prompt_parts = [system_prompt]
        
        if memory_context:
            prompt_parts.append(f"## 历史记忆\n{memory_context}")
        if rag_context:
            prompt_parts.append(f"## 参考上下文\n{rag_context}")
        
        prompt_parts.append(f"## 用户问题\n{user_input}")
        full_prompt = "\n\n".join(prompt_parts)
        
        # 7. Call LLM
        print(f"Sending to LLM...")
        response = self.llm.generate(full_prompt)
        
        # 8. Hard Rules Validation
        violations = plugin.pre_flight_check(user_input, response)
        if violations:
            warning = f"\n\n[⚠️ System Warning: Response may violate principles]\n"
            warning += "\n".join([f"- {v}" for v in violations])
            response = response + warning
        
        # 9. Save to Memory (if enabled)
        if memory_manager:
            memory_manager.add_conversation(user_input, response)
            memory_manager.extract_mentioned_entities(user_input)
            print("💾 Conversation saved to memory")
        
        return response

if __name__ == "__main__":
    executor = SkillExecutor("/workspace")
    
    # Test Case 1: Buffett (Should use DefaultPlugin as buffett_plugin.py doesn't exist now or we can keep it)
    # Note: We removed buffett_plugin.py conceptually in the refactor, but let's see if it falls back correctly.
    # Actually, let's test a violation case.
    
    print("=== Test 1: Fallback to DefaultPlugin ===")
    # To test DefaultPlugin properly without a real LLM, we can mock the response inside the executor 
    # or just test the plugin check directly.
    # Let's test directly.
    
    data = executor.loader.load_role("buffett")
    plugin = DefaultPlugin(data['config'], data['persona'], data['framework'])
    
    bad_resp = "我觉得电网设备公司就是收费桥梁。"
    print(f"Input: 分析一下电网设备公司")
    print(f"Response: {bad_resp}")
    errors = plugin.pre_flight_check("分析一下电网设备公司", bad_resp)
    print(f"Result: {errors if errors else 'PASS'}")

    print("\n=== Test 2: Violation - Macro Prediction ===")
    bad_resp2 = "我认为大盘有 50% 的概率回撤。"
    print(f"Response: {bad_resp2}")
    errors2 = plugin.pre_flight_check("美股走势", bad_resp2)
    print(f"Result: {errors2 if errors2 else 'PASS'}")
    
    print("\n=== Test 3: Violation - Cash Explanation ===")
    bad_resp3 = "我们持有现金是因为看空市场。"
    print(f"Response: {bad_resp3}")
    errors3 = plugin.pre_flight_check("为什么持有那么多现金", bad_resp3)
    print(f"Result: {errors3 if errors3 else 'PASS'}")
