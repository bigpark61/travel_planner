# ✈️ AI Travel Planner

OpenAI와 NAVER API HUB를 활용하여 여행지를 추천하고,
해당 지역의 맛집 정보를 검색하여 여행 계획을 생성하는 AI 기반 여행 플래너입니다.

---

## 1. 프로젝트 소개

사용자가 여행 날짜를 입력하면 AI가 여행지를 추천하고,
NAVER API HUB의 지역 검색 API를 이용하여 추천 여행지 주변의 맛집 정보를 검색합니다.

검색된 정보를 바탕으로 OpenAI가 최종 여행 리포트를 생성합니다.

### 주요 처리 과정

사용자 입력
↓
OpenAI 여행지 추천
↓
NAVER API HUB 지역/맛집 검색
↓
OpenAI 최종 여행 리포트 생성
↓
결과 화면 출력 및 저장

---

## 2. 주요 기능

### AI 여행지 추천

OpenAI API를 이용하여 여행 날짜와 조건에 적합한 여행지를 추천합니다.

### 맛집 검색

NAVER API HUB의 지역 검색 API를 이용하여 추천 여행지의 맛집 정보를 검색합니다.

### 여행 계획 생성

AI 추천 결과와 맛집 검색 결과를 결합하여 최종 여행 계획을 생성합니다.

### 결과 저장

생성된 여행 계획과 원본 데이터를 `results` 폴더에 저장할 수 있습니다.

---

## 3. 사용 기술

| 구분 | 기술 |
|---|---|
| Language | Python |
| Web Framework | Flask |
| CORS | Flask-CORS |
| AI | OpenAI API |
| 지역 검색 | NAVER API HUB |
| HTTP 통신 | Requests |
| 환경변수 | python-dotenv |
| Version Control | Git / GitHub |

---

## 4. 프로젝트 구조

```text
travel_planner/
│
├── app.py
├── travel_planner.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
├── templates/
│   └── ...
│
├── static/
│   ├── css/
│   └── js/
│
├── results/
│   ├── YYYY-MM-DD_travel_plan.md
│   └── YYYY-MM-DD_raw.json
│
└── venv/
```

※ 실제 프로젝트의 파일 및 폴더 구성에 따라 일부 항목은 다를 수 있습니다.

---

## 5. 가상환경 생성

프로젝트 폴더로 이동합니다.

```powershell
cd C:\temp\travel_planner
```

가상환경을 생성합니다.

```powershell
py -3.12 -m venv venv
```

PowerShell에서 스크립트 실행이 차단되는 경우 현재 PowerShell 세션에서만 실행을 허용합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

가상환경을 활성화합니다.

```powershell
.\venv\Scripts\Activate.ps1
```

정상적으로 활성화되면 다음과 같이 `(venv)`가 표시됩니다.

```text
(venv) PS C:\temp\travel_planner>
```

---

## 6. 패키지 설치

필요한 Python 패키지를 설치합니다.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt`

```text
Flask
flask-cors
requests
python-dotenv
openai
```

---

## 7. 환경변수 설정

프로젝트 루트 폴더에 `.env` 파일을 생성합니다.

```env
OPENAI_API_KEY=본인의_OPENAI_API_KEY

NAVER_API_URL=https://naverapihub.apigw.ntruss.com/search/v1/local
NAVER_CLIENT_ID=본인의_NAVER_CLIENT_ID
NAVER_CLIENT_SECRET=본인의_NAVER_CLIENT_SECRET
```

### NAVER API HUB 인증 Header

NAVER API HUB에서는 다음 Header를 사용합니다.

```python
headers = {
    "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
    "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET
}
```

기존 NAVER Developers API의

```text
X-Naver-Client-Id
X-Naver-Client-Secret
```

과 다르므로 주의해야 합니다.

---

## 8. 프로그램 실행

### Flask 웹 애플리케이션 실행

가상환경이 활성화된 상태에서 실행합니다.

```powershell
python app.py
```

또는 가상환경의 Python을 직접 지정할 수 있습니다.

```powershell
.\venv\Scripts\python.exe app.py
```

Flask 서버가 정상적으로 실행되면 터미널에 표시되는 로컬 주소로 접속합니다.

예:

```text
http://127.0.0.1:5000
```

---

## 9. 콘솔 프로그램 실행

여행 날짜를 지정하여 실행할 경우:

```powershell
python travel_planner.py --date 2026-09-10
```

실행 과정 예시:

```text
[1/3] 1차 추천 생성 중(LLM)...
    - recommended_city: 제주도

