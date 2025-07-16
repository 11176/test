import os
import pandas as pd
import re
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from rapidfuzz import process


# 配置数据库连接
engine = create_engine("mysql+pymysql://shop:shop12345@localhost:3306/shop_db?charset=utf8mb4")

# 清空旧数据
with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
    conn.execute(text("DELETE FROM order_item"))
    conn.execute(text("DELETE FROM orders"))
    conn.execute(text("DELETE FROM product_spec"))
    conn.execute(text("DELETE FROM product"))
    conn.execute(text("DELETE FROM region"))
    conn.execute(text("DELETE FROM customer"))
    conn.execute(text("DELETE FROM category"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
print("已清空旧数据，准备导入新数据...")

# 定位文件路径
base_dir = os.path.dirname(os.path.abspath(__file__))
orders_csv_path = os.path.join(base_dir, '../database/订单数据-7.13.csv')
products_excel_path = os.path.join(base_dir, '../database/商品列表.xlsx')

# 读取数据
print("开始读取 CSV 和 Excel 文件...")
df_orders = pd.read_csv(orders_csv_path, encoding='utf-8')
df_products = pd.read_excel(products_excel_path, sheet_name='商品库商品')
df_specs = pd.read_excel(products_excel_path, sheet_name='会员价')
print("文件读取成功。")


# 分类字段统一空值处理 + 去空格
for col in ['一级分类', '二级分类', '三级分类']:
    df_products[col] = df_products[col].fillna('').astype(str).str.strip()

print("导入 category 表...")

# 按三级分类去重，生成分类表
df_categories = df_products[['一级分类', '二级分类', '三级分类']].drop_duplicates().copy()

# 生成唯一 CategoryID，比如 C001, C002, ...
df_categories['CategoryID'] = ['C' + str(i+1).zfill(3) for i in range(len(df_categories))]

# 重命名字段
df_categories.rename(columns={
    '一级分类': 'Category1',
    '二级分类': 'Category2',
    '三级分类': 'Category3'
}, inplace=True)

# 导入 category 表
df_categories.to_sql('category', con=engine, if_exists='append', index=False)

print(f' category 表导入完成，共 {len(df_categories)} 条。')

# ------------------------

print("导入 product 表...")

# 商品唯一 ID
df_products['ProductID'] = df_products['商品id'].astype(str)

# 建立分类映射表
category_map = df_categories.set_index(['Category1', 'Category2', 'Category3'])['CategoryID']

# 给商品表加 CategoryID
df_products['CategoryID'] = df_products.apply(
    lambda row: category_map.get((row['一级分类'], row['二级分类'], row['三级分类'])),
    axis=1
)

# 检查缺失
missing_count = df_products['CategoryID'].isnull().sum()
if missing_count > 0:
    print(f" 有 {missing_count} 个商品未匹配到 CategoryID，建议检查分类数据！")
    print(df_products[df_products['CategoryID'].isnull()][['ProductID', '一级分类', '二级分类', '三级分类']].head())

    # 可选：丢弃这些商品
    df_products = df_products.dropna(subset=['CategoryID'])
    print(f"已丢弃未匹配到分类的商品，剩余 {len(df_products)} 条。")

# 重命名字段
df_products.rename(columns={
    '商品名称': 'ProductName',
    '销量': 'Sales',
    '一级品牌': 'Brand1',
    '二级品牌': 'Brand2',
}, inplace=True)

# 去重后导入
df_products_unique = df_products.drop_duplicates(subset=['ProductID'])

df_products_unique[['ProductID', 'CategoryID', 'ProductName', 'Sales', 'Brand1', 'Brand2']].to_sql(
    'product', con=engine, if_exists='append', index=False
)

print(f' product 表导入完成，共 {len(df_products_unique)} 条（去重后）。')



print("导入 product_spec 表...")

df_products['ProdSpecID'] = df_products['规格id'].astype(str)
df_products['ProductID'] = df_products['商品id'].astype(str)
df_products['SpecName'] = df_products['规格项1'].astype(str)
df_products['Price'] = df_products['零售价'].fillna(0).astype(float)
df_products['Weight'] = df_products['重量'].fillna(100).astype(float)

df_products[['ProdSpecID', 'ProductID', 'SpecName', 'Price', 'Weight']].to_sql(
    'product_spec', con=engine, if_exists='append', index=False)

print(f'product_spec 表导入完成，共 {len(df_products)} 条。')

# 导入 customer 表
print("导入 customer 表...")

# --- 数据清洗和预处理 ---
# 确保关键字段为字符串并去除前后空格
df_orders['买家昵称'] = df_orders['买家昵称'].astype(str).str.strip()
df_orders['下单次数'] = df_orders['下单次数'].astype(str).str.strip()

# 处理会员等级列的混合类型问题
# 为了能安全地使用 .transform('max')，我们先将空值(NaN)替换为空字符串 ''
# 然后再将整列强制转换为字符串类型。空字符串 '' 在比较时会被所有有效等级（如'2_1'）视为“最小”
df_orders['会员等级'] = df_orders['会员等级'].fillna('').astype(str).str.strip()


# --- 计算每个客户的最大下单次数 ---
# 从“下单次数”中提取数字，并转换为整数
df_orders['order_count_num'] = pd.to_numeric(
    df_orders['下单次数'].str.extract(r'(\d+)', expand=False),
    errors='coerce'
).fillna(0).astype(int)
# 按客户分组，计算最大下单次数
df_orders['actual_order_count'] = df_orders.groupby('买家昵称')['order_count_num'].transform('max')


# --- 计算每个客户的最高会员等级 ---
# 现在该列已无混合类型，可以安全地计算最大值
df_orders['actual_member_level'] = df_orders.groupby('买家昵称')['会员等级'].transform('max')


df_customers = df_orders[[
    '买家昵称', '买家姓名', '买家手机号', 'actual_member_level', '买家是否会员',
    '客户标签', '买家备注', 'actual_order_count'
]].copy()

# 重命名字段以匹配数据库
df_customers.rename(columns={
    '买家昵称': 'Customer_ID',
    '买家姓名': 'Name',
    '买家手机号': 'Phone',
    'actual_member_level': 'MemberLevel',
    '买家是否会员': 'IsMember',
    '客户标签': 'Tags',
    '买家备注': 'Remark',
    'actual_order_count':'order_count'
}, inplace=True)

# 去掉重复客户，现在每个客户的 'order_count' 和 'MemberLevel' 都已是其正确的值
df_customers = df_customers.drop_duplicates(subset=['Customer_ID'], keep='last')

# 将处理过程中产生的空字符串 '' 转换回 None
# None 在 to_sql 中会被正确地转换成数据库的 NULL 值
import numpy as np
df_customers['MemberLevel'].replace('', np.nan, inplace=True)


# 将处理好的数据存入数据库
# to_sql 会自动将 pandas 中的 np.nan (NaN) 写入数据库的 NULL
df_customers.to_sql('customer', con=engine, if_exists='append', index=False)
print(f' customer 表导入完成，共 {len(df_customers)} 条。')

# 导入 region 表
print("导入 region 表...")

# 地址字段空值处理
for col in ['收货人省份', '收货人城市', '收货人地区']:
    df_orders[col] = df_orders[col].fillna('').astype(str).str.strip()

df_orders['买家昵称'] = df_orders['买家昵称'].astype(str).str.strip()

df_regions = df_orders[['收货人省份', '收货人城市', '收货人地区', '买家昵称']].drop_duplicates().copy()

df_regions['Customer_ID'] = df_regions['买家昵称']
df_regions.drop(columns=['买家昵称'], inplace=True)

df_regions['RegionID'] = ['R' + str(i+1).zfill(3) for i in range(len(df_regions))]

df_regions.rename(columns={
    '收货人省份': 'Province',
    '收货人城市': 'City',
    '收货人地区': 'District'
}, inplace=True)

df_regions.to_sql('region', con=engine, if_exists='append', index=False)
print(f' region 表导入完成，共 {len(df_regions)} 条。')

# 导入 orders 表
print("导入 orders 表...")

df_orders_main = df_orders[['订单号', '买家昵称', '订单状态', '订单创建时间','买家付款时间','交易成功时间','全部商品名称','商品种类数','订单商品总件数','运费','店铺优惠合计', '商品金额合计']].copy()


# 加 Customer_ID 字段
df_orders_main['Customer_ID'] = df_orders_main['买家昵称'].astype(str).str.strip()

# 给订单加 RegionID：根据省市区+客户匹配
region_map = df_regions.set_index(['Province', 'City', 'District', 'Customer_ID'])['RegionID']

df_orders_main['Province'] = df_orders['收货人省份']
df_orders_main['City'] = df_orders['收货人城市']
df_orders_main['District'] = df_orders['收货人地区']

df_orders_main['RegionID'] = df_orders_main.apply(
    lambda row: region_map.get((row['Province'], row['City'], row['District'], row['Customer_ID'])),
    axis=1
)


# 重命名
df_orders_main.rename(columns={
    '订单号': 'OrderID',
    '订单状态': 'Status',
    '订单创建时间': 'Created_time',
    '买家付款时间': 'Payment_time',
    '交易成功时间': 'Completed_time',
    '运费': 'Freight',
    '店铺优惠合计':'Discount',
    '商品金额合计': 'TotalAmount',
    '全部商品名称':'AllProduct',
    '商品种类数':'Pdnumber',
    '订单商品总件数':'Totalnumber',
}, inplace=True)

# 去掉临时列
df_orders_main.drop(columns=['Province', 'City', 'District', '买家昵称'], inplace=True)
df_orders_main.to_sql('orders', con=engine, if_exists='append', index=False)
print(f' orders 表导入完成，共 {len(df_orders_main)} 条。')


# ============ 自定义映射表 =============
product_name_map = {
    '拌板筋': '牛板筋',
    '拌牛板筋': '牛板筋',
    '拌板筋片': '牛板筋',
    '拌板筋丝': '牛板筋',
}

spec_name_map = {
    '拌板筋丝250g': '板筋丝250g',
    '拌板筋片250g': '板筋片250g',
    '拌板筋片500g': '板筋片500g',
    '拌板筋丝': '板筋丝250g',
    '拌板筋片': '板筋片250g',
}


def clean_text(text):
    if pd.isna(text):
        return ''
    text = ''.join([chr(ord(c)-0xfee0) if '！' <= c <= '～' else c for c in text])
    text = text.strip().lower()
    text = re.sub(r'[\s\u3000]+', '', text)
    return text

def extract_qty_from_spec(spec_str):
    if not spec_str:
        return '', 1
    spec_str = spec_str.strip()
    if re.match(r'^\d+(\.\d+)?[kKgG][gG]$', spec_str):
        return spec_str, 1
    qty_match = re.search(r'(\d+)\s*袋', spec_str)
    qty = int(qty_match.group(1)) if qty_match else 1
    spec_cleaned = re.sub(r'(\d+)\s*袋', '', spec_str).strip()
    return spec_cleaned, qty

def extract_package_items(item_str):
    if pd.isna(item_str) or not item_str.strip():
        return []

    all_brackets = re.findall(r'\((.*?)\)', item_str)
    product_part = item_str.strip()
    package_qty = 1
    spec_str = None

    if len(all_brackets) >= 2:
        # 商品名(规格)(数量)
        spec_str = all_brackets[-2].strip()
        qty_match = re.search(r'(\d+)', all_brackets[-1])
        package_qty = int(qty_match.group(1)) if qty_match else 1
        product_part = item_str[:item_str.rfind('(' + all_brackets[-2] + ')')].strip()

    elif len(all_brackets) == 1:
        possible_qty = re.match(r'^(\d+)\s*(袋|件|瓶|盒)?$', all_brackets[0].strip())
        if possible_qty:
            package_qty = int(possible_qty.group(1))
            product_part = item_str[:item_str.rfind('(' + all_brackets[0] + ')')].strip()

            # 在商品名部分尝试提取规格，如500g
            spec_match = re.search(r'(\d+(?:\.\d+)?\s*[kKgG][gG])', product_part)
            if spec_match:
                spec_str = spec_match.group(1).replace(' ','').lower()
                product_part = product_part.replace(spec_match.group(1), '').strip()
            else:
                spec_str = None
        else:
            spec_str = all_brackets[0].strip()
            product_part = item_str[:item_str.rfind('(' + all_brackets[0] + ')')].strip()
    else:
        spec_str = None
        product_part = item_str.strip()

    product_names = [p.strip() for p in re.split(r'\s*\+\s*', product_part)]
    spec_names_raw = [s.strip() for s in re.split(r'\s*\+\s*', spec_str)] if spec_str else [None]*len(product_names)
    while len(spec_names_raw) < len(product_names):
        spec_names_raw.append(None)

    items = []
    for pname, sname_raw in zip(product_names, spec_names_raw):
        if sname_raw:
            spec_cleaned, spec_qty = extract_qty_from_spec(sname_raw)
            final_qty = package_qty * spec_qty
        else:
            spec_cleaned = ''
            final_qty = package_qty
        items.append((pname, spec_cleaned, final_qty))

    return items

def fuzzy_match_spec_for_banjin(spec_name, candidates, threshold=90):
    if not spec_name:
        return None
    result = process.extractOne(spec_name, candidates, score_cutoff=threshold)
    if result:
        match, score, _ = result
        return match
    else:
        return None

def import_order_items(df_orders, df_products):
    print("导入 order_item 表...")

    df_items = df_orders[['订单号', '全部商品名称']].copy()
    df_items['商品条目'] = df_items['全部商品名称'].str.split(';')
    df_items = df_items.explode('商品条目').reset_index(drop=True)

    expanded_rows = []
    for idx, row in df_items.iterrows():
        order_id = row['订单号']
        item_str = row['商品条目']
        extracted_items = extract_package_items(item_str)
        for pname_raw, sname_raw, qty in extracted_items:
            pname_mapped = product_name_map.get(pname_raw, pname_raw)
            sname_mapped = spec_name_map.get(sname_raw, sname_raw)

            pname_clean = clean_text(pname_mapped)
            sname_clean = clean_text(sname_mapped)

            if '牛板筋' in pname_clean:
                candidates = df_products[df_products['ProductName'].str.strip().str.lower() == '牛板筋']['SpecName'].dropna().unique()
                candidates_cleaned = [clean_text(spec) for spec in candidates]
                matched_spec = fuzzy_match_spec_for_banjin(sname_clean, candidates_cleaned, threshold=90)
                if matched_spec:
                    sname_clean = matched_spec

            expanded_rows.append({
                '订单号': order_id,
                'ProductName': pname_clean,
                'SpecName': sname_clean,
                'Quantity': qty
            })

    df_expanded = pd.DataFrame(expanded_rows)

    # Clean product表
    df_products['ProductName_cleaned'] = df_products['ProductName'].apply(lambda x: clean_text(product_name_map.get(x, x)))
    df_products['SpecName_cleaned'] = df_products['SpecName'].fillna('').apply(lambda x: clean_text(spec_name_map.get(x, x)))

    # 强制 SpecName 空值变 ''
    df_expanded['SpecName'] = df_expanded['SpecName'].fillna('').astype(str).str.strip()

    df_items_with_spec = df_expanded[df_expanded['SpecName'] != ''].copy()
    df_items_no_spec = df_expanded[df_expanded['SpecName'] == ''].copy()

    df_items_with_spec = df_items_with_spec.merge(
        df_products[['ProdSpecID', 'ProductName_cleaned', 'SpecName_cleaned']],
        left_on=['ProductName', 'SpecName'], right_on=['ProductName_cleaned', 'SpecName_cleaned'], how='left')

    df_items_no_spec = df_items_no_spec.merge(
        df_products[['ProdSpecID', 'ProductName_cleaned']],
        left_on='ProductName', right_on='ProductName_cleaned', how='left')

    df_merged = pd.concat([df_items_with_spec, df_items_no_spec], ignore_index=True)

    unmatched = df_merged[df_merged['ProdSpecID'].isnull()][['ProductName', 'SpecName']].drop_duplicates()
    if not unmatched.empty:
        print(f"⚠️ 以下商品未匹配到 ProdSpecID：\n{unmatched}")
        unmatched.to_excel('未匹配商品.xlsx', index=False)
        print("📦 未匹配商品已导出到：未匹配商品.xlsx")

    df_merged['OrderItemID'] = ['OI' + str(i + 1).zfill(5) for i in range(len(df_merged))]
    df_merged.rename(columns={'订单号': 'OrderID'}, inplace=True)
    df_final = df_merged[['OrderItemID', 'OrderID', 'ProdSpecID', 'Quantity']]

    # 写入数据库
    df_final.to_sql('order_item', con=engine, if_exists='append', index=False)
    print(f'✅ order_item 表导入完成，共 {len(df_final)} 条。')


# 最后执行
import_order_items(df_orders, df_products)



print("全部导入完成。")


