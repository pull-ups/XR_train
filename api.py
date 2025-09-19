import pandas as pd
import os
from openai import OpenAI
from flask import Flask, request, jsonify, json, send_file
from pyngrok import ngrok

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


# 전역 변수로 NPC 인스턴스 생성
# 모든 씬에서 사용할 단일 CSV 파일
CSV_PATH = './assets/hint_message_for_NPC.csv'
npcs = {}


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
        
        # '세부단계' 열을 인덱스로 사용하여 CSV 파일 로드
        self.hint_data = pd.read_csv(csv_path, index_col='순서')
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

    def _rephrase_as_npc(self, hint_text: str, user_question: str = None) -> str:
        """
        주어진 힌트 텍스트를 NPC의 자연스러운 대화체로 변환합니다.
        """
        if not self.client or not hint_text:
            return hint_text

        try:
            system_prompt = "당신은 XR 재난 훈련 시뮬레이션의 친절한 AI 조교입니다. 주어진 힌트를 보고, 훈련자가 다음에 무엇을 해야 할지 자연스럽고 격려하는 말투로 안내해주세요. 핵심 내용은 유지하되, 문장을 완성된 형태로 부드럽게 만들어주세요. 너무 많은 내용을 담지 않도록 주의하고, 훈련자가 이해하기 쉽게 간결하게 작성해주세요."
            
            user_content = f"힌트: {hint_text}"
            if user_question:
                user_content = f"사용자 질문: {user_question}\n참고할 힌트: {hint_text}"

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            return f"(시스템) {hint_text}" # API 실패 시 원본 힌트 반환

    def get_default_hint(self, step: int) -> str:
        """
        사용자가 말 없이 힌트를 요청했을 때 기본 힌트를 제공합니다.
        :param step: 현재 세부 단계
        :return: 제공할 힌트 메시지
        """
        if step not in self.hint_data.index:
            return "해당 단계에 대한 정보가 없습니다. 단계를 다시 확인해주세요."
        
        hint = self.hint_data.loc[step, '기본 힌트']

        if not hint.strip():
            return "더 이상 드릴 힌트가 없네요. 주변을 잘 둘러보세요!"

        return self._rephrase_as_npc(hint)

    def get_question_hint(self, step: int, count: int, text_message: str) -> str:
        """
        사용자가 직접 질문했을 때 요청 횟수에 맞는 힌트를 제공합니다.
        :param step: 현재 세부 단계
        :param count: 해당 단계에 대한 힌트 요청 횟수
        :param text_message: 사용자의 질문 메시지
        :return: 제공할 힌트 메시지
        """
        if step not in self.hint_data.index:
            return "해당 단계에 대한 정보가 없습니다. 단계를 다시 확인해주세요."

        if count == 1:
            hint_col = '요청 힌트 1'
        elif count >= 2:
            hint_col = '요청 힌트 2'
        else:
            return "힌트 요청 횟수(count)는 1 이상이어야 합니다."

        hint = self.hint_data.loc[step, hint_col]

        if not hint.strip():
            # 요청 힌트 2가 비었으면 요청 힌트 1을 사용
            if hint_col == '요청 힌트 2' and self.hint_data.loc[step, '요청 힌트 1'].strip():
                hint = self.hint_data.loc[step, '요청 힌트 1']
            else: # 그래도 비어있으면 기본 힌트 사용
                hint = self.hint_data.loc[step, '기본 힌트']

        if not hint.strip():
            return "더 이상 드릴 힌트가 없네요. 주변을 잘 둘러보세요!"

        return self._rephrase_as_npc(hint, user_question=text_message)

# NPC 인스턴스 생성 및 초기화
try:
    if os.path.exists(CSV_PATH):
        # 단일 NPC 인스턴스를 생성합니다.
        single_npc_instance = trainNPC(csv_path=CSV_PATH)
        # 각 씬(ca2, cb2)이 동일한 인스턴스를 참조하도록 설정합니다.
        npcs['ca2'] = single_npc_instance
        npcs['cb2'] = single_npc_instance
        print(f"모든 씬에 대한 NPC 초기화 성공 (CSV: {CSV_PATH}).")
    else:
        print(f"경고: CSV 파일을 찾을 수 없습니다: {CSV_PATH}")
except Exception as e:
    print(f"NPC 초기화 실패: {e}")


# 공통 응답 처리 함수
def create_response(data, status_code=200):
    return app.response_class(
        response=json.dumps(data, ensure_ascii=False, indent=None),
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )

# Flask API 엔드포인트들
@app.route('/ping')
def ping():
    """서버 상태 확인용 엔드포인트"""
    return "pong"

