
import requests
import json

# API 서버의 기본 URL
# BASE_URL = "http://127.0.0.1:14724"
BASE_URL = "https://27df451c45ad.ngrok-free.app"

def print_request_response(title, url, data, response):
    """요청과 응답을 예쁘게 출력하는 함수"""
    print(f"--- {title} ---")
    print(f"요청 URL: {url}")
    if data:
        print("요청 내용:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("요청 내용: (GET 요청)")
    print()
    
    if response.status_code == 200:
        print("✅ 요청 성공!")
        print("응답 내용:")
        try:
            # JSON 응답인 경우
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            # 텍스트 응답인 경우
            print(response.text)
    else:
        print(f"❌ 오류 발생! (상태 코드: {response.status_code})")
        print("오류 내용:")
        print(response.text)
    print("\n" + "="*50 + "\n")

def print_csv_download_response(title, url, response):
    """CSV 파일 다운로드 요청과 응답을 예쁘게 출력하는 함수"""
    print(f"--- {title} ---")
    print(f"요청 URL: {url}")
    print("요청 내용: (GET 요청)")
    print()
    
    if response.status_code == 200:
        print("✅ 요청 성공!")
        print("응답 내용:")
        
        # Content-Type 확인
        content_type = response.headers.get('Content-Type', '')
        print(f"Content-Type: {content_type}")
        
        # Content-Disposition 확인 (파일명 정보)
        content_disposition = response.headers.get('Content-Disposition', '')
        if content_disposition:
            print(f"Content-Disposition: {content_disposition}")
        
        # 파일 크기 확인
        content_length = response.headers.get('Content-Length', '')
        if content_length:
            print(f"파일 크기: {content_length} bytes")
        elif response.content:
            print(f"파일 크기: {len(response.content)} bytes")
        
        # CSV 내용 미리보기 (처음 몇 줄만)
        if response.content:
            try:
                content_text = response.content.decode('utf-8')
                lines = content_text.split('\n')
                print("\nCSV 파일 내용 미리보기 (처음 5줄):")
                for i, line in enumerate(lines[:5]):
                    if line.strip():  # 빈 줄이 아닌 경우만 출력
                        print(f"{i+1}: {line}")
                if len(lines) > 5:
                    print(f"... (총 {len([l for l in lines if l.strip()])}줄)")
            except UnicodeDecodeError:
                print("CSV 파일 내용을 텍스트로 디코딩할 수 없습니다.")
        else:
            print("파일 내용이 비어있습니다.")
            
    else:
        print(f"❌ 오류 발생! (상태 코드: {response.status_code})")
        print("오류 내용:")
        print(response.text)
    print("\n" + "="*50 + "\n")

def test_api():
    """모든 API 엔드포인트를 테스트합니다."""
    
    # 1. 기본 힌트 요청 테스트 (GET 방식)
    # 1-1. 기본값(scene=cb2)으로 1단계 힌트 요청
    url1 = f"{BASE_URL}/hint/default?step=0"
    response1 = requests.get(url1)
    print_request_response("1-1. 기본 힌트 요청 (GET, cb2 씬, 1단계(입력 0))", url1, None, response1)

    # 1-2. 'ca2' 씬의 2단계 힌트 요청
    url2 = f"{BASE_URL}/hint/default?scene=ca2&step=1"
    response2 = requests.get(url2)
    print_request_response("1-2. 기본 힌트 요청 (GET, ca2 씬, 2단계(입력 1))", url2, None, response2)

    # 2. 질문 기반 힌트 요청 테스트 (GET 방식)
    # 2-1. 'cb2' 씬, 1단계, 첫 번째(count=1) 질문
    url3 = f"{BASE_URL}/hint/question?step=0&count=1&text_message=여기서 어떻게 해야 하나요?"
    response3 = requests.get(url3)
    print_request_response("2-1. 질문 힌트 요청 (GET, cb2 씬, 1단계(입력 0))", url3, None, response3)

    # 2-2. 'ca2' 씬, 3단계, 두 번째(count=2) 질문
    url4 = f"{BASE_URL}/hint/question?scene=ca2&step=2&count=2&text_message=탈출구는 어디에 있나요?"
    response4 = requests.get(url4)
    print_request_response("2-2. 질문 힌트 요청 (GET, ca2 씬, 2단계(입력 1))", url4, None, response4)

    # 3. POST 방식 테스트
    # 3-1. 기본 힌트 요청 (POST)
    data5 = {"scene": "ca2", "step": 1}
    url5 = f"{BASE_URL}/hint/default"
    response5 = requests.post(url5, json=data5)
    print_request_response("3-1. 기본 힌트 요청 (POST, ca2 씬, 2단계(입력 1))", url5, data5, response5)

    # 3-2. 질문 기반 힌트 요청 (POST)
    data6 = {
        "scene": "ca2", 
        "step": 2, 
        "count": 2, 
        "text_message": "탈출구는 어디에 있나요?"
    }
    url6 = f"{BASE_URL}/hint/question"
    response6 = requests.post(url6, json=data6)
    print_request_response("3-2. 질문 힌트 요청 (POST, ca2 씬, 2단계(입력 1))", url6, data6, response6)

    # 4. 오류 케이스 테스트
    # 4-1. 필수 파라미터(text_message) 누락 시 에러 응답 테스트 (GET)
    url7 = f"{BASE_URL}/hint/question?step=0&count=1"
    response7 = requests.get(url7)
    print_request_response("4-1. 오류 테스트 - text_message 누락 (GET)", url7, None, response7)

    # 4-2. 존재하지 않는 step 요청 시 에러 응답 테스트
    url8 = f"{BASE_URL}/hint/default?step=999"
    response8 = requests.get(url8)
    print_request_response("4-2. 오류 테스트 - 존재하지 않는 step", url8, None, response8)

    # 4-3. 필수 파라미터(text_message) 누락 시 에러 응답 테스트 (POST)
    data9 = {"step": 0, "count": 1}
    url9 = f"{BASE_URL}/hint/question"
    response9 = requests.post(url9, json=data9)
    print_request_response("4-3. 오류 테스트 - text_message 누락 (POST)", url9, data9, response9)

    # 5. CSV 파일 다운로드 테스트
    # 5-1. hint-csv 파일 다운로드 테스트
    url10 = f"{BASE_URL}/view/hint-csv"
    response10 = requests.get(url10)
    print_csv_download_response("5-1. CSV 파일 다운로드 테스트", url10, response10)

if __name__ == "__main__":
    # API 서버가 실행 중인지 확인
    print("API 서버가 실행 중인지 확인...")
    try:
        requests.get(f"{BASE_URL}/ping")
    except requests.ConnectionError:
        print("오류: API 서버가 실행 중이 아닙니다.")
        print("다른 터미널에서 'python api.py' 명령으로 서버를 먼저 실행해주세요.")
    else:
        test_api()
        
"""
python client.py
"""