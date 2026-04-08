# 📊 数据治理与可视化分析平台

## 项目简介

这是一个**企业级数据治理与可视化**课程设计项目，包含完整的数据采集、质量评估、治理体系和可视化分析功能。

## 项目特点

- ✅ 完整的数据治理流程（采集→质量→治理→可视化）
- ✅ 企业级数据质量评估体系
- ✅ 专业的可视化仪表板
- ✅ 规范的元数据管理和数据字典
- ✅ 代码结构清晰，易于维护和扩展

## 🎯 项目目标

1. **数据采集** - 从多源采集和规范化数据
2. **数据质量评估** - 完整性、唯一性、有效性检验
3. **数据治理** - 元数据管理、数据字典、数据分类
4. **可视化分析** - 生成交互式HTML仪表板

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/haoxinlong2736404344/data-governance-visualization.git
cd data-governance-visualization
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行程序
```bash
python main.py
```

### 5. 查看结果
打开 `reports/dashboard.html` 查看可视化仪表板

## 📊 项目流程

```
数据采集 → 数据质量评估 → 数据治理 → 可视化生成 → 报告输出
  1000条   87.5/100评分    元数据管理   7张图表      HTML + JSON
```

## 📁 核心模块

| 模块 | 功能 | 文件 |
|------|------|------|
| 数据采集 | 生成/加载销售数据 | `src/data_collection/collector.py` |
| 数据质量 | 完整性/唯一性/有效性评估 | `src/data_quality/validator.py` |
| 数据治理 | 元数据管理、数据字典 | `src/data_governance/metadata.py` |
| 可视化 | 图表生成 | `src/visualization/charts.py` |

## 📊 生成的输出

- **reports/dashboard.html** - 交互式可视化仪表板
- **reports/quality_report.json** - 数据质量报告
- **reports/metadata.json** - 元数据和数据字典

## 📝 使用示例

```python
from src.data_collection.collector import DataCollector
from src.data_quality.validator import DataQualityValidator

# 采集数据
collector = DataCollector()
sales_data = collector.generate_sample_sales_data(rows=1000)

# 评估质量
validator = DataQualityValidator(sales_data)
report = validator.generate_quality_report()
print(f"质量评分: {report['overall_quality_score']:.2f}/100")
```
