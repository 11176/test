# backend/config.py
class Config:
    # MySQL 连接配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '13579OKOK'
    MYSQL_DATABASE = 'trade_db'
    
    # 生成连接字符串
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

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

DATA_SOURCE = 'database'  #或 'csv'