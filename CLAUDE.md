# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Claude Skills 技能库聚合仓库,包含 600+ 个来自官方和社区的技能包。技能是预设的提示词包和脚本,用于教会 Claude 执行特定任务,无需每次重复解释上下文。

## Python 虚拟环境

**重要：** 项目的 Python 依赖使用虚拟环境管理，执行任何 Python 命令前必须先激活虚拟环境。

### 激活虚拟环境

```bash
# 进入 tools 目录并激活虚拟环境
cd tools
source .venv/bin/activate

# 激活后即可运行 Python 命令
python -m pytest tests/
python analyzer/skill_analyzer.py
```

### 使用示例

```bash
# ❌ 错误：未激活虚拟环境
cd /root/workspace/ordinary-claude-skills
python3 -m pytest tools/tests/

# ✅ 正确：先激活虚拟环境
cd /root/workspace/ordinary-claude-skills/tools
source .venv/bin/activate
python -m pytest tests/

# 或者在一行命令中激活并执行
source tools/.venv/bin/activate && python -m pytest tools/tests/
```

### 安装新依赖

```bash
cd tools
source .venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt  # 更新依赖列表
```

### 虚拟环境位置

- **虚拟环境目录**: `tools/.venv/`
- **Python 解释器**: `tools/.venv/bin/python`
- **pip**: `tools/.venv/bin/pip`

## 仓库结构

```
ordinary-claude-skills/
├── docs/                    # 静态网站文件(docsify)
│   ├── index.html          # 网站入口
│   ├── SUMMARY.md          # 技能索引
│   └── pages/              # 各分类页面
├── skills_all/             # 所有技能的扁平化存储(415个)
├── skills_categorized/     # 按分类组织的技能(63个分类)
│   ├── backend/            # 后端开发技能
│   ├── frontend/           # 前端开发技能
│   ├── scientific-computing/ # 科学计算技能
│   └── [其他60个分类]/
├── README.md               # 主要文档
└── LICENSE                 # MIT协议

注意:
- skills_all 包含415个独特技能
- skills_categorized 包含1,444个条目(同一技能可能属于多个分类)
- 每个技能目录通常包含: SKILL.md(必需)和 metadata.json(可选)
```

## 技能文件结构

每个技能目录的标准结构:

```
skill-name/
├── SKILL.md          # 核心技能定义(必需)
│                     # 包含YAML前置元数据和Markdown指令
├── metadata.json     # 元数据(96%的技能包含)
│                     # 包含id、作者、描述、GitHub链接等
├── README.md         # 使用说明(5%的技能包含)
├── scripts/          # 辅助脚本(少数技能)
├── assets/           # 资源文件(少数技能)
└── references/       # 参考文档(少数技能)
```

### SKILL.md 文件格式

```markdown
---
name: skill-name
description: 技能描述
---

# 技能名称

## When to Use This Skill
使用场景说明

## Core Concepts
核心概念

## [具体指令内容]
```

### metadata.json 格式

```json
{
  "id": "unique-identifier",
  "name": "skill-name",
  "author": "author-username",
  "authorAvatar": "https://...",
  "description": "技能描述",
  "githubUrl": "https://github.com/...",
  "stars": 12345,
  "forks": 123,
  "updatedAt": 1234567890,
  "hasMarketplace": true,
  "path": "SKILL.md",
  "branch": "main"
}
```

## 63个主要分类

技能按以下分类组织:

**科学研究类**
- academic, astronomy-physics, bioinformatics, computational-chemistry
- lab-tools, scientific-computing

**软件工程类**
- backend, frontend, full-stack, mobile
- architecture-patterns, framework-internals
- debugging, testing, code-quality
- git-workflows, cicd

**基础设施类**
- cloud, containers, monitoring, system-admin
- database-tools, sql-databases, nosql-databases

**数据与AI类**
- data-analysis, data-engineering, machine-learning, llm-ai

**商业应用类**
- business-apps, ecommerce, ecommerce-development
- finance-investment, sales-marketing, payment
- project-management, productivity-tools

**内容创作类**
- content-creation, design, media, documents
- literature-writing, arts-crafts

**Web3与区块链类**
- web3-tools, smart-contracts, defi

**其他专业领域**
- security, automation-tools, cli-tools
- education, health-fitness, culinary-arts
- real-estate-legal, philosophy-ethics
- divination-mysticism(神秘学)

## 主要贡献者

- **K-Dense-AI**: 64个技能
- **wshobson**: 60个技能
- **ruvnet**: 20个技能
- **anthropics**: 14个官方技能
- **其他社区贡献者**: 250+个技能

## 常用操作

### 浏览技能

```bash
# 查看所有分类
ls skills_categorized/

# 查看特定分类下的技能
ls skills_categorized/backend/

# 搜索技能名称
find skills_categorized -name "*api*" -type d

# 搜索技能内容
grep -r "GraphQL" skills_categorized --include="SKILL.md"
```

### 查看技能详情

```bash
# 读取技能定义
cat skills_categorized/backend/api-design-principles/SKILL.md

# 读取元数据
cat skills_categorized/backend/api-design-principles/metadata.json
```

### 统计信息

```bash
# 统计所有技能数量
ls skills_all | wc -l  # 输出: 415

# 统计某分类下的技能数量
ls skills_categorized/backend | wc -l

# 查找包含特定作者的技能
find skills_categorized -name "metadata.json" -exec grep -l "wshobson" {} \;
```

## 静态网站

项目包含一个基于 docsify 的静态文档网站:

- **源码位置**: `docs/` 目录
- **在线地址**: https://microck.github.io/ordinary-claude-skills/
- **本地预览**: 需要 HTTP 服务器(不能直接打开 index.html)

```bash
# 使用 Python 启动本地服务器
cd docs
python3 -m http.server 8000

# 访问 http://localhost:8000
```

## 使用技能的方式

### 1. Claude.ai Web界面
- 进入个人设置 → Custom Skills
- 上传特定技能目录

### 2. MCP (Model Context Protocol)
在 MCP 配置中指向技能目录:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/ordinary-claude-skills/skills_categorized/[category]"
      ]
    }
  }
}
```

### 3. API集成
将 SKILL.md 内容作为系统提示词注入

## 技能内容特点

- **懒加载**: 仅在需要时加载,节省上下文窗口
- **模块化**: 每个技能专注于特定领域
- **标准化**: 大多数遵循相似的文件结构
- **社区驱动**: 来自多个开源项目的聚合

## 注意事项

1. **未经筛选**: 作者声明技能未经全面审核,部分可能不可用
2. **无依赖管理**: 仓库本身无需安装依赖,但个别技能可能需要 Python/Node.js
3. **技能冲突**: 避免同时加载相互矛盾的技能(如 creative-writing 和 technical-documentation)
4. **文件过大**: 某些技能包含大型依赖,使用时忽略 node_modules
5. **重复分类**: skills_categorized 中同一技能可能出现在多个分类下

## 许可证

- 主仓库: MIT License
- 个别技能: 查看各技能目录下的 LICENSE 文件
- 技能来源: Anthropic, ComposioHQ, K-Dense-AI等开源项目
