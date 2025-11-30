# Spring AI Alibaba 技能抓取指南

创建专业的 Spring AI + Spring AI Alibaba 技能，让 Claude AI 成为你的 Spring AI 开发助手。

**适用工具**: Skill Seekers v2.0.0
**抓取方式**: 全自动 + 实时进度监控
**总用时**: 50-90 分钟（一键完成三个方案）

---

## ⚡ 推荐方案: 一键执行（80% 用户选择这个！）

### 适用场景
- ✅ 想要一次性获取所有三个技能（入门 + 框架 + 生态）
- ✅ 不想手动运行三次命令
- ✅ 需要实时查看抓取进度
- ✅ 失败后自动重试

### 前置条件（必读！）

#### 1. 设置 GitHub Token（一次性设置）

**为什么需要 Token?**
- 访问 GitHub 仓库需要认证
- 避免 API 限流（未认证: 60次/小时，认证: 5000次/小时）

**如何获取 Token?**

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 设置名称: `skill-seekers`
4. 选择权限: ✅ `public_repo`
5. 点击 "Generate token"
6. **立即复制** Token（只显示一次！）

**设置 Token:**

```bash
# Windows
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# macOS/Linux
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

**验证 Token:**

```bash
# Windows
echo %GITHUB_TOKEN%

# macOS/Linux
echo $GITHUB_TOKEN
```

应该看到你的 Token（不是空白！）

---

### 执行步骤

#### 第一步: 打开两个终端

**终端 1 - 运行抓取（主窗口）:**

```bash
cd D:\02_Dev\Workspace\GitHub\Skill_Seekers
python run_springai_three_phases.py --skip-existing --force-retry
```

**终端 2 - 实时监控（查看进度）:**

```bash
cd D:\02_Dev\Workspace\GitHub\Skill_Seekers
python watch_springai_progress.py
```

---

#### 第二步: 观察实时进度

**你会看到这样的界面:**

```
======================================================================
📊 Progress Monitor - spring-ai-starter
======================================================================

Status: 🔄 RUNNING
Started: 2025-01-15 10:30:00
Last Update: 2025-01-15 10:32:15
Elapsed: 2m 15s

📦 PHASES
----------------------------------------------------------------------
🔄 Phase 1: Scraping Sources (running)
  🔄 documentation: running
     Progress: 45/100 pages
     Time: 2m 10s
     URL: https://docs.spring.io/spring-ai/reference/api/chat
  ⏳ github: pending
     Progress: 0/0

⏳ Phase 2: Conflict Detection (pending)

⏳ Phase 3: Merging (pending)

⏳ Phase 4: Building Skill (pending)

======================================================================
⏳ Scraping in progress... (Refresh every 3 seconds)
   Press Ctrl+C to stop monitoring
======================================================================
```

**状态图标说明:**
- 🔄 `running` - 正在运行
- ⏳ `pending` - 等待开始
- ✅ `completed` - 已完成
- ❌ `failed` - 失败
- ⏰ `timeout` - 超时

---

### 预期时间

| 阶段 | 时间 | 说明 |
|-----|------|------|
| **方案1: 快速入门** | 5-10 分钟 | 基础文档 + 示例代码 |
| **方案2: 完整框架** | 15-20 分钟 | 完整文档 + 源码分析 |
| **方案3: 完整生态** | 30-60 分钟 | 阿里云生态 + Agent 框架 |
| **总计** | **50-90 分钟** | 全自动执行 |

💡 **提示**: 去喝杯咖啡，脚本会自动完成所有工作！

---

### 自动化特性

✅ **智能跳过** - 已完成的阶段自动跳过
✅ **自动重试** - 失败的阶段自动重试
✅ **实时进度** - 随时查看当前状态
✅ **多任务监控** - 可同时监控所有阶段
✅ **断点续传** - 中断后可以继续

---

### 完成后

**所有阶段成功后，你会得到三个技能包:**

```
output/
├── spring-ai-starter.zip         # 方案1: 快速入门
├── spring-ai-official.zip        # 方案2: 完整框架
└── spring-ai-alibaba.zip         # 方案3: 完整生态
```

**上传到 Claude:**

1. 访问 https://claude.ai/skills
2. 逐个上传 `.zip` 文件
3. 立即开始使用！

**测试技能:**

在 Claude 中输入:
- "如何用 Spring AI Alibaba 调用通义千问？"
- "给我一个 Spring AI 聊天机器人的完整示例"
- "Spring AI 的 ChatClient 怎么配置？"

---

## 📖 常见场景

### 场景 1: 只想要快速入门

```bash
# 只运行方案1
python run_springai_three_phases.py --phase 1
```

### 场景 2: 昨天失败了，今天继续

```bash
# 自动跳过成功的，重试失败的
python run_springai_three_phases.py --skip-existing --force-retry
```

**脚本会:**
- ✅ 跳过已成功的阶段
- 🔄 自动重试失败的阶段
- 🆕 继续执行未完成的阶段

### 场景 3: 想更新所有技能

```bash
# 删除旧数据
rm -rf output/spring-ai-*

