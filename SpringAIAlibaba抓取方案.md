# Spring AI Alibaba 技能抓取指南

创建专业的 Spring AI + Spring AI Alibaba 技能，让 Claude AI 成为你的 Spring AI 开发助手。

**适用工具**: Skill Seekers v2.0.0
**总用时**: 5-60 分钟（分阶段进行，按需选择）

---

## 快速开始（5分钟立即可用）

如果你想要立即开始使用 Spring AI，只需运行：

```bash
# 1. 设置 GitHub Token（必须）
set GITHUB_TOKEN=your_github_token_here

# 2. 快速抓取（3-5分钟）
skill-seekers unified --config configs/spring_ai_starter.json

# 3. 打包上传
skill-seekers package output/spring-ai-starter/
```

**完成！** 5分钟后你就有了一个可用的 Spring AI 开发技能。

---

## 三种抓取方案

根据你的需求选择合适的方案：

### 🚀 方案1：快速入门（推荐新手）

**适用场景**: 刚开始学习 Spring AI，需要基础概念和示例
**用时**: 5 分钟
**内容**: 入门教程 + 基础示例 + 通义千问集成

```bash
# 前置条件：设置 GitHub Token
set GITHUB_TOKEN=your_github_token_here

# 执行抓取
skill-seekers unified --config configs/spring_ai_starter.json

# 增强（可选）
skill-seekers enhance output/spring-ai-starter/

# 打包
skill-seekers package output/spring-ai-starter/

# 上传：访问 https://claude.ai/skills 上传生成的 .zip 文件
```

### 🔧 方案2：完整框架（适合有经验开发者）

**适用场景**: 需要深入了解 Spring AI 底层原理和高级特性
**用时**: 20 分钟
**内容**: 完整官方文档 + 源码分析 + 高级特性

```bash
# 前置条件：确保 GitHub Token 有效
echo %GITHUB_TOKEN%

# 执行抓取
skill-seekers unified --config configs/spring_ai_official.json

# 增强
skill-seekers enhance output/spring-ai-official/

# 打包
skill-seekers package output/spring-ai-official/
```

### 🏢 方案3：完整生态（企业级开发）

**适用场景**: 需要使用阿里云集成、Agent框架等企业级功能
**用时**: 60 分钟
**内容**: 阿里巴巴完整生态 + 管理控制台 + 扩展功能

```bash
# 执行抓取
skill-seekers unified --config configs/spring_ai_alibaba.json

# 增强
skill-seekers enhance output/spring-ai-alibaba/

# 打包
skill-seekers package output/spring-ai-alibaba/
```

---

## 验证技能质量

抓取完成后，在 Claude 中测试：

**基础测试**:
- "如何用 Spring AI Alibaba 调用通义千问？"
- "给我一个 Spring AI 聊天机器人的完整示例"
- "Spring AI 的 ChatClient 怎么配置？"

**进阶测试**:
- "Spring AI 的 ChatClient 内部是如何实现的？"
- "如何自定义一个新的 AI 模型适配器？"
- "Spring AI 的 Function Calling 机制是什么？"

**企业级测试**:
- "Spring AI Alibaba 的 Agent Framework 怎么使用？"
- "如何配置通义千问的不同模型版本？"
- "Spring AI Alibaba 与官方 Spring AI 的主要区别？"

---

## 常见问题

**Q: 抓取失败怎么办？**
1. 检查 GitHub Token: `echo %GITHUB_TOKEN%`
2. 确保网络连接正常
3. 查看错误日志: `skill-seekers unified --config configs/spring_ai_starter.json 2>&1 | tee debug.log`

**Q: 可以只运行快速入门方案吗？**
A: 可以！方案1已经满足大部分开发需求。

**Q: 什么时候需要更新？**
- Spring AI 发布重大版本时
- Spring AI Alibaba 添加新模型支持时
- 技能无法回答新问题时

**Q: 如何更新技能？**
```bash
# 删除旧数据，重新抓取
rm -rf output/spring-ai-*
skill-seekers unified --config configs/spring_ai_starter.json
```

---

## 方案对比

| 方案 | 用时 | 适用场景 | 包含内容 |
|-----|------|----------|----------|
| 🚀 快速入门 | 5分钟 | 新手学习 | 基础概念 + 示例 |
| 🔧 完整框架 | 20分钟 | 经验开发者 | 完整文档 + 源码 |
| 🏢 完整生态 | 60分钟 | 企业级 | 阿里云集成 + 高级功能 |

---

## 立即开始

**推荐**: 从方案1开始，根据需要逐步升级到方案2或方案3。

```bash
# 设置 Token（一次性）
set GITHUB_TOKEN=your_github_token_here

# 开始抓取
skill-seekers unified --config configs/spring_ai_starter.json
```

**5分钟后即可在 Claude 中使用！**