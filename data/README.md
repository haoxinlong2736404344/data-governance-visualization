# 真实数据集使用说明

## 推荐数据集（课程设计优先）

- 数据集名称：Superstore Sales（优先，区域+渠道维度更丰富）
- 示例来源：https://raw.githubusercontent.com/yajasarora/Superstore-Sales-Analysis-with-Tableau/master/Superstore%20sales%20dataset.csv
- 业务语义：包含 Region/State/City 与 Ship Mode，更适合治理成效展示

- 数据集名称：Supermarket Sales（次优，含渠道字段）
- 示例来源：https://raw.githubusercontent.com/sushantag9/Supermarket-Sales-Data-Analysis/master/supermarket_sales%20-%20Sheet1.csv
- 业务语义：交易数据包含 Payment 字段，可直接作为销售渠道分析维度

- 数据集名称：UCI Online Retail（备选）
- 官网页面：https://archive.ics.uci.edu/dataset/352/online+retail
- 许可协议：CC BY 4.0
- 业务语义：电商交易明细，适合做数据质量与治理成效分析

## 放置方式

请将下载后的文件放到 `data/` 目录，以下任一文件名都可自动识别：

- `data/superstore_sales.csv`（最优先）
- `data/Superstore sales dataset.csv`
- `data/supermarket_sales.csv`（优先）
- `data/Supermarket Sales.csv`
- `data/Online Retail.xlsx`
- `data/online_retail.xlsx`
- `data/online_retail.csv`

## 运行

```bash
python main.py
```

程序将优先加载 Superstore Sales；若不存在则尝试 Supermarket Sales，再尝试 UCI 数据集；都不可用时回退模拟数据。
