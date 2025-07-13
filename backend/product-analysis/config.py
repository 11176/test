class Config:
    # MySQL数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'your_username'
    MYSQL_PASSWORD = 'your_password'
    MYSQL_DB = 'shop_db'
    MYSQL_CHARSET = 'utf8mb4'
    
    # 分析参数
    TOP_N_PRODUCTS = 10
    SLOW_MOVING_THRESHOLD = 0.1  # 滞销商品阈值