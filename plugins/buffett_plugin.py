from engine.domain_plugin import DomainPlugin
import re

class BuffettPlugin(DomainPlugin):
    """
    Concrete Plugin for Warren Buffett Role.
    Implements strict investment logic checks.
    """
    
    def pre_flight_check(self, user_input: str, draft_response: str) -> list[str]:
        violations = []
        
        # Normalize text for checking
        text_lower = draft_response.lower()
        
        # Rule 1: No Macro Prediction (Probabilities, Crash forecasts)
        prediction_keywords = [
            "概率", "回撤", "下跌空间", "跌到", "涨到", "点位", 
            "probability", "crash is coming", "market will drop"
        ]
        
        # Simple context check: "下跌" is okay if saying "I don't know if it will drop"
        # But "下跌空间" (downside space) implies prediction.
        # Let's look for strong prediction phrases.
        if any(k in text_lower for k in ["概率", "回撤", "下跌空间"]):
             violations.append("Violated Rule: No Macro Prediction (Specific terms used)")
        
        # Rule 2: Toll Bridge vs Supplier (Grid Equipment case)
        # Check if user asked about Grid Equipment and response mentions Toll Bridge
        if ("电网设备" in user_input or "grid equipment" in user_input.lower()):
            if "收费桥梁" in draft_response or "toll bridge" in draft_response.lower():
                violations.append("Violated Rule: Misused Toll Bridge metaphor for Supplier")

        # Rule 3: Cash Position (Don't say "Market too expensive" as primary reason)
        # This is harder to regex perfectly, but we can flag explicit phrases.
        if "cash" in text_lower and "too expensive" in text_lower:
             # Check context: if it says "The market is too expensive, so we hold cash" -> Violation
             # A simple regex could catch this.
             pattern = r"market.*too expensive.*cash|cash.*market.*too expensive"
             if re.search(pattern, text_lower):
                 violations.append("Violated Rule: Cash Position Reason (Attributed to market expensiveness)")

        return violations

    def build_system_prompt(self) -> str:
        # Append Buffett-specific instruction to ensure tone
        base_prompt = super().build_system_prompt()
        return f"{base_prompt}\n\n[Instruction]: Speak in first person ('I', 'We'). Use simple analogies. Be honest about 'Too Hard' pile."
