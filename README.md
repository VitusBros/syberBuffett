# 电子巴菲特 AI 投资顾问

基于 **Skill + RAG + Memory** 架构的 AI 投资顾问应用。

## 📖 项目简介

"电子巴菲特"是一个基于 Warren Buffett 投资理念的 AI 对话系统。它通过检索增强生成 (RAG) 技术，学习了巴菲特 1977-2024 年的股东信、访谈和主题文章，能够以巴菲特的口吻回答关于价值投资、公司分析、市场观点等问题。

## ✨ 核心特性

- **RAG 知识库**: 涵盖 1977-2024 年完整股东信及相关访谈录，持续更新中。
- **记忆系统**: 支持跨会话记忆，记住用户的关注公司和投资偏好。
- **硬规则约束**: 严格遵循巴菲特投资原则（不预测宏观市场、不投资看不懂的生意等）。
- **中文本地化**: 针对中文用户优化，提供地道的大白话投资解释。

## 🛠️ 技术架构

- **LLM**: 商汤科技 SenseNova (6.7 Flash-Lite)
- **向量数据库**: ChromaDB
- **前端**: Gradio
- **部署**: 支持 Hugging Face Spaces / ModelScope 魔搭社区

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YourUsername/syberBuffett.git
cd syberBuffett
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

在项目根目录创建 `.env` 文件（不要提交到 Git）：

```bash
SENSENOVA_API_KEY=sk-your-key-here
```

### 4. 启动应用

```bash
python app.py
```

## 📊 当前状态

- **语料覆盖**: 1977-2024 股东信
- **检索性能**: Hit@1 100%, MRR 1.0
- **语言**: 简体中文

## 📝 许可证

MIT
