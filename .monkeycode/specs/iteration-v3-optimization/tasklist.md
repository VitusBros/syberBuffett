# 电子巴菲特 v3.0 迭代优化 - 实施计划

- [ ] 1. 语料增强 - 集成 AlphaBuffett 访谈录与 Essays 主题文章
  - [ ] 1.1 下载并整理 AlphaBuffett (Q&A transcripts) 数据集到 `corpus/buffett/qa_transcripts/`
  - [ ] 1.2 编写 `scripts/download_alpha_buffett.py` 从 GitHub 仓库抓取并转换为 TXT 格式
  - [ ] 1.3 下载并整理 Essays (Thematic articles) 数据集到 `corpus/buffett/essays/`
  - [ ] 1.4 编写 `scripts/download_essays.py` 从官方来源获取并清理格式
  - [ ] 1.5 修改 `scripts/ingest_corpus.py` 支持多目录扫描，将新语料入库
  - [ ] 1.6 运行完整入库流程，验证新语料成功加入 ChromaDB
  - [ ] 1.7 更新 `.monkeycode/docs/rag_evaluation.md` 记录新增语料量

- [ ] 2. 检索优化 - 实现 BM25 关键词 + 向量混合检索
  - [ ] 2.1 安装 `rank_bm25` 依赖，添加到 `requirements.txt`
  - [ ] 2.2 创建 `engine/bm25_retriever.py`，实现基于关键词的 BM25 检索器
  - [ ] 2.3 改造 `engine/rag_retriever.py` 为 HybridRetriever，融合向量检索和 BM25 结果
  - [ ] 2.4 实现加权融合算法：`final_score = alpha * vector_score + (1-alpha) * bm25_score`（默认 alpha=0.7）
  - [ ] 2.5 运行 `scripts/evaluate_rag.py` 验证混合检索的 Hit@1 和 MRR 指标

- [ ] 3. 用户反馈循环 - 在 Gradio UI 添加点赞/点踩按钮
  - [ ] 3.1 修改 `app.py` 聊天界面，在每条 AI 回复下方添加 👍/👎 按钮组件
  - [ ] 3.2 创建 `engine/feedback_collector.py`，接收用户反馈并记录到 JSON 文件
  - [ ] 3.3 修改 `engine/memory_manager.py` 新增 `save_feedback()` 方法，关联反馈到对话记录
  - [ ] 3.4 在 `app.py` 实现反馈回调函数，点击按钮后保存数据并更新 UI 提示
  - [ ] 3.5 创建 `scripts/analyze_feedback.py` 脚本，用于离线分析反馈数据统计

- [ ] 4. 跨引擎重排序 - 引入 Cross-Encoder 二次排序
  - [ ] 4.1 安装 `sentence-transformers` 依赖到 `requirements.txt`
  - [ ] 4.2 创建 `engine/cross_encoder_reranker.py`，封装 `cross-encoder/ms-marco-MiniLM-L-6-v2` 模型
  - [ ] 4.3 修改 `engine/rag_retriever.py` 的 retrieve 流程：先检索 N 个候选 → Cross-Encoder 重排序 → 返回 Top-K
  - [ ] 4.4 实现模型缓存机制，避免每次请求都重新加载模型
  - [ ] 4.5 运行评测脚本验证重排序后的 Hit@1 是否稳定在 80%+（不依赖加权 trick）
  - [ ] 4.6 添加配置开关 `use_cross_encoder` 到 `skill.yaml`，支持按需启用/禁用

- [ ] 5. 检查点 - 验证语料增强和检索优化
  - 确保新语料成功入库且 RAG 评测 Hit@1 >= 80%
  - 确认混合检索和 Cross-Encoder 重排序均正常工作
  - 验证用户反馈按钮在 Gradio UI 中可正常点击并记录数据

- [ ] 6. 多角色支持 - 实现 Skills 动态切换
  - [ ] 6.1 修改 `app.py` 添加角色下拉选择器组件，列出 `skills/` 目录下的所有可用角色
  - [ ] 6.2 修改 `app.py` 的聊天处理函数，根据选择的角色动态调用对应的 SkillExecutor
  - [ ] 6.3 实现角色切换时清空聊天历史或保留历史的选项
  - [ ] 6.4 验证 Jobs 角色可正常加载并回答产品相关问题

- [ ] 7. 长短期记忆分离 - 优化 MemoryManager
  - [ ] 7.1 重构 `engine/memory_manager.py`，分离 session_memory.json 和 long_term_memory.json
  - [ ] 7.2 实现长期记忆结构：存储用户偏好、关注公司、投资风格标签
  - [ ] 7.3 修改 `build_system_prompt` 注入长期记忆摘要到 System Prompt
  - [ ] 7.4 实现记忆压缩机制：对话超过 50 轮时自动摘要并归档到长期记忆
  - [ ] 7.5 测试跨会话记忆连续性（关闭浏览器重新打开后仍能记住用户偏好）

- [ ] 8. 引用溯源 - 回答后自动标注来源
  - [ ] 8.1 修改 `engine/rag_retriever.py` 的 retrieve 返回结构化数据（包含 source、year 等元数据）
  - [ ] 8.2 修改 `engine/skill_executor.py` 在最终回复末尾追加引用标注，格式：`📖 参考：1988 年股东信, 巴菲特智慧汇编`
  - [ ] 8.3 修改 `app.py` 的 UI 渲染，将引用标注显示为可展开的折叠面板
  - [ ] 8.4 实现点击查看原文片段的功能（可选，后续迭代）

- [ ] 9. 检查点 - 验证多角色和记忆系统
  - 确保角色切换功能正常且各自记忆独立
  - 验证长期记忆在跨会话中正确加载
  - 确认引用标注准确显示对应的 RAG 来源

- [ ] 10. 流式输出 - 实现打字机效果响应
  - [ ] 10.1 修改 `engine/llm_client.py`，使用 `stream=True` 调用 SenseNova API
  - [ ] 10.2 创建 `engine/streaming_wrapper.py` 将 LLM 流式输出转换为 Generator
  - [ ] 10.3 修改 `engine/skill_executor.py` 新增 `run_streaming()` 方法，支持逐块返回响应
  - [ ] 10.4 修改 `app.py` 使用 Gradio 的 `stream=True` 参数实现打字机效果
  - [ ] 10.5 测试首字延迟 < 500ms，完整响应流畅无卡顿

- [ ] 11. Docker 化部署 - 编写容器化配置文件
  - [ ] 11.1 创建 `Dockerfile`，基于 Python 3.10-slim 镜像构建
  - [ ] 11.2 创建 `docker-compose.yml`，定义 app、chromadb 两个服务
  - [ ] 11.3 编写 `.dockerignore` 排除不必要的文件（node_modules、.git 等）
  - [ ] 11.4 添加健康检查配置，确保 ChromaDB 就绪后再启动 app
  - [ ] 11.5 测试本地 Docker 一键部署：`docker compose up -d`

- [ ] 12. 自动化评测 - CI/CD 集成 RAG 评测
  - [ ] 12.1 修改 `scripts/evaluate_rag.py` 支持输出 JSON 格式结果，方便 CI 解析
  - [ ] 12.2 创建 `.github/workflows/rag-eval.yml` GitHub Actions 工作流
  - [ ] 12.3 配置工作流：每次 PR 到 main 时自动运行 10 题评测
  - [ ] 12.4 设置阈值：Hit@1 < 70% 时标记 PR 为失败
  - [ ] 12.5 添加评测结果注释到 PR 页面，显示各版本指标对比
