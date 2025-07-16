from datetime import datetime
from flask import Blueprint, app, jsonify
from core.Analyze import TradeAnalyzer, ProductAnalyzer
import pandas as pd
import numpy as np

trade_bp = Blueprint('trade_api', __name__, url_prefix='/api/trade')
product_bp = Blueprint('product_api', __name__, url_prefix='/api/product')

def get_top_items(series, top_n=5):
    """
    获取出现频率最高的top_n个项目
    """
    counts = series.value_counts().head(top_n)
    return [{'name': k, 'count': int(v)} for k, v in counts.items()]
def convert_location_to_dict(df):
    """转换为前端友好格式"""
    if df is None or df.empty:
        return None
    # 处理MultiIndex
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index()
    # 替换所有可能的空值表示形式为None
    df = df.replace([np.nan, pd.NA, 'nan', 'NaN', 'null', 'None'], None)
    # 处理畅销商品列
    if '畅销商品' in df.columns:
        df['畅销商品'] = df['畅销商品'].apply(
            lambda x: [s.strip() for s in str(x).split(',')] 
            if x and str(x).lower() not in ['nan', 'none', 'null'] 
            else None
        )
    return {
        'columns': list(df.columns),
        'data': df.to_dict(orient='records')
    }
def convert_user_profiles_to_dict(user_profiles_df):
    """
    将用户画像DataFrame转换为前端友好的字典列表格式
    并对敏感信息进行脱敏处理
    """
    # 深拷贝避免修改原数据
    df = user_profiles_df.copy()
    
    # 处理日期格式
    df['首次下单时间'] = df['首次下单时间'].dt.strftime('%Y-%m-%d')
    df['最近下单时间'] = df['最近下单时间'].dt.strftime('%Y-%m-%d')
    
    # 金额保留两位小数
    df['总消费金额'] = df['总消费金额'].round(2)
    df['平均订单质量'] = df['平均订单质量'].round(2)
    
    # 转换NaN为None
    df = df.where(pd.notnull(df), None)
    
    # 转换为字典列表
    records = df.to_dict('records')
    
    # 进一步处理每个记录
    for record in records:
        # 确保偏好商品字段是字符串
        if record['偏好商品'] is None:
            record['偏好商品'] = []
        else:
            record['偏好商品'] = record['偏好商品'].split('、')
        
        # 添加用户ID（可以用索引或其他唯一标识）
        record['user_id'] = hash(record['买家昵称'] + record['手机号']) if record['手机号'] else hash(record['买家昵称'])
    
    return records

@trade_bp.route('/analyze-location', methods=['GET'])
def analyze_location():
    try:
        analyzer = TradeAnalyzer()
        analyzer.load_order_data()
        result = analyzer.get_location_analysis()
        response_data = {
            'status': 'success',
            'data': {
                'province_summary': convert_location_to_dict(result.get('province_summary')),
                'city_summary': convert_location_to_dict(result.get('city_summary')),
                'district_summary': convert_location_to_dict(result.get('district_summary'))
            }
        }
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trade_bp.route('/analyze-user', methods=['GET'])
def analyze_user_profiles():
    try:
        # 初始化分析器
        analyzer = TradeAnalyzer()
        analyzer.load_order_data()
        
        # 获取用户画像分析结果
        user_profiles = analyzer.get_user_profiles()
        
        # 转换为前端友好格式
        response_data = {
            'status': 'success',
            'data': {
                'user_profiles': convert_user_profiles_to_dict(user_profiles),
                'summary_stats': {
                    'total_users': len(user_profiles),
                    'avg_order_quality': round(user_profiles['平均订单质量'].mean(), 2),
                    'total_consumption': round(user_profiles['总消费金额'].sum(), 2),
                    'top_provinces': get_top_items(user_profiles['省份']),
                    'top_products': get_top_items(user_profiles['偏好商品'].str.split('、').explode())
                }
            }
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trade_bp.route('/test', methods=['GET'])
def test_endpoint():
    """用于前后端联调的测试接口"""
    return jsonify({
        "status": "success",
        "data": {
            "message": "后端API连接成功",
            "sample_data": {
                "城市": "上海",
                "金额": 208.6
            }
        }
    })


#商品分析
@product_bp.route('/analyze-sales', methods=['GET'])
def sales_analysis():
    """API 路由：返回商品销量分析的 JSON 数据"""
    try:
        # 调用你的分析方法（假设 self 是某个类实例）
        analyzer = ProductAnalyzer()  # 替换成你的实际类
        analyzer.load_data()
        res = analyzer.sales_analysis()
        result = {
        "success": True,
        "data": res.to_dict(orient='records'),  # 关键转换：DataFrame → 字典列表
        "message": "Data retrieved successfully"
    }
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
#分类排行
@product_bp.route('/analyze-category', methods=['GET'])
def category_analysis():
    try:
        # 调用你的分析方法（假设 self 是某个类实例）
        analyzer = ProductAnalyzer()  # 替换成你的实际类
        analyzer.load_data()
        res = analyzer.category_analysis()
        return jsonify({
        'category1': res['category1'].to_dict(orient='records'),
        'category2': res['category2'].to_dict(orient='records'),
        'category3': res['category3'].to_dict(orient='records')
    })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500