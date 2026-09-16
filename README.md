````markdown
## 1. 프로그램 실행 방법

Travel Planner는 다음 방식으로 실행할 수 있습니다.

1. Python 콘솔에서 직접 실행
2. Flask API 서버 실행
3. 웹 브라우저에서 실행

실행하기 전에 가상환경을 활성화하고 필요한 패키지가 설치되어 있어야 합니다.

---

### 1.1 가상환경 활성화

프로젝트 폴더로 이동합니다.

```powershell
cd C:\temp\travel_planner
```

PowerShell에서 가상환경을 활성화합니다.

```powershell
.\venv\Scripts\Activate.ps1
```

정상적으로 활성화되면 다음과 같이 `(venv)`가 표시됩니다.

```text
(venv) PS C:\temp\travel_planner>
```

PowerShell 실행 정책으로 인해 활성화가 차단되는 경우 현재 세션에서만 실행을 허용합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

---

### 1.2 콘솔 프로그램 실행

여행 날짜를 지정하여 Python 프로그램을 직접 실행할 수 있습니다.

```powershell
python travel_planner.py --date 2026-09-10
```

실행 과정 예:

```text
[1/3] 1차 추천 생성 중(LLM)...
    - recommended_city: 제주도

[2/3] 맛집 검색 중(NAVER API HUB)...
    - 맛집 검색 완료

[3/3] 최종 리포트 생성 중(LLM)...
    - 리포트 생성 완료

완료!
```

프로그램 실행 결과는 `results` 폴더에 저장됩니다.

예:

```text
results/
├── 2026-09-10_travel_plan.md
└── 2026-09-10_raw.json
```

---

## 2. API 방식으로 실행하기

Travel Planner는 Flask를 이용하여 Backend API 서버로 실행할 수 있습니다.

### 2.1 Flask API 서버 시작

가상환경이 활성화된 상태에서 다음 명령을 실행합니다.

```powershell
python app.py
```

또는 가상환경의 Python을 직접 지정할 수 있습니다.

```powershell
.\venv\Scripts\python.exe app.py
```

정상적으로 실행되면 다음과 비슷한 메시지가 나타납니다.

```text
* Serving Flask app 'app'
* Running on http://127.0.0.1:5000
```

이 상태에서는 Flask Backend 서버가 실행되고 있는 것입니다.

> Flask 서버가 실행되는 동안 해당 PowerShell 창을 종료하지 않습니다.

---

### 2.2 API 호출 구조

웹 화면에서 사용자가 여행 정보를 입력하면 JavaScript가 Flask API를 호출합니다.

전체적인 처리 구조는 다음과 같습니다.

```text
[사용자]
    │
    ▼
[웹 브라우저]
HTML / CSS / JavaScript
    │
    │ HTTP Request
    ▼
[Flask API : app.py]
    │
    ├──── OpenAI API
    │       │
    │       └─ 여행지 추천 / 여행계획 생성
    │
    └──── NAVER API HUB
            │
            └─ 지역 / 맛집 검색
    │
    ▼
[JSON Response]
    │
    ▼
[웹 브라우저 결과 표시]
```

즉, Flask의 `app.py`는 웹 화면과 OpenAI/NAVER 외부 API 사이에서 Backend 역할을 수행합니다.

---

### 2.3 API 동작 확인

Flask 서버가 실행 중인 상태에서 브라우저 또는 프로그램에서 `app.py`에 정의된 API Endpoint를 호출할 수 있습니다.

예를 들어 API가 다음과 같이 구현되어 있다면:

```python
@app.route("/api/plan", methods=["POST"])
def create_plan():
    ...
```

API 주소는 다음과 같습니다.

```text
http://127.0.0.1:5000/api/plan
```

POST 방식으로 여행 정보를 전달하면 Flask가 요청을 받아 OpenAI와 NAVER API HUB를 호출하고 결과를 JSON으로 반환합니다.

> 실제 API Endpoint 이름은 `app.py`에 정의된 Route를 기준으로 사용해야 합니다.

---

## 3. 웹 브라우저에서 실행하기

### 3.1 Backend 서버 실행

먼저 VS Code의 PowerShell에서 다음을 실행합니다.

```powershell
cd C:\temp\travel_planner
.\venv\Scripts\Activate.ps1
python app.py
```

다음 메시지가 나타나는지 확인합니다.

```text
* Running on http://127.0.0.1:5000
```

---

### 3.2 웹 브라우저 접속

Chrome, Edge 등의 웹 브라우저를 실행하고 Flask가 표시한 주소로 접속합니다.

```text
http://127.0.0.1:5000
```

정상적으로 설정되어 있다면 Travel Planner의 웹 화면이 나타납니다.

---

### 3.3 웹에서 여행 계획 생성

웹 화면에서 여행 날짜와 필요한 여행 조건을 입력한 후 실행 버튼을 클릭합니다.

처리 과정은 다음과 같습니다.

```text
① 사용자가 여행 조건 입력
        ↓
② 웹에서 Flask API 호출
        ↓
③ OpenAI가 여행지 추천
        ↓
④ NAVER API HUB에서 맛집 검색
        ↓
⑤ OpenAI가 최종 여행계획 생성
        ↓
⑥ 웹 화면에 결과 표시
```

API 호출에는 처리 시간이 필요하므로 AI 및 외부 API 응답이 완료될 때까지 잠시 기다립니다.

---

## 4. 외부 API 연동

Travel Planner에서는 두 종류의 외부 API를 사용합니다.

### 4.1 OpenAI API

OpenAI API는 다음 기능에 사용합니다.

