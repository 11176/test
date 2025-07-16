import sys
import pandas as pd
import numpy as np
import re
from config import Config
import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import warnings
import mysql.connector
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns



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


class TradeAnalyzer:
    """
    TradeAnalyzer：用于从数据库加载和分析订单交易数据
    """

    _df = None  # 缓存 DataFrame
    
    def __init__(self):
        """
        初始化 TradeAnalyzer：设置日志 & 创建 SQLAlchemy engine
        """
        self.config = Config()
        self.logger = logging.getLogger('TradeAnalyzer')
        self.logger.setLevel(logging.INFO)

        # 创建 SQLAlchemy engine（推荐方式）
        self.engine = create_engine(self.config.SQLALCHEMY_DATABASE_URI)

    @staticmethod
    def add_order_score(df):
        def calculate_order_score(row):
            # 1. 订单状态评分 (50%)
            if row['订单状态'] == '交易关闭':
                status_score = -100
            elif row['订单状态'] == '已发货' or row['订单状态'] == '待发货':
                status_score = 40  # 已发货订单获得较高基础分
            else:  # 交易完成
                # 计算订单完成周期(小时)
                if pd.isna(row['交易成功时间']) or pd.isna(row['订单创建时间']):
                    cycle_hours = 168  # 如果时间缺失，按最长时间处理
                else:
                    cycle_hours = (row['交易成功时间'] - row['订单创建时间']).total_seconds() / 3600
                # 基础分40分 + 速度加分0-10分
                status_score = 40 + 10 * (1 - min(1, cycle_hours / 168))

            # 2. 运费比例评分 (10%) 运费占比越高，订单质量越低
            if row['商品金额合计'] > 0:
                shipping_ratio = row['运费'] / row['商品金额合计']
                # 比例越高扣分越多
                shipping_score = -10 * min(1, shipping_ratio * 10)
            else:
                shipping_score = 0  # 商品金额为0时不计算比例

            # 3. 商品金额评分 (40%)
            amount = row['商品金额合计']
            if amount < 50:
                amount_score = 10
            elif amount < 100:
                amount_score = 20
            elif amount < 200:
                amount_score = 30
            elif amount < 300:
                amount_score = 40
            else:
                amount_score = 40
                # 超过300元部分奖励
                bonus = min(10, (amount - 300) // 100)
                amount_score += bonus

            # 综合评分
            total_score = status_score + shipping_score + amount_score

            # 对于已发货订单，增加额外潜力分
            if row['订单状态'] == '已发货':
                # 已发货订单可能成为高质量订单的潜力
                # 根据商品金额和运费比例给予额外潜力分(0-10分)
                potential_bonus = 0

                # 高金额潜力
                if amount > 200:
                    potential_bonus += 5
                elif amount > 100:
                    potential_bonus += 3

                # 低运费比例潜力
                if row['运费'] == 0:
                    potential_bonus += 3
                elif row['商品金额合计'] > 0 and (row['运费'] / row['商品金额合计']) < 0.05:
                    potential_bonus += 2

                total_score += min(10, potential_bonus)

            return round(total_score, 2)  # 保留两位小数

        # 应用评分函数
        df['订单质量评分'] = df.apply(calculate_order_score, axis=1)

        # 添加评分等级  根据不同评分区间给出评分 F D C B A S
        df['评分等级'] = pd.cut(df['订单质量评分'],
                                bins=[-float('inf'), -50, 0, 50, 70, 90, float('inf')],
                                labels=['F', 'D', 'C', 'B', 'A', 'S'],
                                right=False)

        return df
    
    @staticmethod
    def convert_to_datetime(value):
        """
        将字符串/数字转换为 pandas datetime
        """
        if not value or pd.isna(value):
            return pd.NaT
        try:
            return pd.to_datetime(value)
        except Exception:
            return pd.NaT

    @classmethod
    def load_order_data(cls):
        """
        从数据库加载订单数据，并格式化
        """
        config = Config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

        query = """
            SELECT
                o.OrderID as 订单号,
                o.Status as 订单状态,
                o.Created_time as 订单创建时间,
                o.Payment_time as 买家付款时间,
                o.Completed_time as 交易成功时间,
                o.AllProduct as 全部商品名称,
                o.Pdnumber as 商品种类数,
                o.Totalnumber as 订单商品总件数,
                o.Freight as 运费,
                o.Discount as 店铺优惠合计,
                o.TotalAmount as 商品金额合计,
                o.Customer_ID as 买家昵称,
                c.MemberLevel as 会员等级,
                c.order_count as 下单次数,
                c.Phone as 买家手机号,
                c.Remark as 买家备注,
                r.Province as 收货人省份,
                r.City as 收货人城市,
                r.District as 收货人地区
            FROM orders o
            LEFT JOIN region r ON o.RegionID = r.RegionID
            LEFT JOIN customer c ON o.Customer_ID = c.Customer_ID
        """

        try:
            df = pd.read_sql(query, engine)
        except Exception as e:
            print(f"数据加载失败: {e}")
            return pd.DataFrame()

        # 转换时间字段
        datetime_columns = ["订单创建时间", "买家付款时间", "交易成功时间"]
        for col in datetime_columns:
            df[col] = df[col].apply(cls.convert_to_datetime)

        # 数值列
        for col in ['商品种类数', '订单商品总件数', '商品金额合计', '运费', '店铺优惠合计', '下单次数']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 填充文本字段
        for col in ['收货人省份', '收货人城市', '收货人地区']:
                    if col in df.columns:
                        # 先转换为字符串，然后处理多种空值情况
                        df[col] = df[col].astype(str).replace(['nan', 'None', ''], '未知').str.strip()
        df = cls.add_order_score(df)
        if cls._df is None:
            cls._df = df
        return cls._df

    @staticmethod
    def location_cluster_analysis(df):
        """
        地区聚类分析，包含省份/城市/地区及畅销商品top5
        返回：
            dict: 包含 province_summary, city_summary, district_summary
        """
        # 拆分商品
        temp_df = df[['订单号', '收货人省份', '收货人城市', '全部商品名称']].copy()
        temp_df['商品条目'] = temp_df['全部商品名称'].str.split(';')
        temp_df = temp_df.explode('商品条目')

        # 提取商品名称 & 数量
        def extract_product_info(row):
            product_name = row.split('(')[0].strip()
            quantity_match = re.search(r'\((\d+)[^\d]*\)$', row)
            quantity = int(quantity_match.group(1)) if quantity_match else 1
            return pd.Series([product_name, quantity])

        temp_df[['商品名称', '购买数量']] = temp_df['商品条目'].apply(extract_product_info)

        # 省份汇总
        province_summary = df.groupby('收货人省份')['商品金额合计'].sum().reset_index()
        province_summary = province_summary.rename(columns={'商品金额合计': '省份总金额'})
        province_summary = province_summary.sort_values('省份总金额', ascending=False)

        # 城市汇总
        province_total = df.groupby('收货人省份')['商品金额合计'].sum().rename('省份总金额')
        city_summary = df.groupby(['收货人省份', '收货人城市'])['商品金额合计'].sum().reset_index()
        city_summary = city_summary.rename(columns={'商品金额合计': '城市总金额'})
        city_summary = city_summary.merge(province_total, on='收货人省份')
        city_summary['城市占比'] = (city_summary['城市总金额'] / city_summary['省份总金额']).round(4)
        city_summary = city_summary.sort_values(['收货人省份', '城市占比'], ascending=[True, False])

        # 地区汇总
        city_total = df.groupby(['收货人省份', '收货人城市'])['商品金额合计'].sum().rename('城市总金额')
        district_summary = df.groupby(['收货人省份', '收货人城市', '收货人地区'])['商品金额合计'].sum().reset_index()
        district_summary = district_summary.rename(columns={'商品金额合计': '地区总金额'})
        district_summary = district_summary.merge(city_total, on=['收货人省份', '收货人城市'])
        district_summary['地区占比'] = (district_summary['地区总金额'] / district_summary['城市总金额']).round(4)
        district_summary = district_summary.sort_values(['收货人省份', '收货人城市', '地区占比'],
                                                        ascending=[True, True, False])

        # 畅销商品 top5
        def get_top_products_by_quantity(group):
            product_sales = group.groupby('商品名称')['购买数量'].sum().reset_index()
            top_products = product_sales.sort_values('购买数量', ascending=False).head(5)
            return ', '.join(f"{row['商品名称']}({row['购买数量']})" for _, row in top_products.iterrows())

        # 省份畅销
        province_products = temp_df.groupby('收货人省份').apply(get_top_products_by_quantity).reset_index()
        province_products = province_products.rename(columns={0: '畅销商品'})
        province_summary = province_summary.merge(province_products, on='收货人省份', how='left')

        # 城市畅销
        city_products = temp_df.groupby(['收货人省份', '收货人城市']).apply(get_top_products_by_quantity).reset_index()
        city_products = city_products.rename(columns={0: '畅销商品'})
        city_summary = city_summary.merge(city_products, on=['收货人省份', '收货人城市'], how='left')

        return {
            'province_summary': province_summary,
            'city_summary': city_summary,
            'district_summary': district_summary
        }

    @classmethod
    def get_location_analysis(cls):
        """
        调用 location_cluster_analysis 返回聚类分析结果
        """
        return cls.location_cluster_analysis(cls._df)

    @staticmethod
    def process_user_profiles(df):
        def extract_product_info(row):
            # 提取商品名称
            product_name = row.split('(')[0].strip()
            # 提取购买数量 - 使用正则表达式匹配最后括号中的数字
            quantity_match = re.search(r'\((\d+)[^\d]*\)$', row)
            quantity = int(quantity_match.group(1)) if quantity_match else 1
            return pd.Series([product_name, quantity])
        # 预处理：只保留非订单关闭的记录用于金额计算
        valid_orders = df[df['订单状态'] != '交易关闭'].copy()

        # 1. 按买家昵称分组，计算基本统计信息
        user_stats = valid_orders.groupby('买家昵称').agg({
            '订单号': 'count',
            '商品金额合计': 'sum',
            '订单创建时间': ['min', 'max'],
            '订单质量评分': 'mean',
            '收货人省份': 'last',
            '收货人城市': 'last',
            '收货人地区': 'last',
            '会员等级': 'last',
            '买家手机号': 'last'
        })

        # 扁平化多级列索引
        user_stats.columns = ['_'.join(col).strip() for col in user_stats.columns.values]
        user_stats = user_stats.rename(columns={
            '订单号_count': '有效订单数',
            '商品金额合计_sum': '总消费金额',
            '订单创建时间_min': '首次下单时间',
            '订单创建时间_max': '最近下单时间',
            '订单质量评分_mean': '平均订单质量',
            '收货人省份_last': '省份',
            '收货人城市_last': '城市',
            '收货人地区_last': '地区',
            '会员等级_last': '最新会员等级',
            '买家手机号_last': '手机号'
        })

        # 2.
        valid_order_counts = df.groupby('买家昵称')['订单号'].count()
        user_stats['订单总数'] = valid_order_counts

        # 3. 处理地址信息
        user_stats['完整地址'] = user_stats['省份'] + user_stats['城市'] + user_stats['地区']

        # 4. 处理手机号脱敏
        user_stats['脱敏手机号'] = user_stats['手机号'].apply(
            lambda x: str(x)[:3] + '****' + str(x)[-4:] if pd.notnull(x) else '')

        # 5. 提取偏好商品（购买数量最多的前三种商品）
        # 首先展开所有商品
        product_data = []
        for _, row in df.iterrows():
            products = row['全部商品名称'].split(';')
            for product in products:
                product_name, quantity = extract_product_info(product)
                product_data.append({
                    '买家昵称': row['买家昵称'],
                    '商品名称': product_name,
                    '购买数量': quantity
                })

        product_df = pd.DataFrame(product_data)

        # 按用户和商品分组，计算总购买数量
        user_products = product_df.groupby(['买家昵称', '商品名称'])['购买数量'].sum().reset_index()

        # 对每个用户，获取购买数量最多的前3种商品
        top_products = user_products.sort_values(['买家昵称', '购买数量'], ascending=[True, False]) \
            .groupby('买家昵称') \
            .head(3) \
            .groupby('买家昵称')['商品名称'] \
            .apply(lambda x: '、'.join(x)) \
            .reset_index() \
            .rename(columns={'商品名称': '偏好商品'})

        # 合并到用户统计信息
        user_stats = user_stats.merge(top_products, on='买家昵称', how='left')

        # 6. 计算RFM得分（简化版）
        # 这里只是一个示例，实际RFM计算可能需要更复杂的逻辑
        today = df['订单创建时间'].max()
        rfm = valid_orders.groupby('买家昵称').agg({
            '订单创建时间': lambda x: (today - x.max()).days,
            '订单号': 'count',
            '商品金额合计': 'sum'
        }).rename(columns={
            '订单创建时间': 'Recency',
            '订单号': 'Frequency',
            '商品金额合计': 'Monetary'
        })

        # 分位数评分（1-3分）
        rfm['R_score'] = pd.qcut(rfm['Recency'], 3, labels=[3, 2, 1])
        rfm['F_score'] = pd.cut(rfm['Frequency'], 2, labels=[1,2])
        rfm['M_score'] = pd.qcut(rfm['Monetary'], 3, labels=[1, 2, 3])

        rfm['RFM_score'] = rfm['R_score'].astype(int) + rfm['F_score'].astype(int) + rfm['M_score'].astype(int)

        # 合并RFM得分
        user_stats = user_stats.merge(rfm[['RFM_score']], on='买家昵称', how='left')

        # 7. 重置索引并添加真实姓名（这里假设真实姓名就是买家昵称，可以根据实际情况调整）
        user_stats = user_stats.reset_index()

        # 8. 按要求的列顺序排列
        columns_order = [
            '买家昵称', '脱敏手机号', '手机号', '最新会员等级',
            '省份', '城市', '地区', '完整地址',
            '首次下单时间', '最近下单时间', '订单总数', '有效订单数', '总消费金额',
            '平均订单质量', '偏好商品', 'RFM_score'
        ]

        return user_stats[columns_order]

    @classmethod
    def get_user_profiles(cls):
        return cls.process_user_profiles(cls._df)


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
        
        print(f"数据加载完成! 共加载 {len(self.merged_data)} 条记录")

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