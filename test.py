from flask import Flask, jsonify
import datetime

# Flask 애플리케이션 객체 생성
app = Flask(__name__)

# Ping API 엔드포인트 정의
@app.route('/ping', methods=['GET'])
def ping():
    """
    Ping 요청에 응답하는 API 엔드포인트
    """
    response = {
        "message": "pong",
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    print("Ping request received!")
    return jsonify(response)

# 애플리케이션 실행
if __name__ == '__main__':
    # 0.0.0.0으로 설정하면 외부에서 접근 가능
    app.run(host='0.0.0.0', port=3000, debug=True)