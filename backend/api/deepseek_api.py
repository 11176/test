import traceback
import requests
from flask import Blueprint, jsonify, request, current_app

DEESEEK_API_KEY = "sk-2c50d9a7f01040189bc8bb49d5018814"
DEESEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

TYPE_TO_ENDPOINT = {
    'location': 'http://127.0.0.1:5000/api/trade/analyze-location',
    'user': 'http://127.0.0.1:5000/api/trade/analyze-user',
    'product': 'http://127.0.0.1:5000/api/product/analyze-sales',
}

class DeepSeekClient:
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    def ask(self, messages: list, model: str = 'deepseek-chat') -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7
        }
        resp = requests.post(self.endpoint, json=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            current_app.logger.error(f"DeepSeek 调用失败: {resp.status_code} {resp.text}")
            return f"[错误] DeepSeek API 响应失败: {resp.status_code}"

def simplify_context(data_type: str, context: dict) -> str:
    """压缩并结构化不同类型的数据上下文"""
    if data_type == 'location':
        cities = context.get('city_summary', {}).get('data', [])
        simplified = [
            {
                '省份': item.get('收货人省份'),
                '城市': item.get('收货人城市'),
                '金额': item.get('城市总金额'),
                '畅销商品': item.get('畅销商品', [])[:3]
            }
            for item in cities[:5]
        ]
    elif data_type == 'user':
        summary = context.get('summary_stats', {})
        users = context.get('user_profiles', [])[:5]
        simplified = {
            '总体': {
                '总用户数': summary.get('total_users'),
                '总消费': summary.get('total_consumption')
            },
            '示例用户': [
                {
                    '城市': user.get('城市'),
                    '省份': user.get('省份'),
                    '消费': user.get('总消费金额'),
                    '偏好商品': user.get('偏好商品', [])[:3],
                    '订单数': user.get('订单总数')
                }
                for user in users
            ]
        }
    elif data_type == 'product':
        products = context[:5]
        simplified = [
            {
                '商品名': item.get('ProductName'),
                '销售额': item.get('total_sales'),
                '订单数': item.get('order_count'),
                '高峰时段': item.get('peak_hour')
            }
            for item in products
        ]
    else:
        simplified = context
    return str(simplified)

# Blueprint 注册
deepseek_bp = Blueprint('deepseek_api', __name__, url_prefix='/api/deepseek')

@deepseek_bp.route('/suggest', methods=['POST'])
def suggest():
    try:
        data = request.get_json(force=True)
        data_type = data.get('type', 'location')
        question = data.get('question', '请根据当前分析数据提供运营建议')

        # 获取上下文数据
        backend_url = TYPE_TO_ENDPOINT.get(data_type, TYPE_TO_ENDPOINT['location'])
        resp = requests.get(backend_url)
        resp.raise_for_status()
        raw_context = resp.json().get('data', {})
        context = simplify_context(data_type, raw_context)

        # 构建消息
        messages = [
            {"role": "system", "content": "你是一位电商运营顾问。"},
            {"role": "system", "content": f"当前分析背景：{context}"},
            {"role": "user", "content": question}
        ]

        client = DeepSeekClient(DEESEEK_API_KEY, DEESEEK_ENDPOINT)
        advice = client.ask(messages)

        return jsonify({"status": "success", "advice": advice}), 200

    except Exception as e:
        current_app.logger.error("DeepSeek suggest 接口异常：\n" + traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@deepseek_bp.route('/chat', methods=['POST'])
def chat():
    try:
        body = request.get_json(force=True)
        question = body.get('question', '')
        history = body.get('history', [])

        # 使用 location 类型上下文作为默认对话背景
        backend_url = TYPE_TO_ENDPOINT['location']
        resp = requests.get(backend_url)
        resp.raise_for_status()
        raw_context = resp.json().get('data', {})
        context = simplify_context('location', raw_context)

        messages = [
            {"role": "system", "content": "你是一位电商运营顾问。"},
            {"role": "system", "content": f"当前分析背景：{context}"}
        ]
        if isinstance(history, list):
            messages.extend(history)
        messages.append({"role": "user", "content": question})

        client = DeepSeekClient(DEESEEK_API_KEY, DEESEEK_ENDPOINT)
        reply = client.ask(messages)

        return jsonify({
            "status": "success",
            "answer": reply,
            "messages": messages + [{"role": "assistant", "content": reply}]
        }), 200

    except Exception as e:
        current_app.logger.error("DeepSeek chat 接口异常：\n" + traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500
