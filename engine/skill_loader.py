import os
import sys
import re
import logging
from pathlib import Path
import yaml

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class SkillLoader:
    """
    Dynamic Skill Loader.
    Reads skill.yaml configuration to load precise files.
    Falls back to SKILL.md frontmatter if skill.yaml is missing.
    """

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.skills_dir = self.base_dir / "skills"

    def list_roles(self) -> list[str]:
        if not self.skills_dir.exists():
            return []
        # A role is a directory containing at least persona.md or SKILL.md/skill.yaml
        return [
            d.name for d in self.skills_dir.iterdir()
            if d.is_dir()
        ]

    def load_role(self, role_name: str) -> dict:
        role_dir = self.skills_dir / role_name
        if not role_dir.exists():
            raise FileNotFoundError(f"Role directory '{role_name}' not found")
        
        # 1. Load Configuration (Try YAML first, then fallback to Frontmatter)
        config_path = role_dir / "skill.yaml"
        if config_path.exists():
            logger.info(f"Loading config from skill.yaml for '{role_name}'")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            logger.warning(f"skill.yaml not found for '{role_name}', falling back to SKILL.md frontmatter")
            skill_md_path = role_dir / "SKILL.md"
            if not skill_md_path.exists():
                raise FileNotFoundError(f"Neither skill.yaml nor SKILL.md found for '{role_name}'")
            config = self._parse_frontmatter(skill_md_path.read_text(encoding='utf-8'))
        
        files_config = config.get('files', {})
        
        # 2. Load Persona
        persona_filename = files_config.get('persona', 'persona.md')
        persona_path = role_dir / persona_filename
        if not persona_path.exists():
            raise FileNotFoundError(f"Persona file '{persona_filename}' not found for role '{role_name}'")
        persona_content = persona_path.read_text(encoding='utf-8')

        # 3. Load Framework
        framework_filename = files_config.get('framework')
        framework_content = ""
        if framework_filename:
            framework_path = role_dir / framework_filename
            if not framework_path.exists():
                raise FileNotFoundError(f"Framework file '{framework_filename}' not found for role '{role_name}'")
            framework_content = framework_path.read_text(encoding='utf-8')

        return {
            "config": config,
            "persona": persona_content,
            "framework": framework_content,
            "role_dir": str(role_dir)
        }

    def _parse_frontmatter(self, content: str) -> dict:
        """Parses YAML frontmatter from markdown content."""
        if content.startswith("---"):
            match = re.search(r"^---(.*?)---", content, re.DOTALL)
            if match:
                yaml_block = match.group(1).strip()
                return yaml.safe_load(yaml_block) or {}
        return {}

if __name__ == "__main__":
    loader = SkillLoader("/workspace")
    print("Available Roles:", loader.list_roles())
    
    print("\n--- Loading Buffett ---")
    buffett = loader.load_role("buffett")
    print(f"Name: {buffett['config']['name']}")
    print(f"Framework: {buffett['config']['files']['framework']}")
