from abc import ABC, abstractmethod
from typing import List

class DomainPlugin(ABC):
    """基类：支持通用 DefaultPlugin 和特化子类"""
    
    def __init__(self, config: dict, persona: str, framework: str):
        self.config = config
        self.persona = persona
        self.framework = framework

    @abstractmethod
    def pre_flight_check(self, user_input: str, draft_response: str) -> List[str]:
        pass

    def build_system_prompt(self) -> str:
        return f"{self.persona}\n\n{self.framework}"


class DefaultPlugin(DomainPlugin):
    """通用插件：根据 skill.yaml 中的 constraints 配置自动校验硬规则"""
    
    def pre_flight_check(self, user_input: str, draft_response: str) -> List[str]:
        violations = []
        constraints = self.config.get('constraints', [])
        response_lower = draft_response.lower()
        input_lower = user_input.lower()
        
        for rule in constraints:
            rule_id = rule.get('id', 'unknown')
            description = rule.get('description', '')
            logic = rule.get('logic', 'OR')
            condition_input = [k.lower() for k in rule.get('condition_input', [])]
            forbidden_keywords = [k.lower() for k in rule.get('forbidden_keywords', [])]
            required_keywords = [k.lower() for k in rule.get('required_keywords', [])]
            
            # 检查输入是否命中条件（如果 condition_input 为空，则视为总是命中）
            input_matched = True
            if condition_input:
                input_matched = any(k in input_lower for k in condition_input)
            
            # 检查输出是否包含违禁词
            forbidden_matched = any(k in response_lower for k in forbidden_keywords) if forbidden_keywords else False
            
            # 检查输出是否包含必需词
            required_matched = all(k in response_lower for k in required_keywords) if required_keywords else True
            
            violates = False
            if logic.upper() == 'AND':
                violates = input_matched and forbidden_matched
            else:  # OR
                violates = forbidden_matched
            
            # 如果必需词缺失，也视为违规
            if not required_matched and required_keywords:
                violates = True
                description += f" (缺少必需词: {', '.join(required_keywords)})"
            
            if violates:
                violations.append(f"[{rule_id}] {description}")
        
        return violations