- 여행지 추천
- 여행 조건 분석
- 검색된 지역 정보 활용
- 최종 여행계획 생성

환경변수:

```env
OPENAI_API_KEY=본인의_OPENAI_API_KEY
```

---

### 4.2 NAVER 장소 검색 API

추천 여행지의 지역 및 맛집 정보를 검색합니다. 사용하는 인증 방식에 따라 아래 설정 중 하나만 사용합니다.

Naver API HUB를 사용하는 경우:

```env
NAVER_API_URL=https://naverapihub.apigw.ntruss.com/search/v1/local
NCP_APIGW_API_KEY_ID=발급받은_API_KEY_ID
NCP_APIGW_API_KEY=발급받은_API_KEY
```

일반 Naver Open API를 사용하는 경우:

```env
NAVER_API_URL=https://openapi.naver.com/v1/search/local.json
NAVER_CLIENT_ID=발급받은_CLIENT_ID
NAVER_CLIENT_SECRET=발급받은_CLIENT_SECRET
```

---

## 5. API Key 보안 관리

OpenAI API Key와 NAVER API HUB 인증정보는 프로그램 실행에 필요한 중요한 보안 정보입니다.

API Key를 Python, HTML 또는 JavaScript 코드에 직접 작성하지 않습니다.

특히 Frontend JavaScript에 다음과 같이 API Key를 작성하면 안 됩니다.

```javascript
// 잘못된 예
const OPENAI_API_KEY = "실제_API_KEY";
```

웹 브라우저에서 실행되는 JavaScript 코드는 사용자가 확인할 수 있기 때문에 API Key가 노출될 수 있습니다.

따라서 API Key는 반드시 Backend에서 관리합니다.

```text
[웹 브라우저]
     │
     │ API Key 없음
     ▼
[Flask Backend]
     │
     │ .env에서 API Key 로딩
     ├──── OpenAI API
     └──── NAVER API HUB
```

프로젝트를 처음 실행할 때 프로젝트 루트에 로컬용 `.env` 파일을 만들고 인증정보를 입력합니다. 아래 값은 형식만 보여주는 예시이며, 실제 키를 README나 `.env_exam`에 입력하지 않습니다.

```env
OPENAI_API_KEY=여기에_로컬에서만_실제_키_입력

NAVER_API_URL=사용할_API의_URL
NCP_APIGW_API_KEY_ID=여기에_로컬에서만_실제_KEY_ID_입력
NCP_APIGW_API_KEY=여기에_로컬에서만_실제_KEY_입력
```

보안 규칙:

- 실제 API Key는 로컬 `.env`에만 입력합니다.
- `.env`, `.env.exam`, README, Python, HTML, JavaScript 파일에 실제 Key를 기록하거나 복사하지 않습니다.
- API Key가 포함된 파일을 GitHub에 Push하지 않습니다. `.gitignore`의 `.env` 및 `.env.*` 규칙을 삭제하지 않습니다.
- 화면 공유, 과제 제출, 스크린샷, 로그에 API Key가 보이지 않는지 확인합니다.
- Key가 노출되었다면 해당 서비스를 즉시 중지하거나 Key를 폐기하고 새 Key를 발급받습니다.
- 저장소에 이미 올라간 Key는 파일을 삭제해도 안전하지 않으므로 반드시 폐기하고 재발급합니다.

그리고 `.gitignore`에 반드시 다음 내용을 포함합니다.

```gitignore
.env
.env.*
venv/
.venv/
__pycache__/
*.pyc
```

GitHub Push 전에는 반드시 확인합니다.

```powershell
git status
git diff -- .
git grep -n -I -E "sk-[A-Za-z0-9_-]{20,}|NCP_APIGW_API_KEY=|NAVER_CLIENT_SECRET=" -- ':!README.md'
```

`git status`에 `.env` 또는 실제 키가 포함된 파일이 나타나지 않는지 확인한 후 Push합니다. 검색 명령이 실제 키를 출력하면 Push를 중지하고 해당 키를 폐기합니다.

> API Key가 GitHub 등에 노출된 경우 단순히 파일을 삭제하는 것만으로 끝내지 말고, 해당 API Key를 폐기한 후 새로운 Key를 발급받아야 합니다.

---

## 6. 결과물 확인 방법

### 웹 실행 결과

웹으로 실행한 경우 브라우저 화면에서 생성된 여행계획을 확인합니다.

```text
사용자 여행조건
      ↓
AI 추천 여행지
      ↓
NAVER 맛집 검색
      ↓
최종 여행계획
```

### 파일 저장 결과

파일 저장 기능을 사용하는 경우 `results` 폴더에서 확인합니다.

```text
results/
├── 2026-09-10_travel_plan.md
└── 2026-09-10_raw.json
```

`travel_plan.md`

- AI가 생성한 최종 여행 계획
- 추천 여행지
- 여행 추천 내용
- 맛집 정보
- 최종 일정

`raw.json`

- OpenAI/NAVER API 처리에 사용된 원본 데이터
- 프로그램 개발 및 오류 확인용 데이터

---

## 7. 실행 방법 요약

### 웹으로 실행

```powershell
cd C:\temp\travel_planner
.\venv\Scripts\Activate.ps1
python app.py
```

브라우저 접속:

```text
http://127.0.0.1:5000
```

### 콘솔로 실행

```powershell
python travel_planner.py --date 2026-09-10
```

### 프로그램 종료

Flask 서버가 실행 중인 PowerShell에서:

```text
Ctrl + C
```

가상환경 종료:

```powershell
deactivate
```
````


