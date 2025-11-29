# Spring AI Alibaba 技能抓取指南

**创建日期**: 2025-11-29
**版本**: v2.0 - 用户操作指南
**适用工具**: Skill Seekers v2.0.0

---

## 抓取目标

创建 Claude AI 技能，使 AI 助手能够：

- **掌握 Spring AI 框架** - 理解核心概念、API 和常用功能（聊天、RAG、嵌入等）
- **掌握 Spring AI Alibaba 适配层** - 熟悉阿里云模型集成（通义千问、百川等）
- **提供可运行的代码示例** - 快速回答技术问题，辅助开发和调试

---

## 抓取资源

### 核心资源（必须抓取）

| 资源 | URL | 说明 |
|------|-----|------|
| Spring AI 官方文档 | https://docs.spring.io/spring-ai/reference/ | 官方完整文档 |
| Spring AI 官方仓库 | https://github.com/spring-projects/spring-ai | 核心源代码和架构 |
| Spring AI Alibaba 主仓库 | https://github.com/alibaba/spring-ai-alibaba | 阿里适配层和扩展 |
| Spring AI Alibaba 示例 | https://github.com/spring-ai-alibaba/examples | 官方示例代码 |

### 扩展资源（可选）

| 资源 | URL | 说明 |
|------|-----|------|
| Admin 管理控制台 | https://github.com/spring-ai-alibaba/spring-ai-alibaba-admin | 管理界面 |
| Extensions 扩展 | https://github.com/spring-ai-alibaba/spring-ai-extensions | 社区扩展 |

---

## 操作步骤

### 阶段 1: 快速入门（立即可用）

**目标**: 30分钟内获得立即可用的开发技能

**执行命令**:

```bash
# 1. 抓取文档入门部分 + 示例代码
skill-seekers unified --config configs/spring_ai_starter.json

# 2. AI 增强（可选但推荐）
skill-seekers enhance output/spring-ai-starter/

# 3. 打包技能
skill-seekers package output/spring-ai-starter/

# 4. 上传到 Claude Code
# 手动上传（推荐）: 访问 https://claude.ai/skills 上传 .zip 文件
# 自动上传（可选）: skill-seekers upload output/spring-ai-starter.zip （需设置 ANTHROPIC_API_KEY）
```

**配置文件**: `configs/spring_ai_starter.json`

```json
{
  "name": "spring-ai-starter",
  "description": "Spring AI Alibaba quick start guide with examples",
  "sources": [
    {
      "type": "docs",
      "base_url": "https://docs.spring.io/spring-ai/reference/",
      "max_pages": 100,
      "selectors": {
        "main_content": "article",
        "title": "h1",
        "code_blocks": "pre code"
      },
      "url_patterns": {
        "include": ["/getting-started/", "/concepts/", "/chat/", "/embeddings/"],
        "exclude": ["/api/", "/advanced/"]
      }
    },
    {
      "type": "github",
      "repo": "spring-ai-alibaba/examples",
      "include_code": true,
      "code_analysis_depth": "deep"
    }
  ],
  "merge_mode": "rule-based"
}
```

**验证测试**:

上传技能后，在 Claude 中测试：

1. "如何用 Spring AI Alibaba 调用通义千问？"
2. "给我一个 Spring AI 聊天机器人的完整示例"
3. "Spring AI 的 ChatClient 怎么配置？"

---

### 阶段 2: 深入核心（本周完成）

**目标**: 理解底层原理，掌握高级特性

**执行时机**: 使用阶段1技能1-2天后

**执行命令**:

```bash
# 1. 抓取完整官方文档和源码
skill-seekers unified --config configs/spring_ai_official.json

# 2. AI 增强
skill-seekers enhance output/spring-ai-official/

# 3. 打包并上传到 Claude Code
skill-seekers package output/spring-ai-official/
# 访问 https://claude.ai/skills 上传 output/spring-ai-official.zip
```

**配置文件**: `configs/spring_ai_official.json`

```json
{
  "name": "spring-ai-official",
  "description": "Complete Spring AI framework with advanced features",
  "sources": [
    {
      "type": "docs",
      "base_url": "https://docs.spring.io/spring-ai/reference/",
      "max_pages": 500,
      "selectors": {
        "main_content": "article",
        "title": "h1",
        "code_blocks": "pre code"
      }
    },
    {
      "type": "github",
      "repo": "spring-projects/spring-ai",
      "include_code": true,
      "code_analysis_depth": "deep",
      "paths": [
        "spring-ai-core/",
        "spring-ai-spring-boot-autoconfigure/"
      ]
    }
  ],
  "merge_mode": "claude-enhanced"
}
```

