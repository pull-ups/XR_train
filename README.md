# XR 재난 훈련 힌트 API

이 API는 XR 재난 훈련 시뮬레이션에서 플레이어의 상황에 맞는 힌트를 제공하기 위해 만들어졌습니다. 플레이어의 단계(step)와 질문 여부에 따라 두 가지 종류의 힌트를 제공합니다.


---

## API 엔드포인트

### 1. 기본 힌트 제공 (`/hint/default`)

사용자가 별도의 질문 없이 힌트를 요청할 때 사용합니다. 현재 단계(`step`)에 해당하는 일반적인 힌트를 제공합니다.

-   **URL:** `/hint/default`
-   **Method:** `GET`, `POST`
-   **Output:** `String` - NPC의 말투로 변환된 힌트 메시지

#### Input Arguments

| 이름    | 타입    | 필수 | 기본값 | 설명                                     |
| :------ | :------ | :--- | :----- | :--------------------------------------- |
| `scene` | String  | No   | 'cb2'  | 현재 씬 이름 ('ca2' 또는 'cb2')          |
| `step`  | Integer | Yes  | -      | 사용자의 현재 진행 단계 (CSV의 '세부단계') |

#### 사용 예시

**GET 방식**
```bash
curl "{IP}/hint/default?scene=ca2&step=2"
```

**POST 방식 (JSON)**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scene": "ca2", "step": 2}' \
  "{IP}/hint/default"
```

### 2. 질문 기반 힌트 제공 (`/hint/question`)

사용자가 구체적인 질문을 입력하여 힌트를 요청할 때 사용합니다. 사용자의 질문 내용과 요청 횟수(`count`)를 바탕으로 더 구체적인 힌트를 제공합니다.

-   **URL:** `/hint/question`
-   **Method:** `GET`, `POST`
-   **Output:** `String` - 사용자의 질문을 참고하여 NPC 말투로 변환된 힌트 메시지

#### Input Arguments

| 이름           | 타입    | 필수 | 기본값 | 설명                                                                 |
| :------------- | :------ | :--- | :----- | :------------------------------------------------------------------- |
| `scene`        | String  | No   | 'cb2'  | 현재 씬 이름 ('ca2' 또는 'cb2')                                      |
| `step`         | Integer | Yes  | -      | 사용자의 현재 진행 단계                                              |
| `count`        | Integer | No   | 1      | 해당 단계에서 힌트를 요청한 횟수 (1 또는 2)                          |
| `text_message` | String  | Yes  | -      | 사용자가 입력한 질문 메시지 (예: "여기서 어떻게 해야 하나요?") |

#### 사용 예시

**GET 방식**
```bash
curl "{IP}/hint/question?scene=ca2&step=3&count=2&text_message=탈출구는%20어디에%20있나요?"
```

**POST 방식 (JSON)**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scene": "ca2", "step": 3, "count": 2, "text_message": "탈출구는 어디에 있나요?"}' \
  "{IP}/hint/question"
```