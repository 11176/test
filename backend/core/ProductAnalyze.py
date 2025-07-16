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
import sys

pd.set_option("display.max_rows", None)  # 显示所有行
pd.set_option("display.max_columns", None)  # 显示所有列
pd.set_option("display.width", None)  # 自动调整列宽（避免换行）
pd.set_option("display.max_colwidth", None)  # 显示完整列内容（不截断文本）

# 忽略警告信息
warnings.filterwarnings('ignore', category=UserWarning)

# 尝试从config.py导入配置
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import MYSQL_CONFIG, ANALYSIS_CONFIG, DATA_SOURCE
    print("配置文件加载成功!")
except ImportError:
    print("警告: 未找到配置文件，使用默认配置")
    # 默认配置
    MYSQL_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '13579OKOK',
        'database': 'trade_db',
        'charset': 'utf8mb4'
    }
    
    ANALYSIS_CONFIG = {
        'top_n_products': 10,
        'slow_moving_threshold': 0.1,
        'min_support': 0.005,
        'cancellation_rate_multiplier': 1.5,
        'profit_margin_threshold': 0.3,
        'return_rate_threshold': 0.1,
        'sales_frequency_threshold': 0.01
    }
    
    DATA_SOURCE = 'database'  #'database'

# 项目目录结构（修正路径计算）
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_DIR, 'input')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')

# 确保目录存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)


