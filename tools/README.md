# Skills 自动化评分工具

自动化分析和评估 Claude Skills 质量的工具。

## 功能特性

- 🎯 **自动化评分**：基于 100 分制评分体系
- 📊 **等级评定**：S/A/B/C/D 五个等级
- 🔍 **对比分析**：识别和对比相似技能
- 📄 **双格式报告**：JSON 数据 + Markdown 总结

## 评分体系

- **内容质量**（50分）⭐ - 指令清晰度、技术深度、文档完整度
- **技术实现**（30分）- 代码示例质量、设计模式
- **维护性**（10分）- 更新频率、社区活跃度
- **用户体验**（10分）- 易用性、可读性

## 快速开始

### 安装依赖

```bash
cd tools
pip install -r requirements.txt
```

### 分析单个技能

```bash
python scripts/analyze_single.py ../skills_all/api-design-principles
```

### 批量分析所有技能

```bash
python scripts/analyze_all.py
```

输出：
- `reports/analysis_YYYYMMDD_HHMMSS.json` - 详细数据
- `reports/summary_YYYYMMDD_HHMMSS.md` - 总结说明

### 对比技能

```bash
python scripts/compare_skills.py pdf pdf-processing pdf-processing-pro
```

## 项目结构

```
tools/
├── analyzer/          # 评分器模块
│   ├── utils.py      # 工具函数
│   ├── content_scorer.py      # 内容质量评分（50分）
│   ├── technical_scorer.py    # 技术实现评分（30分）
│   ├── maintenance_scorer.py  # 维护性评分（10分）
│   ├── ux_scorer.py          # 用户体验评分（10分）
│   ├── skill_analyzer.py     # 主分析器
│   └── report_generator.py   # Markdown 报告生成
├── scripts/          # 执行脚本
├── config/           # 配置文件
├── reports/          # 报告输出
└── tests/            # 测试文件
```

## 配置

评分权重可在 `config/scoring_weights.json` 中调整。

## 开发

```bash
# 运行测试
pytest tests/

# 代码覆盖率
pytest --cov=analyzer tests/
```
