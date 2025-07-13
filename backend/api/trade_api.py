from datetime import datetime
from flask import Blueprint, app, jsonify
from core.TradeTable import TradeAnalyzer
import pandas as pd
import numpy as np

trade_bp = Blueprint('trade_api', __name__, url_prefix='/api/trade')

@trade_bp.route('/analyze-location', methods=['GET'])
def analyze_location():
    try:
        analyzer = TradeAnalyzer()
        analyzer.load_order_data()
        result = analyzer.get_location_analysis()
        
        response_data = {
            'status': 'success',
            'data': {
                'province_summary': convert_df_to_dict(result.get('province_summary')),
                'city_summary': convert_df_to_dict(result.get('city_summary')),
                'district_summary': convert_df_to_dict(result.get('district_summary'))
            }
        }
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def convert_df_to_dict(df):
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

