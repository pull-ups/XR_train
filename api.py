import pandas as pd
import os
from openai import OpenAI
from flask import Flask, request, jsonify, json
from pyngrok import ngrok

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# ngrok 터널을 열기 위해 pyngrok 설정
# ngrok.com에 로그인하여 Auth Token을 복사해 붙여넣어야 합니다.
ngrok.set_auth_token("30rQLzpKFLLeWnCIS6lo2iFNh5q_3sdRX3bEabLkTXXe8BNgb")

# 전역 변수로 NPC 인스턴스 생성
csv_file_path = './hint_message.csv'
npc = None


class trainNPC:
    """
    게임 내 NPC 역할을 수행하며, 플레이어의 단계에 따라 힌트를 제공하는 클래스.
    """
    def __init__(self, csv_path: str):
        """
        NPC를 초기화하고 CSV 데이터와 힌트 요청 상태를 설정합니다.

        :param csv_path: 힌트 정보가 담긴 CSV 파일 경로
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
        
        # '단계' 열을 인덱스로 사용하여 CSV 파일 로드
        self.hint_data = pd.read_csv(csv_path, index_col='단계')
        # NaN 값을 빈 문자열로 대체
        self.hint_data = self.hint_data.fillna('')
        # OpenAI 클라이언트 초기화 (환경 변수에서 API 키 로드)
        # 실행 전 터미널에 'export OPENAI_API_KEY='your_api_key''를 입력하세요.
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception as e:
            print(f"OpenAI 클라이언트 초기화 실패: {e}")
            print("OPENAI_API_KEY 환경 변수가 설정되었는지 확인하세요.")
            self.client = None

    def _rephrase_as_npc(self, hint_text: str) -> str:
        """
        주어진 힌트 텍스트를 NPC의 자연스러운 대화체로 변환합니다.
        """
        if not self.client or not hint_text:
            return hint_text

        try:
            system_prompt = "당신은 XR 재난 훈련 시뮬레이션의 친절한 AI 조교입니다. 주어진 힌트를 보고, 훈련자가 다음에 무엇을 해야 할지 자연스럽고 격려하는 말투로 안내해주세요. 핵심 내용은 유지하되, 문장을 완성된 형태로 부드럽게 만들어주세요. 너무 많은 내용을 담지 않도록 주의하고, 훈련자가 이해하기 쉽게 간결하게 작성해주세요."
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": hint_text}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            return f"(시스템) {hint_text}" # API 실패 시 원본 힌트 반환

    def get_hint(self, current_step: int, request_count: int) -> str:
        """
        현재 단계와 요청 횟수에 맞는 힌트를 제공합니다.

        :param current_step: 플레이어의 현재 게임 단계
        :param request_count: 해당 단계에 대한 힌트 요청 횟수
        :return: 제공할 힌트 메시지
        """
        if current_step not in self.hint_data.index:
            return "해당 단계에 대한 정보가 없습니다. 단계를 다시 확인해주세요."

        # 요청 횟수에 따라 힌트 선택
        if request_count == 1:
            hint_col = '힌트1'
        elif request_count == 2:
            hint_col = '힌트2'
        else: # 3회 이상 요청 시
            hint_col = '힌트3'

        hint = self.hint_data.loc[current_step, hint_col]

        # 상위 힌트가 비어있을 경우, 하위 힌트에서 가져오기
        if not hint.strip():
            if hint_col == '힌트3' and self.hint_data.loc[current_step, '힌트2'].strip():
                hint = self.hint_data.loc[current_step, '힌트2']
            elif (hint_col == '힌트2' or hint_col == '힌트3') and self.hint_data.loc[current_step, '힌트1'].strip():
                hint = self.hint_data.loc[current_step, '힌트1']

        if not hint.strip():
            return "더 이상 드릴 힌트가 없네요. 주변을 잘 둘러보세요!"

        return self._rephrase_as_npc(hint)

try:
    npc = trainNPC(csv_path=csv_file_path)
except Exception as e:
    print(f"NPC 초기화 실패: {e}")

# Flask API 엔드포인트들
@app.route('/ping')
def ping():
    """서버 상태 확인용 엔드포인트"""
    return "pong"

@app.route('/hint', methods=['GET'])
def get_hint():
    """특정 단계의 힌트를 제공하는 엔드포인트"""
    if npc is None:
        return jsonify({"error": "NPC가 초기화되지 않았습니다."}), 500
    try:
        step = int(request.args.get('step', 0))
        count = int(request.args.get('count', 1))
        
        hint = npc.get_hint(step, count)
        
        response_data = {"hint": hint}
        
        response = app.response_class(
            response=json.dumps(response_data, ensure_ascii=False, indent=None),
            status=200,
            mimetype='application/json; charset=utf-8'
        )
        return response

    except ValueError:
        return jsonify({"error": "step과 count 파라미터는 정수여야 합니다."}), 400
    except Exception as e:
        return jsonify({"error": f"오류가 발생했습니다: {str(e)}"}), 500


if __name__ == '__main__':
    # 0.0.0.0으로 설정하면 외부에서 접근 가능
    app.run(host='0.0.0.0', port=3001, debug=True)