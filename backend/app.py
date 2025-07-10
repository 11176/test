from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

@app.route('/')
def hello():
    return jsonify({"message": "Hello, Flask!"})

if __name__ == '__main__':
    app.run(debug=True)