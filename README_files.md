# XR Train 프로젝트 구조

## 📁 디렉토리 구조

### `/assets`
힌트 제공에 대한 스텝 구분 기준과 어떤 내용의 힌트를 제공해야 하는지에 대한 설명이 포함된 파일들이 존재합니다.

#### 파일 설명
- **`scenario.xlsx`**: 개념적으로 구분할 수 있는, 최대한 fine-grained하게 스텝이 구분되어있는 파일
- **`hint_message_for_NPC.csv`**: 게임 개발 내부적으로 구분할 수 있는, 비교적 coarse하게 스텝이 구분되어 있는 파일
  - API 코드에서 이 파일을 로드하여 사용

## 🚀 API 서버

### `api.py`
두 개의 API 엔드포인트를 서빙하기 위한 코드입니다.

#### 엔드포인트
- `/hint/default`
- `/hint/question`

#### 실행 방법
```bash
python api.py
```

실행 후 `localhost:3000`에서 API에 접근 가능
