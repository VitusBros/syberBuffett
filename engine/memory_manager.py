"""
Lightweight Memory Manager.
Persists user conversation history as JSON files for cross-session memory.
"""
import json
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    轻量级跨会话记忆管理器
    
    每个用户（或会话）对应一个 JSON 文件，记录：
    - 历史对话摘要
    - 提及的公司/行业
    - 用户偏好
    """
    
    def __init__(self, memory_dir: str = "./memory_data", session_id: str = "default"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id
        self.memory_file = self.memory_dir / f"{session_id}.json"
        self.memory = self._load_memory()
    
    def _load_memory(self) -> dict:
        """加载记忆文件，不存在则创建"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "conversations": [],
            "mentioned_companies": [],
            "user_preferences": {},
            "key_insights": []
        }
    
    def save(self):
        """持久化记忆到磁盘"""
        self.memory["updated_at"] = datetime.now().isoformat()
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
        logger.info(f"Memory saved for session: {self.session_id}")
    
    def add_conversation(self, user_input: str, ai_response: str):
        """添加一轮对话记录"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response_summary": ai_response[:200]  # 只存摘要
        }
        self.memory["conversations"].append(entry)
        
        # 限制历史记录数量（保留最近 20 轮）
        if len(self.memory["conversations"]) > 20:
            self.memory["conversations"] = self.memory["conversations"][-20:]
        
        self.save()
    
    def extract_mentioned_entities(self, text: str):
        """简单提取提及的公司名（可扩展为 NER）"""
        # 这里使用简单的关键词匹配，后续可接入 NLP
        common_companies = [
            "比亚迪", "可口可乐", "苹果", "Amazon", "Tesla", "Google", 
            "Microsoft", "Meta", "Netflix", "Berkshire", "伯克希尔",
            "中国石油", "中国电网", "英伟达", "NVIDIA"
        ]
        for company in common_companies:
            if company in text and company not in self.memory["mentioned_companies"]:
                self.memory["mentioned_companies"].append(company)
        self.save()
    
    def get_context_summary(self, max_turns: int = 3) -> str:
        """
        获取历史记忆摘要，注入到 prompt 中
        
        Returns:
            格式化的记忆上下文字符串
        """
        parts = []
        
        # 1. 最近对话摘要
        recent_convs = self.memory["conversations"][-max_turns:]
        if recent_convs:
            conv_parts = []
            for conv in recent_convs:
                ts = conv["timestamp"][:16]  # 只保留到分钟
                conv_parts.append(f"[{ts}] 用户: {conv['user_input']}")
                conv_parts.append(f"[{ts}] AI: {conv['ai_response_summary']}...")
            parts.append("## 最近对话历史\n" + "\n".join(conv_parts))
        
        # 2. 提及过的公司
        if self.memory["mentioned_companies"]:
            companies = ", ".join(self.memory["mentioned_companies"])
            parts.append(f"## 用户关注过的公司\n{companies}")
        
        # 3. 用户偏好
        if self.memory["user_preferences"]:
            prefs = json.dumps(self.memory["user_preferences"], ensure_ascii=False)
            parts.append(f"## 用户偏好\n{prefs}")
        
        if not parts:
            return ""
        
        return "\n\n".join(parts)
    
    def is_first_conversation(self) -> bool:
        """判断是否是首次对话"""
        return len(self.memory["conversations"]) == 0
    
    def get_greeting_with_memory(self) -> str:
        """根据记忆生成个性化问候"""
        if self.is_first_conversation():
            return "你好！我是巴菲特投资顾问，有什么可以帮你的？"
        
        companies = self.memory["mentioned_companies"]
        if companies:
            last_company = companies[-1]
            return f"你好！很高兴再次和你聊天。上次我们聊到了 {last_company}，今天想继续探讨什么？"
        return "你好！很高兴再次和你聊天，今天想探讨什么投资话题？"
