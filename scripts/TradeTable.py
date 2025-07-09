import pandas as pd
import numpy as np
import re
from collections import Counter


#函数 时间类型转换 用于excel读取时间数据：
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


#函数 地区聚类分析，包含省份/城市的畅销商品top5
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


#函数 订单分析 根据订单状态，订单金额，订单完成时间，运费计算订单的优质程度
def calculate_order_score(row):
    """
    计算订单质量综合评分
    参数:
    row: DataFrame的行数据，包含订单相关信息
    返回:
    float: 订单质量评分
    """
    # 1. 订单状态评分 (50%)
    if row['订单状态'] == '交易取消':
        status_score = -100
    elif row['订单状态'] == '已发货':
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


# 应用评分函数到整个DataFrame
def add_order_score(df):
    """
    为DataFrame添加订单质量评分列
    参数:
    df: 包含订单数据的DataFrame
    返回:
    DataFrame: 添加了'订单质量评分'列的数据
    """
    # 应用评分函数
    df['订单质量评分'] = df.apply(calculate_order_score, axis=1)

    # 添加评分等级  根据不同评分区间给出评分 F D C B A S
    df['评分等级'] = pd.cut(df['订单质量评分'],
                            bins=[-float('inf'), -50, 0, 50, 70, 90, float('inf')],
                            labels=['F', 'D', 'C', 'B', 'A', 'S'],
                            right=False)

    return df


