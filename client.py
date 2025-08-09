import requests
import argparse

# 서버의 기본 URL
BASE_URL = "http://127.0.0.1:3001"

def get_hint_from_api(step, count):
    """
    /hint API를 호출하여 힌트를 요청하고 결과를 출력합니다.
    """
    print(f"--- [TEST] step={step}, count={count} ---")
    try:
        # GET 요청 보내기
        response = requests.get(f"{BASE_URL}/hint", params={"step": step, "count": count})
        
        print(f"Status Code: {response.status_code}")
        
        # 응답이 성공적인지 확인하고 JSON 파싱
        if response.ok:
            print("Response JSON:", response.json())
        else:
            print("Error Response:", response.text)
            
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    print("-" * 30 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API 클라이언트로 /hint 엔드포인트를 테스트합니다.")
    parser.add_argument("--step", help="힌트를 요청할 단계(step)")
    parser.add_argument("--count", help="해당 단계의 힌트 요청 횟수(count)")
    
    args = parser.parse_args()

    # 1단계 힌트 첫 번째 요청
    get_hint_from_api(step=1, count=1)
    
    # 1단계 힌트 두 번째 요청
    get_hint_from_api(step=1, count=2)
    
    # 1단계 힌트 세 번째 요청
    get_hint_from_api(step=1, count=3)
    
    # 정보가 없는 단계 요청
    get_hint_from_api(step=99, count=1)

    # 잘못된 파라미터 타입 요청 (400 Bad Request 테스트)
    get_hint_from_api(step="abc", count=1)

    print("모든 테스트가 완료되었습니다.")
    print("\n사용법 예시:")
    print("python client.py --step 5 --count 1")