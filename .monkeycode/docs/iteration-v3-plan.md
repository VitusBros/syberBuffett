# 电子巴菲特 v3.0 迭代优化计划

> 生成日期：2026-05-18  
> 当前版本：v2.1 (RAG Hit@1 100%, MRR 1.0)  
> 目标版本：v3.0 (语料增强 + 检索优化 + 工程化)

---

## 📊 当前状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 语料覆盖 | ✅ | 1977-2024 股东信完整入库 (1188 chunks) |
| RAG 性能 | ✅ | Hit@1 100%, MRR 1.0 (元数据加权生效) |
| LLM 集成 | ✅ | 商汤 SenseNova 已接入 |
| 中文本地化 | ✅ | Persona 完全汉化，去除模板味 |
| 跨会话记忆 | ✅ | JSON 文件持久化 |
| 用户反馈 | ❌ | 待实现 |
| 混合检索 | ❌ | 待实现 |
| 流式输出 | ❌ | 待实现 |

---

## 🔥 P0: 核心体验优化

### 任务 1: 语料增强 - 集成 AlphaBuffett 访谈录与 Essays 主题文章

**目标**：让巴菲特能回答更多概念性/对话性问题

| 子任务 | 说明 |
|--------|------|
| 1.1 下载 AlphaBuffett 数据集 | 编写脚本从 GitHub 仓库抓取 Q&A transcripts |
| 1.2 格式转换 | 转换为纯 TXT 格式，存入 `corpus/buffett/qa_transcripts/` |
| 1.3 下载 Essays 数据集 | 从官方来源获取主题文章 |
| 1.4 格式清理 | 存入 `corpus/buffett/essays/` |
| 1.5 改造 ingest_corpus.py | 支持多目录扫描，将新语料入库 |
| 1.6 完整入库验证 | 运行入库流程，验证新语料成功加入 ChromaDB |
| 1.7 更新文档 | 记录新增语料量到 `.monkeycode/docs/rag_evaluation.md` |

**预期结果**：语料量从 1188 chunks → 3000+ chunks

---

### 任务 2: 检索优化 - 实现 BM25 关键词 + 向量混合检索

**目标**：解决专有名词精确匹配问题（如 "Toll Bridge"、"Moat"）

| 子任务 | 说明 |
|--------|------|
| 2.1 安装 rank_bm25 | 添加到 `requirements.txt` |
| 2.2 创建 bm25_retriever.py | 实现基于关键词的 BM25 检索器 |
| 2.3 改造为 HybridRetriever | 融合向量检索和 BM25 结果 |
| 2.4 实现加权融合算法 | `final_score = alpha * vector_score + (1-alpha) * bm25_score`（默认 alpha=0.7） |
| 2.5 运行评测 | 验证混合检索的 Hit@1 和 MRR 指标 |

**预期结果**：专有名词命中率提升 30%+

---

### 任务 3: 用户反馈循环 - 在 Gradio UI 添加点赞/点踩按钮

**目标**：收集真实使用数据，指导后续优化

| 子任务 | 说明 |
|--------|------|
| 3.1 添加 UI 按钮 | 在每条 AI 回复下方添加 👍/👎 按钮组件 |
| 3.2 创建 feedback_collector.py | 接收用户反馈并记录到 JSON 文件 |
| 3.3 修改 memory_manager.py | 新增 `save_feedback()` 方法 |
| 3.4 实现反馈回调 | 点击按钮后保存数据并更新 UI 提示 |
| 3.5 创建分析脚本 | `scripts/analyze_feedback.py` 离线分析反馈数据 |

---

### 任务 4: 跨引擎重排序 - 引入 Cross-Encoder 二次排序

**目标**：提升检索质量，不依赖"加权 trick"