**验证测试**:

1. "Spring AI 的 ChatClient 内部是如何实现的？"
2. "如何自定义一个新的 AI 模型适配器？"
3. "Spring AI 的 Function Calling 机制是什么？"

---

### 阶段 3: 完整生态（需要时执行）

**目标**: 掌握所有阿里云集成和扩展功能

**执行时机**: 需要使用阿里云特定功能时

**执行命令**:

```bash
# 1. 抓取 Alibaba 主仓库 + 扩展
skill-seekers unified --config configs/spring_ai_alibaba.json

# 2. AI 增强
skill-seekers enhance output/spring-ai-alibaba/

# 3. 打包并上传到 Claude Code
skill-seekers package output/spring-ai-alibaba/
# 访问 https://claude.ai/skills 上传 output/spring-ai-alibaba.zip

# 可选：抓取管理控制台和扩展
skill-seekers github --repo spring-ai-alibaba/spring-ai-alibaba-admin
skill-seekers github --repo spring-ai-alibaba/spring-ai-extensions
skill-seekers package output/spring-ai-alibaba-admin/
skill-seekers package output/spring-ai-alibaba-extensions/
# 同样访问 https://claude.ai/skills 上传对应的 .zip 文件
```

**配置文件**: `configs/spring_ai_alibaba.json`

```json
{
  "name": "spring-ai-alibaba",
  "description": "Complete Spring AI Alibaba ecosystem with cloud integration",
  "sources": [
    {
      "type": "github",
      "repo": "alibaba/spring-ai-alibaba",
      "include_code": true,
      "code_analysis_depth": "full",
      "paths": [
        "spring-ai-alibaba-core/",
        "community/",
        "spring-ai-alibaba-agent-framework/",
        "spring-ai-alibaba-graph-core/"
      ]
    },
    {
      "type": "github",
      "repo": "spring-ai-alibaba/examples",
      "include_code": true,
      "code_analysis_depth": "full"
    }
  ],
  "merge_mode": "claude-enhanced"
}
```

**验证测试**:

1. "Spring AI Alibaba 的 Agent Framework 怎么使用？"
2. "如何配置通义千问的不同模型版本？"
3. "Spring AI Alibaba 与官方 Spring AI 的主要区别？"

---

## 执行时间表

| 阶段 | 执行时机 | 用时 | 产出 |
|------|----------|------|------|
| 阶段1 | 今天立即执行 | 30分钟 | 立即可用的入门技能 |
| 阶段2 | 1-2天后 | 1小时 | 深入理解底层原理 |
| 阶段3 | 需要时执行 | 1.5小时 | 完整阿里云生态掌握 |

**总用时**: 3小时（分3次执行）

---

## 快速开始

```bash
# 进入项目目录
cd D:\02_Dev\Workspace\GitHub\Skill_Seekers

# 立即执行阶段1（推荐）
skill-seekers unified --config configs/spring_ai_starter.json
skill-seekers enhance output/spring-ai-starter/
skill-seekers package output/spring-ai-starter/

# 上传到 Claude Code
# 访问 https://claude.ai/skills 上传 output/spring-ai-starter.zip
```

30分钟后即可开始使用！

---

## 更新策略

**何时更新**:
- Spring AI 发布重大版本时
- Spring AI Alibaba 添加新模型支持时
- 技能无法回答新问题时

**如何更新**:

```bash
# 删除旧数据
rm -rf output/spring-ai-starter* output/spring-ai-official* output/spring-ai-alibaba*

# 重新执行对应阶段的命令
skill-seekers unified --config configs/spring_ai_starter.json
# ... 后续步骤同上
```

**建议**: 每月检查一次更新

---

## 常见问题

**Q: 配置文件在哪里？**
A: 需要手动创建 `configs/spring_ai_starter.json`、`configs/spring_ai_official.json`、`configs/spring_ai_alibaba.json` 三个文件，内容见上文。

**Q: 可以只执行阶段1吗？**
A: 可以！阶段1已经满足大部分开发需求，后续阶段按需执行。

**Q: 如何验证技能质量？**
A: 上传后在 Claude 中提问，检查回答是否准确、代码示例是否可运行。

**Q: 抓取失败怎么办？**
A: 检查网络连接，查看 `TROUBLESHOOTING.md` 获取详细帮助。

---

## 支持与反馈

- 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 获取故障排除指南
- 查看 [GitHub Issues](https://github.com/yusufkaraaslan/Skill_Seekers/issues) 搜索已知问题
- 提交新 Issue 报告问题或建议

---

**准备好了吗？立即开始阶段1！**

```bash
skill-seekers unified --config configs/spring_ai_starter.json
```
