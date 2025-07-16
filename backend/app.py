from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from api.trade_api import trade_bp
from api.deepseek_api import deepseek_bp
import logging
from logging.handlers import RotatingFileHandler

# 创建Flask应用实例
app = Flask(__name__)

app.json.ensure_ascii = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # 美化JSON输出
# 配置CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 配置日志
def configure_logging():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=1024*1024, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

# 注册蓝图
app.register_blueprint(trade_bp, url_prefix='/api/trade')
app.register_blueprint(deepseek_bp)

# 全局错误处理
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    configure_logging()
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, debug=True)
    