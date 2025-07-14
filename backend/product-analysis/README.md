# 商品分析模块

## 模块结构

```txt
product-analysis/
├── input               # 数据输入目录（用于CSV模式）
├── output              # 结果导出目录
│   ├── reports/                   # 报告目录
│   │   ├── product_sales_report_20250712_143022.csv
│   │   ├── high_cancel_products_20250712_143022.csv
│   │   └── product_associations_20250712_143022.csv
│   └── charts/                    # 图表目录
│       └── product_sales_analysis_20250712_143022.png
├── src                 # 源代码目录
│   └── product_analysis.py    # 商品分析主文件
├── config.py                  # 配置文件（可选）
└── requirements.txt           # 依赖文件
```

## 进度

### 已实现的功能（及其对应函数）

| 功能 | 对应函数 | 描述 |
|------|----------|------|
| 数据库连接与数据加载 | `__init__()` 和 `load_data()` | 连接MySQL数据库，加载订单、商品和分类数据 |
| 商品销售分析 | `sales_analysis()` | 计算商品总销量、总销售额、平均销售额和热销时段 |
| 高取消率商品识别 | `cancellation_analysis()` | 识别取消率高于平均水平的商品 |
| 商品关联分析 | `association_analysis()` | 使用Apriori算法发现商品关联组合 |
| 分类销售排名 | `category_analysis()` | 统计各级分类的销量和销售额排名 |
| 销售数据可视化 | `visualize_sales()` | 生成销售额和销量TOP商品的图表 |
| 报告生成 | `generate_report()` | 整合所有分析结果生成完整报告 |
| 运营建议生成 | `generate_recommendations()` | 基于分析结果生成可操作的运营建议 |
| 日期筛选 | `filter_by_date()` | 按时间范围筛选数据 |

### 待实现的功能

## 启动与输出

### 启动方式

> 先根据数据源的不同配置文件

- 如果使用数据库为数据源：

将`backend/product-analysis/config.py`中的`user`和`password`替换为自己的

- 如果使用`.csv`文件为数据源：

将`config.py`中的`DATA_SOURCE'的值替换为`csv`，并在`backend/product-analysis/input`目录下的添加`.csv`文件，命名为`orders.csv`、`products.csv`和`categories.csv`

> 然后在项目根目录运行：

```bash
python backend/product-analysis/src/product_analysis.py
```

### 输出结果及其分析

- 使用数据库中的数据时：

```txt
配置文件加载成功!
数据库连接成功!
正在加载数据...
数据加载完成! 共加载 225 条记录, 耗时: 0:00:00.010148

==================================================
开始生成商品分析报告 (时间范围: 2025-06-01 至 2025-07-01)
==================================================

=== 商品销售分析 ===
 ProductID     ProductName  total_quantity  total_sales  order_count  avg_sales  peak_hour
4357786608   小银鱼/干虾 干果150g             147       3486.0           83  35.938144          9
4029931608          辣白菜 袋装             106       2640.0           51  50.769231         18
4357786584             牛板筋              32       1010.0           12  63.125000         21
4357786197 拌桔梗（咸口&甜口） 250g              47        774.0           36  20.918919         19
4360592195            亲久米酒              25        445.0           14  21.190476         15

=== 高取消率商品 ===
 ProductID   ProductName  总订单数  取消订单数    取消率
4357786608 小银鱼/干虾 干果150g    83   12.0 14.46%
正在分析商品关联规则 (最小支持度: 0.005)...
E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\src\product_analysis.py:366: SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame

See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  result.rename(columns={
关联分析完成! 耗时: 0:00:00.006637

=== 商品关联分析 ===
                          商品组合  组合商品数量   支持度
拌桔梗（咸口&甜口） 250g, 小银鱼/干虾 干果150g       2 8.82%
       辣白菜 袋装, 拌桔梗（咸口&甜口） 250g       2 8.82%
         辣白菜 袋装, 小银鱼/干虾 干果150g       2 8.82%
           亲久米酒, 小银鱼/干虾 干果150g       2 2.94%
                  亲久米酒, 辣白菜 袋装       2 2.94%
          牛板筋, 拌桔梗（咸口&甜口） 250g       2 2.94%
                   牛板筋, 辣白菜 袋装       2 2.94%
   亲久米酒, 辣白菜 袋装, 小银鱼/干虾 干果150g       3 2.94%
  牛板筋, 辣白菜 袋装, 拌桔梗（咸口&甜口） 250g       3 2.94%
正在进行商品健康度分析...
E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\src\product_analysis.py:511: SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame

See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  result.rename(columns={
健康度分析完成! 耗时: 0:00:00.007963

=== 商品健康度分析 ===
      商品ID            商品名称  总销量   总销售额    利润率    退货率    动销率 健康状态
4357786608   小银鱼/干虾 干果150g  147 3486.0 30.00% 11.97% 42.13% 一般商品
4029931608          辣白菜 袋装  106 2640.0 30.00%  7.49% 25.89% 健康商品
4357786584             牛板筋   32 1010.0 30.00% 14.64%  6.09% 一般商品
4357786197 拌桔梗（咸口&甜口） 250g   47  774.0 30.00% 19.01% 18.27% 一般商品
4360592195            亲久米酒   29  525.0 30.00%  3.12%  7.61% 健康商品

=== 一级分类销售额排名 ===
Category1  total_quantity  total_sales
       食品             361       8435.0
已保存销售分析图表: E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\output\charts\product_sales_analysis_20250715_004805.png

=== 运营建议 ===
1. 高取消率商品(1款): 如小银鱼/干虾 干果150g - 建议检查商品描述、库存状态和物流时效
2. 热销商品推荐: 小银鱼/干虾 干果150g, 辣白菜 袋装, 牛板筋 - 建议增加库存和推广资源
3. 发现9组商品关联组合 - 推荐促销组合: [拌桔梗（咸口&甜口） 250g, 小银鱼/干虾 干果150g]
4. 表现最佳品类: 食品 - 建议加大该品类商品开发
已保存销售报告: E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\output\reports\product_sales_report_20250715_004805.csv
已保存高取消率商品报告: E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\output\reports\high_cancel_products_20250715_004805.csv
已保存商品关联报告: E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\output\reports\product_associations_20250715_004805.csv
已保存商品健康度报告: E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\output\reports\product_health_report_20250715_004805.csv
已保存报告摘要: E:\CodeLab_E\xxq202507\github\test\backend\product-analysis\output\reports\report_summary_20250715_004805.txt

报告生成完成!
数据库连接已关闭
```

- 使用`CSV`文件中的数据时：

【未测试】