class ProductAnalyzer:
    def __init__(self, data_source=DATA_SOURCE, csv_dir=INPUT_DIR):
        """
        初始化分析器
        :param data_source: 数据源类型 - 'database' 或 'csv'
        :param csv_dir: CSV文件目录（当data_source='csv'时使用）
        """
        self.data_source = data_source
        self.csv_dir = csv_dir
        self.config = ANALYSIS_CONFIG
        
        if data_source == 'database':
            self.connect_to_database()
        elif data_source == 'csv':
            print(f"使用CSV数据源，目录: {self.csv_dir}")
        else:
            raise ValueError("不支持的data_source参数，请使用'database'或'csv'")
            
        self.load_data()
        
    def connect_to_database(self):
        """连接数据库"""
        try:
            self.connection = mysql.connector.connect(**MYSQL_CONFIG)
            print("数据库连接成功!")
        except mysql.connector.Error as err:
            print(f"数据库连接失败: {err}")
            print("请检查您的数据库配置:")
            print(f"主机: {MYSQL_CONFIG['host']}")
            print(f"端口: {MYSQL_CONFIG['port']}")
            print(f"用户名: {MYSQL_CONFIG['user']}")
            print(f"数据库: {MYSQL_CONFIG['database']}")
            print("密码是否正确？数据库是否运行中？")
            exit(1)

    def load_from_database(self):
        """从数据库加载数据"""
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
        
    def load_from_csv(self):
        """从CSV文件加载数据"""
        # 加载订单数据
        orders_path = os.path.join(self.csv_dir, 'orders.csv')
        if os.path.exists(orders_path):
            self.orders = pd.read_csv(orders_path)
        else:
            raise FileNotFoundError(f"订单数据文件不存在: {orders_path}")
        
        # 加载订单商品项数据
        order_items_path = os.path.join(self.csv_dir, 'order_items.csv')
        if os.path.exists(order_items_path):
            self.order_items = pd.read_csv(order_items_path)
        else:
            raise FileNotFoundError(f"订单商品项数据文件不存在: {order_items_path}")
        
        # 检查是否有数据
        if self.orders.empty or self.order_items.empty:
            print("警告: 加载的数据为空!")
            print(f"订单记录数: {len(self.orders)}")
            print(f"订单商品项记录数: {len(self.order_items)}")

    def load_data(self):
        """从数据源加载所需数据"""
        print("正在加载数据...")
        start_time = datetime.now()
        
        if self.data_source == 'database':
            self.load_from_database()
        elif self.data_source == 'csv':
            self.load_from_csv()
        
        # 合并订单和商品数据
        self.merged_data = pd.merge(
            self.order_items,
            self.orders[['OrderID', 'Status', 'Created_time']],
            on='OrderID',
            how='inner'
        )
        
        # 处理时间字段
        self.merged_data['Created_time'] = pd.to_datetime(self.merged_data['Created_time'])
        self.merged_data['order_hour'] = self.merged_data['Created_time'].dt.hour
        self.merged_data['order_date'] = self.merged_data['Created_time'].dt.date
        
        # 计算销售额
        self.merged_data['sales_amount'] = self.merged_data['Quantity'] * self.merged_data['Price']
        
        print(f"数据加载完成! 共加载 {len(self.merged_data)} 条记录, 耗时: {datetime.now()-start_time}")

    def sales_analysis(self):
        """商品销量与销售额统计"""
        # 筛选时间范围
        data = self.merged_data
        
        if data.empty:
            print("警告: 没有数据!")
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
        """按日期范围过滤数据"""
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
        
        # 获取配置参数
        multiplier = self.config.get('cancellation_rate_multiplier', 1.5)
        
        # 识别高取消率商品（高于平均取消率）
        if not cancel_rates.empty:
            avg_rate = cancel_rates['cancellation_rate'].mean()
            high_cancel = cancel_rates[cancel_rates['cancellation_rate'] > avg_rate * multiplier]
        else:
            high_cancel = pd.DataFrame()
        
        # 添加商品名称
        if not high_cancel.empty:
            product_names = self.merged_data[['ProductID', 'ProductName']].drop_duplicates()
            result = pd.merge(high_cancel, product_names, on='ProductID')
            
            # 添加取消率百分比列
            result['cancellation_rate_pct'] = result['cancellation_rate'].apply(
                lambda x: f"{x:.2%}"
            )
            
            # 选择并重命名列
            result = result[[
                'ProductID', 'ProductName', 'total_orders', 
                'canceled_orders', 'cancellation_rate_pct'
            ]]
            result.rename(columns={
                'total_orders': '总订单数',
                'canceled_orders': '取消订单数',
                'cancellation_rate_pct': '取消率'
            }, inplace=True)
            
            return result.sort_values('取消率', ascending=False)
        else:
            return pd.DataFrame()

    def association_analysis(self, min_support=None):
        """商品关联分析"""
        if self.merged_data.empty:
            print("警告: 没有可用的合并数据!")
            return pd.DataFrame()
        
        # 使用配置参数
        if min_support is None:
            min_support = self.config.get('min_support', 0.01)
        
        print(f"正在分析商品关联规则 (最小支持度: {min_support})...")
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
            
            # 计算支持度百分比
            frequent_itemsets['support_pct'] = frequent_itemsets['support'].apply(
                lambda x: f"{x:.2%}"
            )
            
            # 选择并重命名列
            result = frequent_itemsets[['itemsets', 'length', 'support_pct']]
            result.rename(columns={
                'itemsets': '商品组合',
                'length': '组合商品数量',
                'support_pct': '支持度'
            }, inplace=True)
        else:
            print("没有找到频繁项集")
            result = pd.DataFrame()
        
        print(f"关联分析完成! 耗时: {datetime.now()-start_time}")
        return result.head(20)

    def visualize_sales(self, sales_data, top_n=None):
        """可视化销售数据"""
        # 使用配置参数
        if top_n is None:
            top_n = self.config.get('top_n_products', 10)
        
        if sales_data.empty:
            print("没有销售数据可用于可视化")
            return
            
        plt.figure(figsize=(14, 10))
        
        # 销售额TOP商品
        plt.subplot(2, 1, 1)
        top_sales = sales_data.sort_values('total_sales', ascending=False).head(top_n)
        if not top_sales.empty:
            sns.barplot(
                x='total_sales', 
                y='ProductName', 
                data=top_sales, 
                hue='ProductName',
                palette='viridis',
                legend=False,
                dodge=False
            )
            plt.title(f'销售额TOP{top_n}商品')
            plt.xlabel('销售额')
            plt.ylabel('商品名称')
            
            # 添加数据标签
            for i, v in enumerate(top_sales['total_sales']):
                plt.text(v + 3, i, f"¥{v:.2f}", va='center')
        else:
            plt.text(0.5, 0.5, '没有销售数据', ha='center', va='center')
        
        # 销量TOP商品
        plt.subplot(2, 1, 2)
        top_quantity = sales_data.sort_values('total_quantity', ascending=False).head(top_n)
        if not top_quantity.empty:
            sns.barplot(
                x='total_quantity', 
                y='ProductName', 
                data=top_quantity, 
                hue='ProductName',
                palette='magma',
                legend=False,
                dodge=False
            )
            plt.title(f'销量TOP{top_n}商品')
            plt.xlabel('销量')
            plt.ylabel('')
            
            # 添加数据标签
            for i, v in enumerate(top_quantity['total_quantity']):
                plt.text(v + 0.5, i, f"{v:.0f}", va='center')
        else:
            plt.text(0.5, 0.5, '没有销售数据', ha='center', va='center')
        
        plt.tight_layout()
        
        # 添加时间戳到文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_path = os.path.join(CHARTS_DIR, f'product_sales_analysis_{timestamp}.png')
        plt.savefig(chart_path, bbox_inches='tight', dpi=300)
        print(f"已保存销售分析图表: {chart_path}")

    def health_analysis(self):
        """商品健康度分析"""
        if self.merged_data.empty:
            print("警告: 没有可用的合并数据!")
            return pd.DataFrame()
        
        print("正在进行商品健康度分析...")
        start_time = datetime.now()
        
        # 获取配置参数
        profit_threshold = self.config.get('profit_margin_threshold', 0.3)
        return_threshold = self.config.get('return_rate_threshold', 0.1)
        sales_freq_threshold = self.config.get('sales_frequency_threshold', 0.01)
        
        # 计算基础销售指标
        sales_stats = self.merged_data.groupby(['ProductID', 'ProductName']).agg(
            total_quantity=('Quantity', 'sum'),
            total_sales=('sales_amount', 'sum'),
            total_cost=('Quantity', lambda x: (x * self.merged_data.loc[x.index, 'Price'] * 0.7).sum()),  # 假设成本是售价的70%
            order_count=('OrderID', 'nunique')
        ).reset_index()
        
        # 计算利润率
        sales_stats['profit_margin'] = (sales_stats['total_sales'] - sales_stats['total_cost']) / sales_stats['total_sales']
        
        # 模拟退货率数据（实际项目中应从退货数据计算）
        np.random.seed(42)
        sales_stats['return_rate'] = np.random.uniform(0, 0.2, len(sales_stats))
        
        # 计算动销率（销售天数占总天数的比例）
        # 实际项目中需要更精确的计算
        sales_stats['sales_frequency'] = sales_stats['order_count'] / sales_stats['order_count'].sum()
        
        # 健康度评估
        conditions = [
            # 健康商品：高利润、低退货率、高动销率
            (sales_stats['profit_margin'] >= profit_threshold) &
            (sales_stats['return_rate'] <= return_threshold) &
            (sales_stats['sales_frequency'] >= sales_freq_threshold),
            
            # 问题商品：低利润、高退货率、低动销率
            (sales_stats['profit_margin'] < profit_threshold) &
            (sales_stats['return_rate'] > return_threshold) &
            (sales_stats['sales_frequency'] < sales_freq_threshold),
            
            # 高毛利滞销品：高利润但低动销率
            (sales_stats['profit_margin'] >= profit_threshold) &
            (sales_stats['sales_frequency'] < sales_freq_threshold),
            
            # 引流商品：低利润但高动销率
            (sales_stats['profit_margin'] < profit_threshold) &
            (sales_stats['sales_frequency'] >= sales_freq_threshold)
        ]
        
        choices = ['健康商品', '问题商品', '高毛利滞销品', '引流商品']
        sales_stats['health_status'] = np.select(conditions, choices, default='一般商品')
        
        # 格式化指标
        sales_stats['profit_margin_pct'] = sales_stats['profit_margin'].apply(lambda x: f"{x:.2%}")
        sales_stats['return_rate_pct'] = sales_stats['return_rate'].apply(lambda x: f"{x:.2%}")
        sales_stats['sales_frequency_pct'] = sales_stats['sales_frequency'].apply(lambda x: f"{x:.2%}")
        
        # 选择并重命名列
        result = sales_stats[[
            'ProductID', 'ProductName', 'total_quantity', 'total_sales',
            'profit_margin_pct', 'return_rate_pct', 'sales_frequency_pct', 'health_status'
        ]]
        result.rename(columns={
            'ProductID': '商品ID',
            'ProductName': '商品名称',
            'total_quantity': '总销量',
            'total_sales': '总销售额',
            'profit_margin_pct': '利润率',
            'return_rate_pct': '退货率',
            'sales_frequency_pct': '动销率',
            'health_status': '健康状态'
        }, inplace=True)
        
        print(f"健康度分析完成! 耗时: {datetime.now()-start_time}")
        return result.sort_values('总销售额', ascending=False)

    def generate_report(self, start_date=None, end_date=None):
        """生成完整分析报告"""
        print("\n" + "="*50)
        print(f"开始生成商品分析报告 (时间范围: {start_date or '全部'} 至 {end_date or '全部'})")
        print("="*50)
        
        # 添加时间戳到文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
        
        # 3. 关联分析 - 使用配置参数
        association_report = self.association_analysis(
            min_support=self.config.get('min_support', 0.005)
        )
        print("\n=== 商品关联分析 ===")
        if not association_report.empty:
            print(association_report.head(10).to_string(index=False))
        else:
            print("没有找到有效的商品关联")
        
        # 4. 健康度分析
        health_report = self.health_analysis()
        print("\n=== 商品健康度分析 ===")
        if not health_report.empty:
            print(health_report.head(10).to_string(index=False))
        else:
            print("没有健康度数据")
        
        # 5. 分类分析
        category_report = self.category_analysis()
        print("\n=== 一级分类销售额排名 ===")
        if not category_report['category1'].empty:
            print(category_report['category1'].head(10).to_string(index=False))
        else:
            print("没有分类数据")
        
        # 6. 可视化
        self.visualize_sales(sales_report)
        
        # 7. 生成建议
        recommendations = self.generate_recommendations(sales_report, cancel_report, association_report, health_report)
        print("\n=== 运营建议 ===")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # 保存报告到CSV
        if not sales_report.empty:
            sales_path = os.path.join(REPORTS_DIR, f'product_sales_report_{timestamp}.csv')
            sales_report.to_csv(sales_path, index=False, encoding='utf_8_sig')
            print(f"已保存销售报告: {sales_path}")
        if not cancel_report.empty:
            cancel_path = os.path.join(REPORTS_DIR, f'high_cancel_products_{timestamp}.csv')
            cancel_report.to_csv(cancel_path, index=False, encoding='utf_8_sig')
            print(f"已保存高取消率商品报告: {cancel_path}")
        if not association_report.empty:
            assoc_path = os.path.join(REPORTS_DIR, f'product_associations_{timestamp}.csv')
            association_report.to_csv(assoc_path, index=False, encoding='utf_8_sig')
            print(f"已保存商品关联报告: {assoc_path}")
        if not health_report.empty:
            health_path = os.path.join(REPORTS_DIR, f'product_health_report_{timestamp}.csv')
            health_report.to_csv(health_path, index=False, encoding='utf_8_sig')
            print(f"已保存商品健康度报告: {health_path}")
        
        # 生成报告摘要
        self.generate_summary_report(sales_report, cancel_report, association_report, health_report, timestamp)
        
        print("\n报告生成完成!")

    def generate_recommendations(self, sales_data, cancel_data, assoc_data, health_data):
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
            top_combo = assoc_data.iloc[0]['商品组合']
            rec = f"发现{len(assoc_data)}组商品关联组合 - 推荐促销组合: [{top_combo}]"
            recommendations.append(rec)
        else:
            recommendations.append("没有找到有效的商品关联组合")
        
        # 健康度分析建议
        if not health_data.empty:
            # 问题商品建议
            problem_products = health_data[health_data['健康状态'] == '问题商品']
            if not problem_products.empty:
                rec = f"问题商品({len(problem_products)}款): 建议优化包装、加强质检或调整定价"
                recommendations.append(rec)
            
            # 高毛利滞销品建议
            high_profit_slow = health_data[health_data['健康状态'] == '高毛利滞销品']
            if not high_profit_slow.empty:
                rec = f"高毛利滞销品({len(high_profit_slow)}款): 建议制作试用装、增加曝光或捆绑销售"
                recommendations.append(rec)
            
            # 引流商品建议
            traffic_products = health_data[health_data['健康状态'] == '引流商品']
            if not traffic_products.empty:
                rec = f"引流商品({len(traffic_products)}款): 建议作为促销活动主力商品"
                recommendations.append(rec)
        
        # 分类建议
        category_data = self.category_analysis()['category1']
        if not category_data.empty:
            top_category = category_data.head(1)['Category1'].values[0]
            recommendations.append(f"表现最佳品类: {top_category} - 建议加大该品类商品开发")
        else:
            recommendations.append("没有找到分类数据")
        
        return recommendations

    def generate_summary_report(self, sales_data, cancel_data, assoc_data, health_data, timestamp):
        """生成报告摘要文件"""
        summary = []
        
        # 报告标题
        summary.append(f"商品分析报告摘要 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("=" * 60)
        
        # 销售概况
        if not sales_data.empty:
            total_sales = sales_data['total_sales'].sum()
            total_quantity = sales_data['total_quantity'].sum()
            top_product = sales_data.iloc[0]['ProductName']
            top_sales = sales_data.iloc[0]['total_sales']
            
            summary.append("\n销售概况:")
            summary.append(f"- 总销售额: ¥{total_sales:.2f}")
            summary.append(f"- 总销量: {total_quantity} 件")
            summary.append(f"- 最畅销商品: {top_product} (¥{top_sales:.2f})")
        else:
            summary.append("\n销售概况: 无数据")
        
        # 高取消率商品
        if not cancel_data.empty:
            top_cancel = cancel_data.iloc[0]['ProductName']
            cancel_rate = cancel_data.iloc[0]['取消率']
            
            summary.append("\n高取消率商品:")
            summary.append(f"- 最高取消率商品: {top_cancel} ({cancel_rate})")
            summary.append(f"- 高取消率商品总数: {len(cancel_data)}")
        else:
            summary.append("\n高取消率商品: 无")
        
        # 商品关联
        if not assoc_data.empty:
            top_combo = assoc_data.iloc[0]['商品组合']
            support = assoc_data.iloc[0]['支持度']
            
            summary.append("\n商品关联分析:")
            summary.append(f"- 最强关联组合: {top_combo} (支持度: {support})")
            summary.append(f"- 有效关联组合数: {len(assoc_data)}")
        else:
            summary.append("\n商品关联分析: 无有效关联")
        
        # 健康度分析
        if not health_data.empty:
            health_counts = health_data['健康状态'].value_counts().to_dict()
            
            summary.append("\n商品健康度分析:")
            for status, count in health_counts.items():
                summary.append(f"- {status}: {count}款")
        else:
            summary.append("\n商品健康度分析: 无数据")
        
        # 保存摘要文件
        summary_path = os.path.join(REPORTS_DIR, f'report_summary_{timestamp}.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(summary))
        
        print(f"已保存报告摘要: {summary_path}")


if __name__ == "__main__":
    try:
        analyzer = ProductAnalyzer(data_source=DATA_SOURCE)
        analyzer.load_data()
        df = analyzer.sales_analysis()
        print(df)

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保关闭数据库连接（如果是数据库连接）
        if hasattr(analyzer, 'connection') and analyzer.connection:
            analyzer.connection.close()
            print("数据库连接已关闭")