@app.route('/hint/default', methods=['GET', 'POST'])
def get_default_hint():
    """1. 사용자가 말 없이 힌트를 요청했을 때"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            scene = data.get('scene', 'cb2')
            step = int(data['step'])
        else: # GET
            scene = request.args.get('scene', 'cb2')
            step = int(request.args.get('step'))

        if scene not in npcs:
            return f"'{scene}' 씬이 초기화되지 않았습니다.", 500
        
        npc = npcs[scene]
        hint = npc.get_default_hint(step)
        return hint

    except (TypeError, KeyError):
        return "필수 파라미터 'step'이 누락되었거나 형식이 잘못되었습니다.", 400
    except ValueError:
        return "'step' 파라미터는 정수여야 합니다.", 400
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}", 500

@app.route('/hint/question', methods=['GET', 'POST'])
def get_question_hint():
    """2. 사용자가 직접 질문을 통해 힌트를 요청했을 때"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            scene = data.get('scene', 'cb2')
            step = int(data['step'])
            count = int(data.get('count', 1))
            text_message = data['text_message']
        else: # GET
            scene = request.args.get('scene', 'cb2')
            step = int(request.args.get('step'))
            count = int(request.args.get('count', 1))
            text_message = request.args.get('text_message', '')

        if not text_message:
            return "필수 파라미터 'text_message'가 누락되었습니다.", 400

        if scene not in npcs:
            return f"'{scene}' 씬이 초기화되지 않았습니다.", 500

        npc = npcs[scene]
        hint = npc.get_question_hint(step, count, text_message)
        return hint

    except (TypeError, KeyError):
        return "필수 파라미터('step', 'text_message')가 누락되었거나 형식이 잘못되었습니다.", 400
    except ValueError:
        return "'step'과 'count' 파라미터는 정수여야 합니다.", 400
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}", 500

@app.route('/view/hint-csv', methods=['GET'])
def download_hint_csv():
    """
    hint_message_for_NPC.csv 파일을 클라이언트에 전송합니다.
    """
    if not os.path.exists(CSV_PATH):
        return "CSV 파일을 찾을 수 없습니다.", 404
    return send_file(
        CSV_PATH,
        mimetype='text/csv',
        as_attachment=True,
        download_name='hint_message_for_NPC.csv'
    )

if __name__ == '__main__':
    # 0.0.0.0으로 설정하면 외부에서 접근 가능
    app.run(host='0.0.0.0', port=14724, debug=True)

"""
python -m api
"""

"""
# --- API 테스트용 curl 명령어 예시 ---
# 서버가 실행 중일 때, 터미널에서 아래 명령어를 실행하여 테스트할 수 있습니다.
# URL의 공백이나 특수문자를 위해 큰따옴표("")로 감싸주는 것이 안전합니다.

# 1. 사용자가 말 없이 힌트를 요청했을 때 (/hint/default)
# 1-1. 기본값(scene=cb2)으로 1단계 힌트 요청
# curl "http://127.0.0.1:3000/hint/default?step=1"

# 1-2. 'ca2' 씬의 2단계 힌트 요청
# curl "http://127.0.0.1:3000/hint/default?scene=ca2&step=2"


# 2. 사용자가 직접 질문을 통해 힌트를 요청했을 때 (/hint/question)
# 2-1. 'cb2' 씬, 1단계, 첫 번째(count=1) 질문
# curl "http://127.0.0.1:3000/hint/question?step=1&count=1&text_message=여기서%20어떻게%20해야%20하나요?"

# 2-2. 'ca2' 씬, 3단계, 두 번째(count=2) 질문
# curl "http://127.0.0.1:3000/hint/question?scene=ca2&step=3&count=2&text_message=탈출구는%20어디에%20있나요?"

# 2-3. 필수 파라미터(text_message) 누락 시 에러 응답 테스트
# curl "http://127.0.0.1:3000/hint/question?step=1&count=1"

# 2-4. 존재하지 않는 step 요청 시 에러 응답 테스트
# curl "http://127.0.0.1:3000/hint/default?step=999"




# [ POST 방식 (JSON) ]
# 1. 사용자가 말 없이 힌트를 요청했을 때 (/hint/default)
# curl -X POST -H "Content-Type: application/json" -d "{\"scene\": \"ca2\", \"step\": 2}" "http://127.0.0.1:3000/hint/default"

# 2. 사용자가 직접 질문을 통해 힌트를 요청했을 때 (/hint/question)
# curl -X POST -H "Content-Type: application/json" -d "{\"scene\": \"ca2\", \"step\": 3, \"count\": 2, \"text_message\": \"탈출구는 어디에 있나요?\"}" "http://127.0.0.1:3000/hint/question"

# 2-1. 필수 파라미터(text_message) 누락 시 에러 응답 테스트 (POST)
# curl -X POST -H "Content-Type: application/json" -d "{\"step\": 1, \"count\": 1}" "http://127.0.0.1:3000/hint/question"
"""