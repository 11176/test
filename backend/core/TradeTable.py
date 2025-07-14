import pandas as pd
import numpy as np
import re
from collections import Counter
import sqlite3
import mysql.connector
from mysql.connector import Error
from .config import Config
import pandas as pd
from contextlib import closing
import logging


class TradeAnalyzer:
    #数据库格式化 链接 查询
    def __init__(self):
        """初始化TradeProcessor实例"""
        # 从配置文件中加载数据库设置
        self.config = Config()
        
        # 设置默认值
        self.logger = logging.getLogger('TradeProcessor')
        self.logger.setLevel(logging.INFO)
        
        # 初始化缓存
        self._region_cache = None
        self._connection_pool = None

    def _create_connection(self):
        """创建MySQL数据库连接"""
        try:
            conn = mysql.connector.connect(
                host=self.config.MYSQL_HOST,
                port=self.config.MYSQL_PORT,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE
            )
            return conn
        except Error as e:
            raise RuntimeError(f"MySQL连接失败: {e}")

    def execute_query(self, query, params=None):
        """执行查询并返回结果"""
        try:
            with closing(self._create_connection()) as conn:
                with closing(conn.cursor(dictionary=True)) as cursor:
                    cursor.execute(query, params or ())
                    return cursor.fetchall()
        except Exception as e:
            print(f"查询执行失败: {e}")
            return []
    _df = None
    
    #时间类型转化
    @staticmethod
    def convert_to_datetime(time_str):
        """
        将样例时间字符串转换为datetime对象
        参数:
        time_str (str): 时间字符串，格式如 "2025/6/22 7:54"
        返回:
        pandas.Timestamp: 转换后的datetime对象
        说明:
        1. 支持单数字月份/日期/小时（如 "2025/6/22 7:54"）
        2. 如果输入为空字符串或None，返回NaT（Not a Time）
        3. 如果格式错误，返回NaT（Not a Time）
        """
        # 处理空值情况
        if not time_str or pd.isna(time_str):
            return pd.NaT
        try:
            # 直接使用pandas的to_datetime函数进行转换
            return pd.to_datetime(time_str, format='%Y/%m/%d %H:%M')
        except Exception as e:
            print(f"时间转换错误: {e}，输入值: '{time_str}'")
            return pd.NaT

    #下单次数获取
    @staticmethod
    def extract_order_count(value):
        """
        从各种格式的下单次数中提取数字
        参数:
        value: 原始值，可以是字符串、整数、浮点数等
        返回:
        int: 提取后的整数下单次数，无法提取时返回0
        """
        # 处理空值
        if pd.isna(value) or value is None:
            return 0

        # 尝试直接转换为整数
        try:
            return int(value)
        except (ValueError, TypeError):
            pass

        # 处理字符串格式
        if isinstance(value, str):
            # 移除空白字符
            cleaned = value.strip()

            # 1. 处理"第N次"格式
            if cleaned.startswith('第') and cleaned.endswith('次'):
                # 提取数字部分
                match = re.search(r'\d+', cleaned)
                if match:
                    return int(match.group(0))

            # 2. 处理纯中文数字格式
            chinese_numbers = {
                "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
                "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
                "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20,
                "廿一": 21, "廿二": 22, "廿三": 23, "廿四": 24, "廿五": 25,
                "廿六": 26, "廿七": 27, "廿八": 28, "廿九": 29, "三十": 30
            }

            # 检查是否包含中文数字
            for cn, num in chinese_numbers.items():
                if cn in cleaned:
                    return num

            # 3. 处理纯数字格式（可能有非数字字符）
            numbers = re.findall(r'\d+', cleaned)
            if numbers:
                return int(numbers[0])

        # 所有尝试都失败时返回0
        return 0
    
    #读取scv
    @classmethod
    def load_order_data(cls, file_path="D:\\GitWorkspace\\backend\\data\\订单信息列表.csv"):
        """
            从CSV文件加载订单数据，并使用自定义函数转换日期时间列
            参数:
            file_path (str): CSV文件路径，默认为"订单信息列表.csv"
            convert_to_datetime (function): 自定义日期时间转换函数
            返回:
            DataFrame: 格式化后的订单数据
            """

        columns_spec = {
            "订单号": str,
            "订单状态": str,
            "订单创建时间": "datetime64[ns]",
            "买家付款时间": "datetime64[ns]",
            "交易成功时间": "datetime64[ns]",
            "全部商品名称": str,
            "商品种类数": int,
            "订单商品总件数": int,
            "收货人省份": str,
            "买家昵称": str,
            "收货人城市": str,
            "收货人地区": str,
            "会员等级": str,
            "下单次数": int,
            "商品金额合计": float,
            "店铺优惠合计": float,
            "运费": float
        }

        # 读取CSV文件
        df = pd.read_csv(file_path,encoding='utf-8-sig')
        # 验证列是否存在
        required_columns = list(columns_spec.keys())
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"CSV文件中缺少必要列: {missing_columns}")

        # 确保所有列都存在（即使值为空）
        for col in required_columns:
            if col not in df.columns:
                df[col] = np.nan
        # 选择需要的列
        df = df[required_columns]

        # 使用自定义函数转换日期时间列
        datetime_columns = ["订单创建时间", "买家付款时间", "交易成功时间"]
        if callable(cls.convert_to_datetime):
            for col in datetime_columns:
                df[col] = df[col].apply(cls.convert_to_datetime)
        else:
            for col in datetime_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        # 特殊处理：下单次数列（提取数字）
        if "下单次数" in df.columns:
            df['下单次数'] = df['下单次数'].apply(cls.extract_order_count)

        # 数据类型转换（非日期列）
        for col, dtype in columns_spec.items():
            if dtype == "datetime64[ns]":
                continue  # 已处理
            elif dtype == float:
                # 处理金额列中的特殊字符
                df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
            else:
                try:
                    df[col] = df[col].astype(dtype)
                except Exception as e:
                    print(f"转换列 '{col}' 时出错: {e}")
                    # 尝试转换为字符串再转换
                    df[col] = df[col].astype(str).astype(dtype)
        # 数据清洗
        # 2. 地理位置处理
        for col in ['收货人省份', '收货人城市', '收货人地区']:
            df[col] = df[col].fillna('未知').str.strip()
        # 3. 订单状态处理
        df['订单状态'] = df['订单状态'].fillna('未知').str.strip()
        # 4. 数值列处理
        for col in ['商品种类数', '订单商品总件数', '下单次数', '商品金额合计', '运费']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. 确保日期列类型正确
        for col in datetime_columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                print(f"警告: 列 '{col}' 未能转换为datetime类型")
        if cls._df is None:
            cls._df = df
        return cls._df
    
    # 函数 地区聚类分析，包含省份/城市的畅销商品top5
    @staticmethod
    def location_cluster_analysis(df):
        """
        对地理位置信息进行多级聚类分析，并添加商品偏好分析
        参数:
        df (DataFrame): 包含地理位置和商品金额的数据表
        返回:
        dict: 包含三个层级的聚类分析结果
            - province_summary: 每个省份的总商品金额及前五商品
            - city_summary: 每个省份下城市的金额占比及前五商品
            - district_summary: 每个城市下地区的金额占比
        """
        # 预处理：拆分商品并提取商品名称和数量
        # 创建临时DataFrame用于商品分析
        temp_df = df[['订单号', '收货人省份', '收货人城市', '全部商品名称']].copy()

        # 拆分多个商品（按分号分割）
        temp_df['商品条目'] = temp_df['全部商品名称'].str.split(';')
        temp_df = temp_df.explode('商品条目')

        # 提取商品名称（第一个括号前的内容）和购买数量
        def extract_product_info(row):
            # 提取商品名称
            product_name = row.split('(')[0].strip()

            # 提取购买数量 - 使用正则表达式匹配最后括号中的数字
            quantity_match = re.search(r'\((\d+)[^\d]*\)$', row)
            quantity = int(quantity_match.group(1)) if quantity_match else 1

            return pd.Series([product_name, quantity])

        # 应用提取函数
        temp_df[['商品名称', '购买数量']] = temp_df['商品条目'].apply(extract_product_info)

        # 删除临时列
        temp_df = temp_df.drop(columns=['全部商品名称', '商品条目'])

        # 1. 省份级别的聚类分析
        province_summary = df.groupby('收货人省份')['商品金额合计'].sum().reset_index()
        province_summary = province_summary.rename(columns={'商品金额合计': '省份总金额'})
        province_summary = province_summary.sort_values('省份总金额', ascending=False)

        # 2. 城市级别的聚类分析
        province_total = df.groupby('收货人省份')['商品金额合计'].sum().rename('省份总金额')
        city_summary = df.groupby(['收货人省份', '收货人城市'])['商品金额合计'].sum().reset_index()
        city_summary = city_summary.rename(columns={'商品金额合计': '城市总金额'})
        city_summary = city_summary.merge(province_total, on='收货人省份')
        city_summary['城市占比'] = (city_summary['城市总金额'] / city_summary['省份总金额']).round(4)
        city_summary = city_summary.sort_values(['收货人省份', '城市占比'], ascending=[True, False])

        # 3. 地区级别的聚类分析（保持不变）
        city_total = df.groupby(['收货人省份', '收货人城市'])['商品金额合计'].sum().rename('城市总金额')
        district_summary = df.groupby(['收货人省份', '收货人城市', '收货人地区'])['商品金额合计'].sum().reset_index()
        district_summary = district_summary.rename(columns={'商品金额合计': '地区总金额'})
        district_summary = district_summary.merge(city_total, on=['收货人省份', '收货人城市'])
        district_summary['地区占比'] = (district_summary['地区总金额'] / district_summary['城市总金额']).round(4)
        district_summary = district_summary.sort_values(['收货人省份', '收货人城市', '地区占比'],
                                                        ascending=[True, True, False])

        # ================= 商品偏好分析（基于销售数量）=================
        # 辅助函数：获取前五畅销商品（基于销售数量）
        def get_top_products_by_quantity(group):
            # 按商品名称分组计算总销售数量
            product_sales = group.groupby('商品名称')['购买数量'].sum().reset_index()
            product_sales = product_sales.rename(columns={'购买数量': '总销售数量'})

            # 按销售数量降序排序并取前五
            top_products = product_sales.sort_values('总销售数量', ascending=False).head(5)

            # 创建格式化的商品列表：商品名称(销售数量)
            product_list = [f"{row['商品名称']}({row['总销售数量']})"
                            for _, row in top_products.iterrows()]

            return ', '.join(product_list)

        # 省份级别的商品偏好
        province_products = temp_df.groupby('收货人省份').apply(get_top_products_by_quantity).reset_index()
        province_products = province_products.rename(columns={0: '畅销商品'})
        province_summary = province_summary.merge(province_products, on='收货人省份', how='left')

        # 城市级别的商品偏好
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
        """获取地理位置分析结果"""
        return cls.location_cluster_analysis(cls._df)

