
.# 국내 여행지 추천 프로그램 개발 절차

과제 내용을 확인했습니다. LLM API + 지도/장소 API를 엮어서 CLI 프로그램을 만드는 과제네요. 아래 순서대로 진행하면 됩니다.

## 1단계: 개발 환경 및 API 제공자 선택

- Python 3.10 이상 설치 확인, 가상환경(`venv`) 생성
- **LLM API**: OpenAI 또는 Gemini 중 1개 선택
- **지도/장소 API**: Kakao Local 또는 Naver Local Search 중 1개 선택 (국내 장소 검색 가능해야 함)
- 필요 라이브러리 설치: `openai`(또는 `google-generativeai`), `requests`, `python-dotenv`

```bash
python -m venv venv
source venv/bin/activate  # Windows는 venv\Scripts\activate
pip install openai requests python-dotenv
```

## 2단계: API 키 발급 및 `.env` 설정

- 선택한 LLM/지도 API의 키를 각 콘솔(OpenAI Platform, Kakao Developers 등)에서 발급
- 프로젝트 루트에 `.env` 파일 생성 후 키 기록, **`.gitignore`에 반드시 추가**

```
OPENAI_API_KEY=your_key
KAKAO_API_KEY=your_key
```

## 3단계: 프로젝트 구조 설계

```
travel_planner/
├── travel_planner.py   # 메인 실행 파일
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── results/            # 실행 시 생성
```

## 4단계: CLI 인터페이스 구현

- `argparse`로 `-date "YYYY-MM-DD"` 필수 옵션 처리
- `datetime.strptime`으로 날짜 형식 검증 → 실패 시 사용법 출력 후 종료

## 5단계: 1차 추천(LLM) — 날씨/행사 정보

- 사용자가 입력한 날짜를 프롬프트에 넣어 LLM 호출
- **반드시 JSON만 출력**하도록 프롬프트 설계 (예: "다른 설명 없이 JSON만 출력하라")
- 최소 스키마: `recommended_city`, `weather`, `events`(배열), `reason`
- `json.loads()`로 파싱, 실패 시 재시도 1회(프롬프트를 "필수 키만 JSON으로" 수정해서)

## 6단계: 맛집 검색(지도/장소 API) 연동

- 1차 JSON의 `recommended_city`를 키워드로 장소 검색 API 호출
- 응답에서 `name`, `address`, `category`, `url`, `x/y`(또는 `lat/lng`) 추출, 5곳 권장
- **인증 실패(401/403)나 0건 결과가 나와도 프로그램이 멈추지 않도록** try-except로 감싸고, 실패 시 "데이터 없음" 상태로 다음 단계 진행

## 7단계: 최종 리포트 생성(LLM)

- 1차 JSON + 맛집 목록(0건일 수 있음)을 다시 LLM에 넘겨 Markdown 리포트 생성 요청
- 리포트 필수 항목: 추천 지역/이유, 날씨 요약, 행사/축제, 맛집 리스트(0건 시 "데이터 없음"), 1일 일정 제안

## 8단계: 에러 처리 및 오류 로그 관리

- 내부적으로 `errors` 리스트(딕셔너리 배열: `step`, `type`, `message`)를 관리하며 각 단계 실패를 기록
- API 키 미설정 → 즉시 종료 + 설정 방법 안내
- LLM JSON 파싱 실패 → 재시도 최대 1회(무한 재시도 금지)

## 9단계: 결과 저장

- `results/` 폴더 생성
- `results/{date}_raw.json`: 1차 추천 JSON + 맛집 검색 결과 + `errors` 배열
- `results/{date}_travel_plan.md`: 최종 리포트

## 10단계: README.md 작성

- 프로그램 개요, 실행 방법(`python travel_planner.py --date "YYYY-MM-DD"`), API 키 설정 방법(`.env` 안내, 절대 실제 키 값은 적지 않기), 결과물 확인 방법

## 11단계: 테스트

과제에 나온 예시 케이스로 직접 검증:

- 정상 흐름 (날짜 입력 → 리포트 생성)
- 맛집 검색 0건 케이스
- 지도 API 인증 실패(401/403) 케이스
- 잘못된 날짜 형식 입력 시 사용법 출력 후 종료

## (선택) 보너스 과제

- 복수 지역 추천: `recommended_cities` 배열로 확장, 지역별 반복 처리
- 결과 캐싱: 같은 날짜로 재실행 시 저장된 JSON이 있으면 API 호출 건너뛰기

---

원하시면 4~9단계 중 특정 단계(예: LLM 프롬프트 설계, argparse 코드, 에러 처리 로직)부터 실제 코드로 같이 작성해볼 수 있습니다. 어느 부분부터 시작하고 싶으세요?