| 子任务 | 说明 |
|--------|------|
| 4.1 安装 sentence-transformers | 添加到 `requirements.txt` |
| 4.2 创建 cross_encoder_reranker.py | 封装 `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| 4.3 修改检索流程 | 先检索 N 候选 → Cross-Encoder 重排序 → 返回 Top-K |
| 4.4 模型缓存机制 | 避免每次请求都重新加载模型 |
| 4.5 运行评测验证 | Hit@1 稳定在 80%+ |
| 4.6 配置开关 | 在 `skill.yaml` 添加 `use_cross_encoder` 开关 |

---

## 🚀 P1: 功能扩展

### 任务 6: 多角色支持 - 实现 Skills 动态切换

| 子任务 | 说明 |
|--------|------|
| 6.1 添加角色选择器 | UI 下拉选择器，列出 `skills/` 目录下所有角色 |
| 6.2 动态调用 | 根据选择的角色动态调用对应的 SkillExecutor |
| 6.3 历史处理 | 角色切换时清空或保留聊天历史的选项 |
| 6.4 验证 Jobs 角色 | 测试芒格/Jobs 等角色可正常运行 |

---

### 任务 7: 长短期记忆分离 - 优化 MemoryManager

| 子任务 | 说明 |
|--------|------|
| 7.1 重构 memory_manager.py | 分离 session_memory.json 和 long_term_memory.json |
| 7.2 长期记忆结构 | 存储用户偏好、关注公司、投资风格标签 |
| 7.3 注入 System Prompt | 在 build_system_prompt 中注入长期记忆摘要 |
| 7.4 记忆压缩机制 | 对话超过 50 轮时自动摘要并归档 |
| 7.5 跨会话测试 | 关闭浏览器重新打开后仍能记住用户偏好 |

---

### 任务 8: 引用溯源 - 回答后自动标注来源

| 子任务 | 说明 |
|--------|------|
| 8.1 结构化返回数据 | modify retrieve 返回包含 source、year 等元数据 |
| 8.2 追加引用标注 | 在回复末尾显示：`📖 参考：1988 年股东信, 巴菲特智慧汇编` |
| 8.3 UI 折叠面板 | 将引用标注显示为可展开的面板 |

---

## 🎨 P1+: 体验升级

### 任务 10: 流式输出 - 实现打字机效果响应

| 子任务 | 说明 |
|--------|------|
| 10.1 修改 llm_client.py | 使用 `stream=True` 调用 SenseNova API |
| 10.2 创建 streaming_wrapper.py | 将流式输出转换为 Generator |
| 10.3 修改 skill_executor.py | 新增 `run_streaming()` 方法 |
| 10.4 修改 app.py | 使用 Gradio 的 `stream=True` 参数 |
| 10.5 性能测试 | 首字延迟 < 500ms |

---

## 🐳 P2: 工程化

### 任务 11: Docker 化部署

| 子任务 | 说明 |
|--------|------|
| 11.1 创建 Dockerfile | 基于 Python 3.10-slim 镜像 |
| 11.2 创建 docker-compose.yml | 定义 app、chromadb 两个服务 |
| 11.3 编写 .dockerignore | 排除不必要的文件 |
| 11.4 健康检查 | 确保 ChromaDB 就绪后再启动 app |
| 11.5 本地测试 | `docker compose up -d` |

---

### 任务 12: CI/CD 自动化评测

| 子任务 | 说明 |
|--------|------|
| 12.1 修改 evaluate_rag.py | 支持输出 JSON 格式结果 |
| 12.2 创建 GitHub Actions 工作流 | `.github/workflows/rag-eval.yml` |
| 12.3 配置自动评测 | 每次 PR 到 main 时自动运行 10 题 |
| 12.4 设置阈值 | Hit@1 < 70% 时标记 PR 为失败 |
| 12.5 结果注释 | 显示各版本指标对比到 PR 页面 |

---

## 📅 建议执行顺序

```
Phase 1 (本周): 语料增强(1) → 混合检索(2) → 用户反馈(3)
Phase 2 (下周): Cross-Encoder(4) → 多角色(6) → 记忆分离(7)
Phase 3 (下下周): 引用溯源(8) → 流式输出(10) → Docker化(11)
Phase 4 (持续): CI/CD(12)
```

## ⚠️ 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 商汤 API 成本超支 | 高 | 设置日限额，开发 Mock 模式用于本地调试 |
| 语料继续膨胀导致检索稀释 | 中 | 引入"语料权重"配置，动态调整主题优先级 |
| 中文语境下 LLM 表现下降 | 中 | 考虑切换到 Qwen/DeepSeek 等中文原生模型 |
| Cross-Encoder 模型加载慢 | 低 | 使用模型缓存，按需加载 |

---

## ✅ 验收标准

| 模块 | 验收标准 |
|------|----------|
| 语料增强 | RAG 能正确回答"如何看待 AI"、"什么是收费桥梁"等概念性问题 |
| 混合检索 | Hit@1 >= 80%, MRR >= 0.85 |
| 用户反馈 | 每条回答后可标记，数据可导出分析 |
| Cross-Encoder | 不依赖加权 trick，Hit@1 仍稳定在 80%+ |
| 多角色 | 可在 UI 切换角色，共享同一套 RAG/Memory 架构 |
| 记忆分离 | 跨会话仍能记住用户"喜欢价值投资"等偏好 |
| 引用溯源 | 每条回答带链接，可点击查看原文片段 |
| 流式输出 | 首字延迟 < 500ms |
| Docker 化 | 一键本地部署，包含 ChromaDB 持久化 |
| CI/CD | 每次 PR 自动跑 10 题评测，Hit@1 < 70% 则阻塞合并 |