# 重新抓取所有方案
python run_springai_three_phases.py --force-retry
```

### 场景 4: 自定义执行

```bash
# 只运行方案2和方案3
python run_springai_three_phases.py --phase 2 --phase 3

# 跳过已完成的
python run_springai_three_phases.py --phase 2 --phase 3 --skip-existing
```

---

## 🔧 故障排除

### 问题 1: GitHub Token 错误

**现象:**
```
❌ GitHub API rate limit exceeded
```

**原因:** Token 未设置或已过期

**解决方案:**

```bash
# 1. 重新设置 Token
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 2. 验证
echo %GITHUB_TOKEN%

# 3. 重新运行
python run_springai_three_phases.py --skip-existing --force-retry
```

---

### 问题 2: 抓取超时

**现象:**
进度文件显示 `⏰ timeout`，或者某个阶段卡住超过 10 分钟

**原因:**
- 网络太慢
- `max_pages` 设置过大
- 服务器限流

**解决方案:**

**方法 A: 减少页面数（推荐）**

编辑配置文件 `configs/spring_ai_starter.json`:

```json
{
  "sources": [
    {
      "type": "documentation",
      "max_pages": 50,     // 从 100 降到 50
      "rate_limit": 0.5
    }
  ]
}
```

**方法 B: 增加超时**

```json
{
  "sources": [
    {
      "type": "documentation",
      "timeout": 1200      // 20 分钟超时
    }
  ]
}
```

**方法 C: 检查网络**

```bash
# 测试网络连接
python test_network.py
```

修改后重新运行:
```bash
python run_springai_three_phases.py --skip-existing --force-retry
```

---

### 问题 3: 看不到进度

**现象:**
监控窗口显示 "等待任务启动..." 超过 1 分钟

**排查步骤:**

1. **检查进度文件是否存在**
   ```bash
   # Windows
   dir output\*_progress.json

   # macOS/Linux
   ls output/*_progress.json
   ```

2. **查看进度文件内容**
   ```bash
   # Windows
   type output\spring-ai-starter_progress.json

   # macOS/Linux
   cat output/spring-ai-starter_progress.json
   ```

3. **检查抓取进程是否在运行**
   ```bash
   # 在终端 1 中应该看到日志输出
   # 如果没有输出，说明进程可能卡住了
   ```

4. **重启抓取**
   ```bash
   # Ctrl+C 中断
   # 重新运行
   python run_springai_three_phases.py --skip-existing --force-retry
   ```

---

### 问题 4: 某个阶段失败

**现象:**
进度显示 `❌ failed`

**查看错误详情:**

```bash
# 查看进度文件中的错误
python -c "import json; data=json.load(open('output/spring-ai-starter_progress.json')); print('\n'.join([e['message'] for e in data['errors']]))"
```

**常见错误和解决方案:**

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `Connection timeout` | 网络超时 | 检查网络，重试 |
| `404 Not Found` | 页面不存在 | 检查配置 URL |
| `Permission denied` | 文件权限 | 检查 output/ 目录权限 |
| `Module not found` | 依赖缺失 | `pip install -r requirements.txt` |

**通用解决方案:**

```bash
# 修复问题后，自动重试失败的阶段
python run_springai_three_phases.py --skip-existing --force-retry
```

---

## 📚 三种抓取方案详解

如果你想单独运行某个方案，可以使用以下命令:

### 🚀 方案1：快速入门（推荐新手）

**适用场景:** 刚开始学习 Spring AI，需要基础概念和示例
**用时:** 5-10 分钟
**内容:** 入门教程 + 基础示例 + 通义千问集成

```bash
# 前置条件：设置 GitHub Token
set GITHUB_TOKEN=your_github_token_here

# 执行抓取
skill-seekers unified --config configs/spring_ai_starter.json

# 增强（可选）
skill-seekers enhance output/spring-ai-starter/

# 打包
skill-seekers package output/spring-ai-starter/
```

**生成文件:** `output/spring-ai-starter.zip`

---

### 🔧 方案2：完整框架（适合有经验开发者）

**适用场景:** 需要深入了解 Spring AI 底层原理和高级特性
**用时:** 15-20 分钟
**内容:** 完整官方文档 + 源码分析 + 高级特性

```bash
# 执行抓取
skill-seekers unified --config configs/spring_ai_official.json

# 增强
skill-seekers enhance output/spring-ai-official/

# 打包
skill-seekers package output/spring-ai-official/
```

**生成文件:** `output/spring-ai-official.zip`

---

### 🏢 方案3：完整生态（企业级开发）

**适用场景:** 需要使用阿里云集成、Agent框架等企业级功能
**用时:** 30-60 分钟
**内容:** 阿里巴巴完整生态 + 管理控制台 + 扩展功能

```bash
# 执行抓取
skill-seekers unified --config configs/spring_ai_alibaba.json

# 增强
skill-seekers enhance output/spring-ai-alibaba/

# 打包
skill-seekers package output/spring-ai-alibaba/
```

**生成文件:** `output/spring-ai-alibaba.zip`

---

## 🎯 方案对比

| 方案 | 用时 | 页面数 | 适用场景 | 包含内容 |
|-----|------|--------|----------|----------|
| 🚀 快速入门 | 5-10 分钟 | ~100 | 新手学习 | 基础概念 + 示例 |
| 🔧 完整框架 | 15-20 分钟 | ~200 | 经验开发者 | 完整文档 + 源码 |
| 🏢 完整生态 | 30-60 分钟 | ~500+ | 企业级 | 阿里云集成 + 高级功能 |

💡 **推荐策略:** 从方案1开始，根据需要逐步升级到方案2或方案3。

---

## 📊 验证技能质量

抓取完成后，在 Claude 中测试技能:

### 基础测试（方案1）
- "如何用 Spring AI Alibaba 调用通义千问？"
- "给我一个 Spring AI 聊天机器人的完整示例"
- "Spring AI 的 ChatClient 怎么配置？"

### 进阶测试（方案2）
- "Spring AI 的 ChatClient 内部是如何实现的？"
- "如何自定义一个新的 AI 模型适配器？"
- "Spring AI 的 Function Calling 机制是什么？"

### 企业级测试（方案3）
- "Spring AI Alibaba 的 Agent Framework 怎么使用？"
- "如何配置通义千问的不同模型版本？"
- "Spring AI Alibaba 与官方 Spring AI 的主要区别？"

---

## ❓ 常见问题

### Q: 可以只运行快速入门方案吗？

**A:** 可以！方案1 已经满足大部分开发需求。

```bash
python run_springai_three_phases.py --phase 1
```

---

### Q: 什么时候需要更新技能？

**A:** 以下情况需要更新:
- Spring AI 发布重大版本时
- Spring AI Alibaba 添加新模型支持时
- 技能无法回答新问题时

**更新方法:**
```bash
# 删除旧数据
rm -rf output/spring-ai-*

# 重新抓取
python run_springai_three_phases.py --force-retry
```

---

### Q: 抓取失败怎么办？

**A:** 自动重试功能会帮你:

```bash
# 第一次失败后，直接重新运行
python run_springai_three_phases.py --skip-existing --force-retry
```

脚本会:
1. 自动跳过已成功的阶段
2. 自动重试失败的阶段
3. 继续执行未完成的阶段

---

### Q: 可以并行运行多个方案吗？

**A:** 不推荐！可能会导致冲突。

建议使用一键执行:
```bash
python run_springai_three_phases.py --skip-existing --force-retry
```

脚本会串行执行所有方案，避免冲突。

---

### Q: 进度文件有什么用？

**A:** 进度文件 (`output/{name}_progress.json`) 记录:
- 当前状态（running/completed/failed）
- 各阶段进度
- 错误信息
- 时间统计

即使进程崩溃，进度文件也会保留，方便恢复。

---

## 🚀 快速开始

**第一次使用？只需三步:**

```bash
# 1. 设置 GitHub Token（一次性）
set GITHUB_TOKEN=your_github_token_here

# 2. 打开两个终端，分别运行:
# 终端 1:
python run_springai_three_phases.py --skip-existing --force-retry

# 终端 2:
python watch_springai_progress.py

# 3. 等待完成（50-90 分钟），去喝杯咖啡！
```

**完成后上传到 Claude，立即开始使用！** 🎉

---

## 📖 延伸阅读

- **完整技术文档:** [THREE_PHASE_GUIDE.md](THREE_PHASE_GUIDE.md)
- **改进说明:** [IMPROVEMENTS.md](IMPROVEMENTS.md)
- **项目主页:** [README.md](README.md)

---

**有问题？** 查看 [故障排除](#故障排除) 或提交 [GitHub Issue](https://github.com/yusufkaraaslan/Skill_Seekers/issues)
