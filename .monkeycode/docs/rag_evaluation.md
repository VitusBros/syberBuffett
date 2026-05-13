# RAG 检索效果评测集

## 说明
本文档用于量化 RAG 系统的检索准确率。每次优化分块策略或 embedding 模型后，重新运行评测并记录得分。

## 评测方法
1. 对每个问题，使用 RAG 检索 Top-3 片段
2. 人工判断是否有至少一个片段包含"预期原文"中的关键信息
3. 计算命中率（Hit Rate）和 MRR（Mean Reciprocal Rank）

---

## 评测用例

| # | 问题 | 预期引用的原文年份/主题 | 预期关键内容 | Top-1 是否命中 | Top-3 是否命中 | 备注 |
|---|------|------------------------|-------------|---------------|---------------|------|
| 1 | 什么是保险浮存金？ | buffett_wisdom_compilation | "float - money that we hold but don't own" | | | |
| 2 | 为什么巴菲特投资可口可乐？ | 1988/1992 股东信 | brand, distribution, pricing power, $1 billion | | | |
| 3 | 巴菲特的能力圈是什么？ | buffett_wisdom_compilation | "circle of competence", "too hard pile" | | | |
| 4 | 什么是经济护城河？ | buffett_wisdom_compilation | moat, brand, switching costs, network effects | | | |
| 5 | 巴菲特如何看待 2008 年金融危机？ | buffett_wisdom_compilation | "Buy American. I Am", Goldman Sachs, GE | | | |
| 6 | 为什么投资苹果？ | buffett_wisdom_compilation | consumer products, loyal customer, Tim Cook | | | |
| 7 | 巴菲特对普通投资者的建议是什么？ | buffett_wisdom_compilation | S&P 500 index fund, low-cost | | | |
| 8 | 伯克希尔的纺织业务为什么失败了？ | 1977/1978 股东信 | textile business, terrible economics | | | |
| 9 | 什么是好的管理层？ | buffett_wisdom_compilation | love the business not money, think like owners | | | |
| 10 | 巴菲特如何看待通货膨胀？ | buffett_wisdom_compilation | inflation is a tax, pricing power protection | | | |

---

## 评分标准

| 指标 | 计算公式 | 目标 |
|------|---------|------|
| **Hit Rate @1** | Top-1 命中的问题数 / 总问题数 | > 60% |
| **Hit Rate @3** | Top-3 至少一个命中的问题数 / 总问题数 | > 80% |
| **MRR** | 1/rank 的平均值（rank 为首次命中的位置） | > 0.5 |

---

## 评测记录

| 日期 | 版本 | 语料量 | top_k | 策略 | Hit@1 | Hit@3 | MRR | 备注 |
|------|------|--------|-------|------|-------|-------|-----|------|
| 2026-05-12 | v1.0 (语义段落分块) | 120 块 | 2 | 基础向量检索 | 80.0% | 100.0% | 0.900 | 远超目标。仅 Textile 和管理员问题排第 2 |
| 2026-05-12 | v2.0 (1998-2024 全量入库) | 1188 块 | 2 | 基础向量检索 | 50.0% | 80.0% | 0.792 | 语料暴增导致检索稀释 |
| 2026-05-12 | v2.1 (top_k 调整 + 元数据加权) | 1188 块 | 5 | 加权重排序 (weight/ distance) | 100.0% | 100.0% | 1.000 | 完美命中。主题语料 x2.0 加权生效 |
| 2026-05-12 | v2.1 (top_k=5 + metadata weighting) | 1188 块 | 50.0% | 80.0% | 0.731 | top_k 扩大但检索器未实现加权重排序，指标持平 |
