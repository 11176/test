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
import os

class TradeAnalyzer:
    '''
    # 数据库格式化 链接 查询
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
    '''
    _df = None
    # 时间类型转化
    @staticmethod
    def convert_to_datetime(time_str):
        # 处理空值情况
        if not time_str or pd.isna(time_str):
            return pd.NaT
        try:
            # 直接使用pandas的to_datetime函数进行转换2025/6/5  21:14:08
            return pd.to_datetime(time_str)
        except Exception as e:
            print(f"时间转换错误: {e}，输入值: '{time_str}'")
            return pd.NaT
    
    # 下单次数获取
    @staticmethod
    def extract_order_count(value):
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
    
    # 读取scv
    @classmethod
    def load_order_data(cls, file_path=None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "订单信息列表.csv")
        columns_spec = {
            "订单号": str,  # 字符串类型（长订单号）
            "订单状态": str,  # 字符串类型（交易完成，交易关闭，已发货，待发货）
            "订单创建时间": "datetime64[ns]",  # 日期时间类型
            "买家付款时间": "datetime64[ns]",  # 日期时间类型
            "交易成功时间": "datetime64[ns]",  # 日期时间类型
            "全部商品名称": str,  # 字符串（多商品用分号分隔）
            "商品种类数": int,  # 整数类型
            "订单商品总件数": int,  # 整数类型
            "收货人省份": str,  # 字符串类型
            "买家昵称": str,  # 字符串类型（姓名）
            "收货人城市": str,  # 字符串类型
            "收货人地区": str,  # 字符串类型（区/县）
            "会员等级": str,  # 字符串类型（如：黄金、钻石等）
            "下单次数": int,  # 整数类型（需从"第N次"提取数字）
            "商品金额合计": float,  # 浮点数类型（金额）
            "运费": float,  # 浮点数类型（金额）
            "买家手机号": str,  # 字符串类型
            "买家备注": str,  # 字符串类型
        }

        # 读取CSV文件
        df = pd.read_csv(file_path, encoding='utf-8-sig')
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
        for col in datetime_columns:
            df[col] = df[col].apply(cls.convert_to_datetime)
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
            if col in df.columns:
                # 先转换为字符串，然后处理多种空值情况
                df[col] = df[col].astype(str).replace(['nan', 'None', ''], '未知').str.strip()
        # 3. 订单状态处理
        df['订单状态'] = df['订单状态'].fillna('交易关闭').str.strip()
        # 4. 数值列处理
        for col in ['商品种类数', '订单商品总件数', '下单次数', '商品金额合计', '运费']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. 确保日期列类型正确
        for col in datetime_columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                print(f"警告: 列 '{col}' 未能转换为datetime类型")
        df = cls.add_order_score(df)
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
