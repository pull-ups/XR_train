
# 1. 사용자가 말 없이 힌트를 요청했을 때 (/hint/default)
# 1-1. 기본값(scene=cb2)으로 1단계 힌트 요청
# curl "https://150308f6b21a.ngrok-free.app/hint/default?step=1"

# 1-2. 'ca2' 씬의 2단계 힌트 요청
# curl "https://150308f6b21a.ngrok-free.app/hint/default?scene=ca2&step=2"


# 2. 사용자가 직접 질문을 통해 힌트를 요청했을 때 (/hint/question)
# 2-1. 'cb2' 씬, 1단계, 첫 번째(count=1) 질문
# curl "https://150308f6b21a.ngrok-free.app/hint/question?step=1&count=1&text_message=여기서%20어떻게%20해야%20하나요?"

# 2-2. 'ca2' 씬, 3단계, 두 번째(count=2) 질문
# curl "https://150308f6b21a.ngrok-free.app/hint/question?scene=ca2&step=3&count=2&text_message=탈출구는%20어디에%20있나요?"

# 2-3. 필수 파라미터(text_message) 누락 시 에러 응답 테스트
# curl "https://150308f6b21a.ngrok-free.app/hint/question?step=1&count=1"

# 2-4. 존재하지 않는 step 요청 시 에러 응답 테스트
# curl "https://150308f6b21a.ngrok-free.app/hint/default?step=999"




# [ POST 방식 (JSON) ]
# 1. 사용자가 말 없이 힌트를 요청했을 때 (/hint/default)
# curl -X POST -H "Content-Type: application/json" -d "{\"scene\": \"ca2\", \"step\": 2}" "https://150308f6b21a.ngrok-free.app/hint/default"

# 2. 사용자가 직접 질문을 통해 힌트를 요청했을 때 (/hint/question)
# curl -X POST -H "Content-Type: application/json" -d "{\"scene\": \"ca2\", \"step\": 3, \"count\": 2, \"text_message\": \"탈출구는 어디에 있나요?\"}" "https://150308f6b21a.ngrok-free.app/hint/question"

# 2-1. 필수 파라미터(text_message) 누락 시 에러 응답 테스트 (POST)
# curl -X POST -H "Content-Type: application/json" -d "{\"step\": 1, \"count\": 1}" "https://150308f6b21a.ngrok-free.app/hint/question"