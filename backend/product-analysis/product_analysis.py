import pandas as pd
import numpy as np
import mysql.connector
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# 忽略警告信息
warnings.filterwarnings('ignore', category=UserWarning)

# 数据库配置 (请根据您的实际配置修改)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'jiongs',
    'database': 'shop_db',
    'charset': 'utf8mb4'
}

class ProductAnalyzer:
    def __init__(self, db_config):
        try:
            # 使用 mysql.connector 连接数据库
            self.connection = mysql.connector.connect(**db_config)
            print("数据库连接成功!")
            self.load_data()
        except mysql.connector.Error as err:
            print(f"数据库连接失败: {err}")
            print("请检查您的数据库配置:")
            print(f"主机: {db_config['host']}")
            print(f"端口: {db_config['port']}")
            print(f"用户名: {db_config['user']}")
            print(f"数据库: {db_config['database']}")
            print("密码是否正确？数据库是否运行中？")
            exit(1)
        
    def load_data(self):
        """从MySQL数据库加载所需数据"""
        print("正在从数据库加载数据...")
        start_time = datetime.now()
        
        # 加载订单数据
        orders_query = """
        SELECT OrderID, Status, Created_time, TotalAmount
        FROM orders
        """
        self.orders = pd.read_sql(orders_query, self.connection)
        
        # 加载订单商品项数据
        order_items_query = """
        SELECT oi.OrderItemID, oi.OrderID, oi.ProdSpecID, oi.Quantity, 
               ps.ProductID, ps.Price, ps.Weight,
               p.ProductName, p.CategoryID,
               c.Category1, c.Category2, c.Category3
        FROM order_item oi
        JOIN product_spec ps ON oi.ProdSpecID = ps.ProdSpecID
        JOIN product p ON ps.ProductID = p.ProductID
        JOIN category c ON p.CategoryID = c.CategoryID
        """
        self.order_items = pd.read_sql(order_items_query, self.connection)
        
        # 检查是否有数据
        if self.orders.empty or self.order_items.empty:
            print("警告: 加载的数据为空!")
            print(f"订单记录数: {len(self.orders)}")
            print(f"订单商品项记录数: {len(self.order_items)}")
        
        # 合并订单和商品数据
        self.merged_data = pd.merge(
            self.order_items,
            self.orders[['OrderID', 'Status', 'Created_time']],
            on='OrderID',
            how='inner'
        )
        
        # 处理时间字段 - 确保所有日期都是 Timestamp 类型
        self.merged_data['Created_time'] = pd.to_datetime(self.merged_data['Created_time'])
        
        # 添加日期相关的列
        self.merged_data['order_hour'] = self.merged_data['Created_time'].dt.hour
        self.merged_data['order_date'] = self.merged_data['Created_time'].dt.date
        
        # 计算销售额
        self.merged_data['sales_amount'] = self.merged_data['Quantity'] * self.merged_data['Price']
        
        print(f"数据加载完成! 共加载 {len(self.merged_data)} 条记录, 耗时: {datetime.now()-start_time}")

    def sales_analysis(self, start_date=None, end_date=None):
        """商品销量与销售额统计"""
        # 筛选时间范围
        data = self.filter_by_date(start_date, end_date)
        
        if data.empty:
            print("警告: 没有找到指定时间范围内的销售数据!")
            return pd.DataFrame()
        
        # 按商品统计
        product_stats = data.groupby(['ProductID', 'ProductName']).agg(
            total_quantity=('Quantity', 'sum'),
            total_sales=('sales_amount', 'sum'),
            order_count=('OrderID', 'nunique'),
            avg_sales=('sales_amount', 'mean')
        ).reset_index()
        
        # 热销时间段（按小时）
        peak_hours = data.groupby(['ProductID', 'order_hour'])['Quantity'].sum().reset_index()
        peak_hours = peak_hours.loc[peak_hours.groupby('ProductID')['Quantity'].idxmax()]
        peak_hours.rename(columns={'order_hour': 'peak_hour'}, inplace=True)
        
        # 合并结果
        result = pd.merge(product_stats, peak_hours[['ProductID', 'peak_hour']], on='ProductID', how='left')
        return result.sort_values('total_sales', ascending=False)

    def cancellation_analysis(self):
        """高订单取消率商品识别"""
        if self.merged_data.empty:
            print("警告: 没有可用的合并数据!")
            return pd.DataFrame()
        
        # 筛选已取消订单
        canceled_orders = self.merged_data[self.merged_data['Status'].isin(['交易关闭', '已取消'])]
        
        if canceled_orders.empty:
            print("没有找到已取消的订单")
            return pd.DataFrame()
        
        # 计算每个商品的取消订单数
        canceled_stats = canceled_orders.groupby('ProductID').agg(
            canceled_orders=('OrderID', 'nunique')
        ).reset_index()
        
        # 计算总订单数
        total_orders = self.merged_data.groupby('ProductID')['OrderID'].nunique().reset_index()
        total_orders.rename(columns={'OrderID': 'total_orders'}, inplace=True)
        
        # 计算取消率
        cancel_rates = pd.merge(total_orders, canceled_stats, on='ProductID', how='left').fillna(0)
        
        # 避免除零错误
        cancel_rates['cancellation_rate'] = cancel_rates.apply(
            lambda row: row['canceled_orders'] / row['total_orders'] if row['total_orders'] > 0 else 0,
            axis=1
        )
        
        # 识别高取消率商品（高于平均取消率）
        if not cancel_rates.empty:
            avg_rate = cancel_rates['cancellation_rate'].mean()
            high_cancel = cancel_rates[cancel_rates['cancellation_rate'] > avg_rate]
        else:
            high_cancel = pd.DataFrame()
        
        # 添加商品名称
        if not high_cancel.empty:
            product_names = self.merged_data[['ProductID', 'ProductName']].drop_duplicates()
            result = pd.merge(high_cancel, product_names, on='ProductID')
            return result.sort_values('cancellation_rate', ascending=False)
        else:
            return pd.DataFrame()

    def association_analysis(self, min_support=0.01):
        """商品关联分析"""
        if self.merged_data.empty:
            print("警告: 没有可用的合并数据!")
            return pd.DataFrame()
        
        print("正在分析商品关联规则...")
        start_time = datetime.now()
        
        # 只使用已完成的订单
        completed_orders = self.merged_data[self.merged_data['Status'] == '交易完成']
        
        if completed_orders.empty:
            print("没有找到已完成的订单")
            return pd.DataFrame()
        
        # 准备交易数据
        transaction_data = completed_orders.groupby('OrderID')['ProductName'].apply(list).reset_index(name='items')
        
        if transaction_data.empty:
            print("没有找到交易数据")
            return pd.DataFrame()
        
        # 转换格式
        te = TransactionEncoder()
        te_ary = te.fit(transaction_data['items']).transform(transaction_data['items'])
        df = pd.DataFrame(te_ary, columns=te.columns_)
        
        # 使用Apriori算法
        frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
        
        # 获取最常见的商品组合
        if not frequent_itemsets.empty:
            frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
            frequent_itemsets = frequent_itemsets[frequent_itemsets['length'] >= 2].sort_values('support', ascending=False)
            
            # 转换itemsets为可读字符串
            frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(
                lambda x: ", ".join(list(x))
            )
        else:
            print("没有找到频繁项集")
        
        print(f"关联分析完成! 耗时: {datetime.now()-start_time}")
        return frequent_itemsets.head(20)

    def category_analysis(self):
        """商品分类销量和销售额排名"""
        if self.merged_data.empty:
            print("警告: 没有可用的合并数据!")
            return {
                'category1': pd.DataFrame(),
                'category2': pd.DataFrame(),
                'category3': pd.DataFrame()
            }
        
        # 按一级分类统计
        cat1_stats = self.merged_data.groupby('Category1').agg(
            total_quantity=('Quantity', 'sum'),
            total_sales=('sales_amount', 'sum')
        ).reset_index()
        
        # 按二级分类统计
        cat2_stats = self.merged_data.groupby(['Category1', 'Category2']).agg(
            total_quantity=('Quantity', 'sum'),
            total_sales=('sales_amount', 'sum')
        ).reset_index()
        
        # 按三级分类统计
        cat3_stats = self.merged_data.groupby(['Category1', 'Category2', 'Category3']).agg(
            total_quantity=('Quantity', 'sum'),
            total_sales=('sales_amount', 'sum')
        ).reset_index()
        
        return {
            'category1': cat1_stats.sort_values('total_sales', ascending=False),
            'category2': cat2_stats.sort_values('total_sales', ascending=False),
            'category3': cat3_stats.sort_values('total_sales', ascending=False)
        }

    def filter_by_date(self, start_date, end_date):
        """按日期范围过滤数据 - 修复日期比较问题"""
        if self.merged_data.empty:
            return pd.DataFrame()
            
        data = self.merged_data.copy()
        
        # 确保所有日期都是 Timestamp 类型
        data['Created_time'] = pd.to_datetime(data['Created_time'])
        
        if start_date:
            # 将开始日期转换为 Timestamp
            start_dt = pd.to_datetime(start_date)
            data = data[data['Created_time'] >= start_dt]
            
        if end_date:
            # 将结束日期转换为 Timestamp 并加上一天，然后使用小于
            end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
            data = data[data['Created_time'] < end_dt]
            
        return data

    def visualize_sales(self, sales_data, top_n=10):
        """可视化销售数据"""
        if sales_data.empty:
            print("没有销售数据可用于可视化")
            return
            
        plt.figure(figsize=(14, 10))
        
        # 销售额TOP商品
        plt.subplot(2, 1, 1)
        top_sales = sales_data.sort_values('total_sales', ascending=False).head(top_n)
        if not top_sales.empty:
            sns.barplot(x='total_sales', y='ProductName', data=top_sales, palette='viridis')
            plt.title(f'销售额TOP{top_n}商品')
            plt.xlabel('销售额')
            plt.ylabel('商品名称')
        else:
            plt.text(0.5, 0.5, '没有销售数据', ha='center', va='center')
        
        # 销量TOP商品
        plt.subplot(2, 1, 2)
        top_quantity = sales_data.sort_values('total_quantity', ascending=False).head(top_n)
        if not top_quantity.empty:
            sns.barplot(x='total_quantity', y='ProductName', data=top_quantity, palette='magma')
            plt.title(f'销量TOP{top_n}商品')
            plt.xlabel('销量')
            plt.ylabel('')
        else:
            plt.text(0.5, 0.5, '没有销售数据', ha='center', va='center')
        
        plt.tight_layout()
        plt.savefig('product_sales_analysis.png')
        print("已保存销售分析图表: product_sales_analysis.png")

    def generate_report(self, start_date=None, end_date=None):
        """生成完整分析报告"""
        print("\n" + "="*50)
        print("开始生成商品分析报告")
        print("="*50)
        
        # 1. 销售分析
        sales_report = self.sales_analysis(start_date, end_date)
        print("\n=== 商品销售分析 ===")
        if not sales_report.empty:
            print(sales_report.head(10).to_string(index=False))
        else:
            print("没有销售数据")
        
        # 2. 取消率分析
        cancel_report = self.cancellation_analysis()
        print("\n=== 高取消率商品 ===")
        if not cancel_report.empty:
            print(cancel_report.head(10).to_string(index=False))
        else:
            print("没有高取消率商品")
        
        # 3. 关联分析
        association_report = self.association_analysis(min_support=0.005)
        print("\n=== 商品关联分析 ===")
        if not association_report.empty:
            print(association_report.head(10).to_string(index=False))
        else:
            print("没有找到有效的商品关联")
        
        # 4. 分类分析
        category_report = self.category_analysis()
        print("\n=== 一级分类销售额排名 ===")
        if not category_report['category1'].empty:
            print(category_report['category1'].head(10).to_string(index=False))
        else:
            print("没有分类数据")
        
        # 5. 可视化
        self.visualize_sales(sales_report)
        
        # 6. 生成建议
        recommendations = self.generate_recommendations(sales_report, cancel_report, association_report)
        print("\n=== 运营建议 ===")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
            
        # 保存报告到CSV
        if not sales_report.empty:
            sales_report.to_csv('product_sales_report.csv', index=False, encoding='utf_8_sig')
            print("已保存销售报告: product_sales_report.csv")
        if not cancel_report.empty:
            cancel_report.to_csv('high_cancel_products.csv', index=False, encoding='utf_8_sig')
            print("已保存高取消率商品报告: high_cancel_products.csv")
        if not association_report.empty:
            association_report.to_csv('product_associations.csv', index=False, encoding='utf_8_sig')
            print("已保存商品关联报告: product_associations.csv")
        
        print("\n报告生成完成!")

    def generate_recommendations(self, sales_data, cancel_data, assoc_data):
        """生成初步运营建议"""
        recommendations = []
        
        # 高取消率商品建议
        if not cancel_data.empty:
            top_cancel = cancel_data.head(3)['ProductName'].tolist()
            rec = f"高取消率商品({len(cancel_data)}款): 如{', '.join(top_cancel)} - 建议检查商品描述、库存状态和物流时效"
            recommendations.append(rec)
        else:
            recommendations.append("没有高取消率商品，商品取消率在正常范围内")
        
        # 热销商品建议
        if not sales_data.empty:
            top_sellers = sales_data.sort_values('total_sales', ascending=False).head(3)['ProductName'].tolist()
            recommendations.append(f"热销商品推荐: {', '.join(top_sellers)} - 建议增加库存和推广资源")
        else:
            recommendations.append("没有找到热销商品")
        
        # 关联分析建议
        if not assoc_data.empty:
            top_combo = assoc_data.iloc[0]['itemsets']
            rec = f"发现{len(assoc_data)}组商品关联组合 - 推荐促销组合: [{top_combo}]"
            recommendations.append(rec)
        else:
            recommendations.append("没有找到有效的商品关联组合")
        
        # 分类建议
        category_data = self.category_analysis()['category1']
        if not category_data.empty:
            top_category = category_data.head(1)['Category1'].values[0]
            recommendations.append(f"表现最佳品类: {top_category} - 建议加大该品类商品开发")
        else:
            recommendations.append("没有找到分类数据")
        
        return recommendations

if __name__ == "__main__":
    # 设置分析时间范围 (可选)
    start_date = '2025-06-01'
    end_date = '2025-07-01'
    
    # 初始化分析器
    try:
        analyzer = ProductAnalyzer(DB_CONFIG)
        # 生成完整报告
        analyzer.generate_report(start_date, end_date)
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保关闭数据库连接
        if 'analyzer' in locals() and hasattr(analyzer, 'connection'):
            analyzer.connection.close()
            print("数据库连接已关闭")