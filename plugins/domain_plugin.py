from abc import ABC, abstractmethod
from pathlib import Path

class DomainPlugin(ABC):
    """
    Abstract Base Class for Domain Plugins.
    
    Every character type (e.g., Investor, Innovator, Artist) should implement
    a specific plugin that defines how they analyze problems.
    """
    
    @property
    @abstractmethod
    def framework_file(self) -> str:
        """The filename of the domain framework (e.g., investment_framework.md)"""
        pass

    @abstractmethod
    def analyze_input(self, user_query: str, framework_content: str, persona_content: str) -> str:
        """
        Analyzes the user input based on the role's specific framework.
        
        Args:
            user_query: The user's question.
            framework_content: The content of the domain framework file.
            persona_content: The content of the persona file.
            
        Returns:
            A structured analysis result (or the generated response).
        """
        pass

# Example Implementation (Conceptual)
class InvestmentPlugin(DomainPlugin):
    @property
    def framework_file(self) -> str:
        return "investment_framework.md"

    def analyze_input(self, user_query: str, framework_content: str, persona_content: str) -> str:
        # Logic: Check against Circle of Competence, Moat, etc.
        return f"Analyzing '{user_query}' using Investment Framework..."

class ProductPlugin(DomainPlugin):
    @property
    def framework_file(self) -> str:
        return "product_framework.md"

    def analyze_input(self, user_query: str, framework_content: str, persona_content: str) -> str:
        # Logic: Check against UX, Simplicity, 10x Improvement
        return f"Analyzing '{user_query}' using Product Innovation Framework..."