[2/3] 맛집 검색 중(지도/장소 API)...
    - 맛집 검색 완료

[3/3] 최종 리포트 생성 중(LLM)...
    - 리포트 생성 완료

완료!
```

---

## 10. 결과 파일

프로그램에서 결과 저장 기능을 사용하는 경우 `results` 폴더에서 생성된 결과를 확인할 수 있습니다.

```text
results/
├── 2026-09-10_travel_plan.md
└── 2026-09-10_raw.json
```

`travel_plan.md`는 최종 여행 계획이며,
`raw.json`은 프로그램 처리 과정에서 생성된 원본 데이터입니다.

---

## 11. NAVER API HUB

지역 및 맛집 검색에는 NAVER API HUB의 지역 검색 API를 사용합니다.

```text
GET /search/v1/local
```

환경변수에는 다음 호출 URL을 설정합니다.

```env
NAVER_API_URL=https://naverapihub.apigw.ntruss.com/search/v1/local
```

주요 검색 파라미터 예시:

```python
params = {
    "query": "제주 맛집",
    "display": 5,
    "start": 1,
    "sort": "comment",
    "format": "json"
}
```

---

## 12. 보안 주의사항

OpenAI API Key와 NAVER API HUB 인증정보는 GitHub에 업로드하면 안 됩니다.

`.gitignore`에 다음 내용을 추가합니다.

```gitignore
.env
.env.*
venv/
.venv/
__pycache__/
*.pyc
```

GitHub에는 실제 API Key 대신 `.env.example` 파일을 제공하는 방법을 권장합니다.

예:

```env
OPENAI_API_KEY=your_openai_api_key
NAVER_API_URL=https://naverapihub.apigw.ntruss.com/search/v1/local
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

---

## 13. GitHub 업데이트

변경된 파일을 확인합니다.

```powershell
git status
```

변경 내용을 추가합니다.

```powershell
git add .
```

커밋합니다.

```powershell
git commit -m "Update travel planner and NAVER API HUB integration"
```

GitHub에 업로드합니다.

```powershell
git push origin main
```

---

## 14. 실행 오류 확인

### Flask가 없는 경우

```text
ModuleNotFoundError: No module named 'flask'
```

해결:

```powershell
python -m pip install flask
```

### Flask-CORS가 없는 경우

```text
ModuleNotFoundError: No module named 'flask_cors'
```

해결:

```powershell
python -m pip install flask-cors
```

### Requests가 없는 경우

```text
ModuleNotFoundError: No module named 'requests'
```

해결:

```powershell
python -m pip install requests
```

개별적으로 설치하기보다는 다음 명령으로 필요한 패키지를 한 번에 설치하는 것을 권장합니다.

```powershell
python -m pip install -r requirements.txt
```

---

## 15. 프로젝트 목표

이 프로젝트는 다음 내용을 학습하고 구현하는 것을 목표로 합니다.

- Python 기반 웹 애플리케이션 개발
- Flask를 이용한 Backend 구현
- OpenAI API 연동
- NAVER API HUB 외부 API 연동
- `.env`를 이용한 API Key 관리
- JSON 데이터 처리
- AI와 외부 검색 데이터의 결합
- Git/GitHub를 이용한 버전 관리
- 가상환경을 이용한 Python 개발환경 관리

---

## License

본 프로젝트는 학습 및 실습 목적으로 제작되었습니다.