#构建用户画像
def build_basic_user_profile(df):
    """
    基于订单信息表构建用户基础画像，包含用户偏好商品分析
    参数:
    df (DataFrame): 包含用户订单信息的数据表
    返回:
    DataFrame: 包含用户基础画像的数据表，每行代表一个用户
    """
    # 确保必要的列存在
    required_columns = ['收货人/提货人', '买家手机号', '会员等级',
                        '收货人省份', '收货人城市', '收货人地区', '订单创建时间',
                        '下单次数', '商品金额合计', '订单质量评分', '全部商品名称']

    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"数据表缺少必要列: {missing}")

    # 1. 预处理：拆分商品并提取商品名称和数量
    temp_df = df[['买家手机号', '全部商品名称']].copy()

    # 拆分多个商品（按分号分割）
    temp_df['商品条目'] = temp_df['全部商品名称'].str.split(';')
    temp_df = temp_df.explode('商品条目')

    # 提取商品名称和购买数量
    def extract_product_info(row):
        # 提取商品名称
        product_name = row.split('(')[0].strip()

        # 提取购买数量 - 使用正则表达式匹配最后括号中的数字
        quantity_match = re.search(r'\((\d+)[^\d]*\)$', row)
        quantity = int(quantity_match.group(1)) if quantity_match else 1

        return pd.Series([product_name, quantity])

    # 应用提取函数
    temp_df[['商品名称', '购买数量']] = temp_df['商品条目'].apply(extract_product_info)

    # 2. 计算每个用户的偏好商品
    # 按用户和商品分组，计算每个用户购买每个商品的总数量
    user_product_sales = temp_df.groupby(['买家手机号', '商品名称'])['购买数量'].sum().reset_index()

    # 对每个用户按购买数量排序，获取前三商品
    user_top_products = user_product_sales.groupby('买家手机号').apply(
        lambda x: x.sort_values('购买数量', ascending=False).head(3)
    ).reset_index(drop=True)

    # 将前三商品格式化为字符串：商品A(数量), 商品B(数量), 商品C(数量)
    user_top_products_str = user_top_products.groupby('买家手机号').apply(
        lambda x: ', '.join([f"{row['商品名称']}({row['购买数量']})"
                             for _, row in x.iterrows()])
    ).reset_index()
    user_top_products_str.columns = ['买家手机号', '偏好商品']

    # 3. 创建用户画像数据
    user_profile = df.groupby('买家手机号').apply(
        lambda x: pd.Series({
            '姓名': x['收货人/提货人'].iloc[0],  # 取第一次出现的姓名
            '手机号': x['买家手机号'].iloc[0],
            '最新会员等级': x.sort_values('订单创建时间', ascending=False)['会员等级'].iloc[0],
            '省份': x.sort_values('订单创建时间', ascending=False)['收货人省份'].iloc[0],
            '城市': x.sort_values('订单创建时间', ascending=False)['收货人城市'].iloc[0],
            '地区': x.sort_values('订单创建时间', ascending=False)['收货人地区'].iloc[0],
            '完整地址': f"{x['收货人省份'].iloc[0]}{x['收货人城市'].iloc[0]}{x['收货人地区'].iloc[0]}",
            '首次下单时间': x['订单创建时间'].min(),
            '最近下单时间': x['订单创建时间'].max(),
            '订单总数': x['下单次数'].max(),
            '总消费金额': x['商品金额合计'].sum(),
            '平均订单质量': x['订单质量评分'].mean(),
        })
    ).reset_index(drop=True)

    # 4. 计算RFM评分
    reference_date = df['订单创建时间'].max()
    user_profile['R'] = (reference_date - user_profile['最近下单时间']).dt.days
    user_profile['活跃天数'] = (user_profile['最近下单时间'] - user_profile['首次下单时间']).dt.days + 1
    user_profile['F'] = user_profile['活跃天数'] / user_profile['订单总数']
    user_profile['M'] = user_profile['平均订单质量']

    # 对RFM进行1-5分评分（5分最高）
    # R值越小越好（最近购买），F值越小越好（购买频率高），M值越大越好
    user_profile['R_score'] = pd.qcut(user_profile['R'], 5, labels=[5, 4, 3, 2, 1])
    user_profile['F_score'] = pd.qcut(user_profile['F'], 5, labels=[5, 4, 3, 2, 1])
    user_profile['M_score'] = pd.qcut(user_profile['M'], 5, labels=[1, 2, 3, 4, 5])

    # 计算RFM总分（0-15分）
    user_profile['RFM_score'] = (
            user_profile['R_score'].astype(int) +
            user_profile['F_score'].astype(int) +
            user_profile['M_score'].astype(int)
    )

    # 5. 合并偏好商品信息
    user_profile = user_profile.merge(user_top_products_str, on='买家手机号', how='left')

    # 添加脱敏手机号（保留前3后4位，中间用*代替）
    user_profile['脱敏手机号'] = user_profile['手机号'].apply(
        lambda x: f"{x[:3]}****{x[-4:]}" if len(x) == 11 else x
    )

    # 整理列顺序
    columns_order = [
        '姓名', '脱敏手机号', '手机号', '最新会员等级',
        '省份', '城市', '地区', '完整地址',
        '首次下单时间', '最近下单时间', '订单总数', '总消费金额',
        '平均订单质量', '偏好商品', 'RFM_score'
    ]

    return user_profile[columns_order]


# 定义表头及对应的数据类型
columns = {
    "订单号": str,  # 字符串类型（长订单号）
    "订单状态": str,  # 字符串类型（三种状态）
    "订单创建时间": "datetime64[ns]",  # 日期时间类型
    "买家付款时间": "datetime64[ns]",  # 日期时间类型
    "交易成功时间": "datetime64[ns]",  # 日期时间类型
    "全部商品名称": str,  # 字符串类型（多个商品名称组合）
    "商品种类数": int,  # 整数类型
    "订单商品总件数": int,  # 整数类型
    "收货人省份": str,  # 字符串类型
    "收货人/提货人": str,  # 字符串类型
    "收货人城市": str,  # 字符串类型
    "收货人地区": str,  # 字符串类型
    "会员等级": str,   # 字符串类型
    "下单次数": int,  # 整数类型
    "商品金额合计": float,  # 浮点数类型（金额）
    "运费": float,    # 浮点数类型（金额）
    "买家手机号": str,
    "备注": str,
    "标签": str
}
# 创建空DataFrame
df = pd.DataFrame(columns=columns.keys())
# 设置DataFrame每列的数据类型
for col, dtype in columns.items():
    df[col] = pd.Series(dtype=dtype)



# 打印验证
print()
