# 如何添加新角色 (How to Add a New Role)

只需 3 个文件，即可为你的“数字生命”添加一个新角色。无需编写 Python 代码。

## 步骤 1: 创建角色目录
在 `skills/` 目录下创建以角色英文名命名的文件夹，例如 `lu_xun/`。
```bash
mkdir -p skills/lu_xun
```

## 步骤 2: 编写 `skill.yaml` (配置文件)
这是角色的“身份证”和规则引擎。
```yaml
# skills/lu_xun/skill.yaml
name: "鲁迅文学助手"
type: "celebrity"
version: "1.0.0"
files:
  persona: "persona.md"
  framework: "writing_style.md"
# 可选：定义硬规则校验
constraints:
  - id: "no_modern_slang"
    description: "禁止使用现代网络流行语"
    forbidden_keywords: ["YYDS", "绝绝子", "emo", "躺平"]
    logic: "OR"
  - id: "must_use_metaphor"
    description: "批判时必须使用比喻（投枪/匕首）"
    condition_input: ["批评", "讽刺", "criticize"]
    forbidden_keywords: []
    required_keywords: ["投枪", "匕首", "鲜血", "黑暗"]
    logic: "AND"
```

## 步骤 3: 编写 `persona.md` (六层人格画像)
按照通用模板填写具体内容。
```markdown
# Persona: 鲁迅

## Layer 1: Hard Rules (Principles)
- 绝不妥协于黑暗。
- 哀其不幸，怒其不争。

## Layer 2: Identity
- 我是民族的脊梁，而非取悦看客的小丑。

... (填写其他层级)
```

## 步骤 4: 编写领域框架文件
例如 `writing_style.md`，定义该角色在特定领域的分析逻辑。
```markdown
# 鲁迅写作风格
...
```

## 步骤 5: 测试
运行 `SkillExecutor` 测试新角色：
```python
from engine.skill_executor import SkillExecutor
executor = SkillExecutor("/workspace")
resp = executor.run("lu_xun", "你怎么看现在的年轻人")
print(resp)
```

完成！你现在拥有了一个全新的数字人格。
