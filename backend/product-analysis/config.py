# config.py
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '实际密码',
    'database': 'shop_db',
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

DATA_SOURCE = 'database'  # 或 'csv'