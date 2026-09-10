"""
국내 여행지 추천 프로그램
- LLM API: OpenAI
- 지도/장소 검색 API: Naver Local Search
"""

import argparse
import json
import os
import re
import sys

import requests
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NAVER_API_KEY_ID = os.getenv("NCP_APIGW_API_KEY_ID") or os.getenv("NAVER_CLIENT_ID")
NAVER_API_KEY = os.getenv("NCP_APIGW_API_KEY") or os.getenv("NAVER_CLIENT_SECRET")
NAVER_API_URL = os.getenv("NAVER_API_URL")
USE_NAVER_API_HUB = bool(
    os.getenv("NCP_APIGW_API_KEY_ID") or os.getenv("NCP_APIGW_API_KEY")
)


def get_openai_client() -> Optional[OpenAI]:
    """Lazy-initialize and return an OpenAI client or None if API key missing."""
    if not OPENAI_API_KEY:
        return None
    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        return None

# 실행 중 발생한 오류를 모아두는 리스트 (최종 리포트의 "오류 요약"에 사용)
errors = []


def log_error(step: str, err_type: str, message: str) -> None:
    errors.append({"step": step, "type": err_type, "message": message})


# ---------------------------------------------------------------------------
# 4단계: CLI 인터페이스
# ---------------------------------------------------------------------------
def parse_args() -> tuple[str, bool]:
    parser = argparse.ArgumentParser(description="국내 여행지 추천 프로그램")
    parser.add_argument("--date", required=True, help='여행 날짜, 예: --date "2026-03-15"')
    parser.add_argument("--dry-run", action="store_true", help="외부 API 호출 없이 모의 실행합니다.")
    args = parser.parse_args()

    from datetime import datetime

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        parser.print_usage(sys.stderr)
        print('오류: 날짜 형식이 올바르지 않습니다. 예: --date "2026-03-15"', file=sys.stderr)
        sys.exit(1)

    return args.date, args.dry_run


def check_api_keys() -> None:
    global DRY_RUN
    if DRY_RUN:
        print('Dry-run: API 키 검사를 건너뜁니다.')
        return
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not NAVER_API_KEY_ID or not NAVER_API_KEY:
        missing.append("NCP_APIGW_API_KEY_ID / NCP_APIGW_API_KEY")
    if not NAVER_API_URL:
        missing.append("NAVER_API_URL")

    if missing:
        print(f"오류: 다음 API 키가 설정되지 않았습니다 -> {', '.join(missing)}")
        print('설정 방법: 프로젝트 루트에 .env 파일을 만들고 아래처럼 키를 추가하세요.')
        print('  OPENAI_API_KEY=sk-...')
        print('  NCP_APIGW_API_KEY_ID=...')
        print('  NCP_APIGW_API_KEY=...')
        print('  NAVER_API_URL=https://콘솔에서_발급받은_호출_URL')
        sys.exit(1)


def call_llm(prompt: str, system: Optional[str] = None) -> str:
    """Call OpenAI LLM and return the text content. Raises RuntimeError if client unavailable."""
    # Dry-run behavior is handled by callers (get_recommendation / generate_report).
    client = get_openai_client()
    if client is None:
        raise RuntimeError("OpenAI API key is not set. Set OPENAI_API_KEY in your .env file.")


    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        # Newer SDK returns choices with message property; handle safely
        choice = response.choices[0]
        if hasattr(choice, "message"):
            return choice.message.content
        # Fallback: try content field
        return getattr(choice, "content", str(choice))
    except Exception as e:
        raise


def extract_json(text: str) -> dict:
    """LLM 응답에 코드블록(```json ... ```)이 섞여 있어도 JSON 부분만 뽑아낸다."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("응답에서 JSON 형식을 찾지 못했습니다.")
    return json.loads(match.group(0))


# ---------------------------------------------------------------------------
# 5단계: 1차 추천(LLM) - 날씨/행사 정보
# ---------------------------------------------------------------------------
REQUIRED_KEYS = ["recommended_city", "weather", "events", "reason"]

# When True, skip real API calls and return canned responses for safe testing
DRY_RUN = False


def get_recommendation(travel_date: str) -> dict:
    global DRY_RUN
    if DRY_RUN:
        return {
            "recommended_city": "부산",
            "weather": "9월은 쾌청하고 온화하며 해안가 바람이 선선함",
            "events": ["해운대 가을 축제", "부산국제영화제"],
            "reason": "해변, 음식, 접근성이 좋아 가을 여행지로 적합합니다.",
        }
    system_prompt = (
        "너는 국내 여행 추천 전문가다. 사용자가 입력한 날짜를 기준으로 "
        "여행하기 좋은 국내 지역 1곳을 추천한다.\n"
        "다른 설명, 인사말, 코드블록 표시(```) 없이 아래 JSON 스키마만 정확히 출력하라.\n"
        '{"recommended_city": "지역명(string)", '
        '"weather": "해당 시기 일반적 날씨 요약(string)", '
        '"events": ["행사/축제 후보 1~3개(string)"], '
        '"reason": "추천 근거 2~4문장(string)"}'
    )
    prompt = f"{travel_date}에 여행하기 좋은 국내 지역을 추천해줘."

    for attempt in range(2):  # 최초 1회 + 재시도 1회 (무한 재시도 금지)
        try:
            raw = call_llm(prompt, system=system_prompt)
            data = extract_json(raw)
            if not all(key in data for key in REQUIRED_KEYS):
                raise ValueError(f"필수 키 누락: {REQUIRED_KEYS}")
            return data
        except Exception as e:
            if attempt == 0:
                print(f"    - JSON 파싱 실패, 재시도합니다... ({e})")
                # 재시도 시: 필수 키만 다시 출력하도록 프롬프트를 좁힌다.
                prompt = (
                    f"{travel_date} 여행 추천 결과를, 오직 {REQUIRED_KEYS} "
                    "이 네 개의 키만 포함한 JSON 객체로 다시 출력해줘. "
                    "그 외 텍스트는 절대 포함하지 마."
                )
                continue

            log_error("recommendation", "PARSE_ERROR", str(e))
            print(f"    - 오류: 추천 결과 파싱에 최종 실패했습니다({e}). 기본값으로 진행합니다.")
            return {
                "recommended_city": "정보 없음",
                "weather": "정보 없음",
                "events": [],
                "reason": "LLM 응답을 JSON으로 파싱하지 못했습니다.",
            }


# ---------------------------------------------------------------------------
# 6단계: 지도/장소 검색 API 연동 - 맛집 검색 (Naver Local Search)
# ---------------------------------------------------------------------------
def search_restaurants(city: str, count: int = 5) -> list[dict]:
    global DRY_RUN
    if DRY_RUN:
        # Return a small set of sample restaurants for dry-run/testing
        return [
            {"name": "모범횟집", "address": "부산 해운대구", "category": "해산물", "url": "http://example.com", "lat": "35.163", "lng": "129.163"},
            {"name": "달맞이카페", "address": "부산 달맞이길", "category": "카페", "url": "http://example.com", "lat": "35.165", "lng": "129.169"},
        ][:count]

    if not city or city == "정보 없음":
        return []

    if not NAVER_API_URL:
        log_error("place_search", "CONFIG_ERROR", "NAVER_API_URL is not set")
        print("    - 오류: .env에 API HUB 호출 URL인 NAVER_API_URL을 설정하세요.")
        return []

    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_API_KEY_ID,
        "X-NCP-APIGW-API-KEY": NAVER_API_KEY,
    }
    params = {"query": f"{city} 맛집", "display": count}

    try:
        res = requests.get(NAVER_API_URL, headers=headers, params=params, timeout=10)

        if res.status_code in (401, 403):
            detail = res.text[:300].strip()
            log_error("place_search", "AUTH_ERROR", f"HTTP {res.status_code}: {detail}")
            print(f"    - 오류: 인증 실패({res.status_code}). 키 값/헤더명을 확인하세요.")
            if detail:
                print(f"    - API 응답: {detail}")
            print("    - 맛집 섹션은 '데이터 없음'으로 처리하고 계속 진행합니다.")
            return []

        res.raise_for_status()
        items = res.json().get("items", [])

        if not items:
            log_error("place_search", "EMPTY_RESULT", f"0 results for query={params['query']}")
            print("    - 검색 결과 0건 (다음 단계로 진행)")
            return []

        restaurants = []
        tag_pattern = re.compile(r"<.*?>")
        for item in items:
            restaurants.append(
                {
                    "name": tag_pattern.sub("", item.get("title", "")),
                    "address": item.get("roadAddress") or item.get("address", ""),
                    "category": item.get("category", ""),
                    "url": item.get("link", ""),
                    "lat": item.get("mapy", ""),
                    "lng": item.get("mapx", ""),
                }
            )
        print(f"    - 맛집 {len(restaurants)}곳 검색 완료")
        return restaurants

    except requests.exceptions.RequestException as e:
        log_error("place_search", "NETWORK_ERROR", str(e))
        print(f"    - 오류: 네트워크 오류({e}). 맛집 섹션은 '데이터 없음'으로 처리합니다.")
        return []


# ---------------------------------------------------------------------------
# 7단계: 최종 리포트 생성 (LLM)
# ---------------------------------------------------------------------------
def generate_report(travel_date: str, recommendation: dict, restaurants: list[dict]) -> str:
    global DRY_RUN
    if DRY_RUN:
        # Build a simple Markdown report for dry-run
        if restaurants:
            restaurant_text = "\n".join(f"- {r['name']} ({r.get('category','')}) - {r.get('address','')}" for r in restaurants)
        else:
            restaurant_text = "데이터 없음 (장소 검색 결과 0건)"

        events_text = ", ".join(recommendation.get("events", [])) or "정보 없음"

        md = f"# {travel_date} 국내 여행 추천 리포트\n\n"
        md += f"## 추천 지역\n{recommendation.get('recommended_city')}\n\n"
        md += f"## 추천 이유\n{recommendation.get('reason')}\n\n"
        md += f"## 날씨 요약\n{recommendation.get('weather')}\n\n"
        md += f"## 행사/축제\n{events_text}\n\n"
        md += f"## 맛집 추천\n{restaurant_text}\n\n"
        md += "## 1일 일정 제안 (오전/오후/저녁)\n- 오전: 자유시간\n- 오후: 투어\n- 저녁: 식사\n"
        return md
    if restaurants:
        restaurant_text = "\n".join(
            f"- {r['name']} ({r.get('category', '')}) - {r.get('address', '')}"
            for r in restaurants
        )
    else:
        restaurant_text = "데이터 없음 (장소 검색 결과 0건)"

    events_text = ", ".join(recommendation.get("events", [])) or "정보 없음"

    prompt = f"""아래 정보를 바탕으로 국내 여행 추천 리포트를 Markdown으로 작성해줘.

여행 날짜: {travel_date}
추천 지역: {recommendation.get('recommended_city')}
추천 이유: {recommendation.get('reason')}
날씨: {recommendation.get('weather')}
행사/축제: {events_text}
맛집 목록:
{restaurant_text}

다음 형식(제목/소제목)을 반드시 지켜서 작성해줘:
# {travel_date} 국내 여행 추천 리포트
## 추천 지역
## 추천 이유
## 날씨 요약
## 행사/축제
## 맛집 추천
## 1일 일정 제안 (오전/오후/저녁)
"""

    try:
        return call_llm(prompt)
    except Exception as e:
        log_error("report_generation", "LLM_ERROR", str(e))
        print(f"    - 오류: 리포트 생성 실패({e}). 기본 리포트로 대체합니다.")
        return (
            f"# {travel_date} 국내 여행 추천 리포트\n\n"
            "리포트 생성 중 오류가 발생하여 기본 내용으로 대체되었습니다.\n"
        )


def append_error_section(report_md: str) -> str:
    if not errors:
        return report_md
    error_lines = "\n".join(f"- [{e['step']}] {e['type']}: {e['message']}" for e in errors)
    return report_md + f"\n\n## 오류 요약(errors)\n{error_lines}\n"


# ---------------------------------------------------------------------------
# 8단계: 결과 저장
# ---------------------------------------------------------------------------
def save_results(travel_date: str, recommendation: dict, restaurants: list[dict], report_md: str):
    os.makedirs("results", exist_ok=True)

    raw_data = {
        "recommendation": recommendation,
        "restaurants": restaurants,
        "errors": errors,
    }
    json_path = os.path.join("results", f"{travel_date}_raw.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    md_path = os.path.join("results", f"{travel_date}_travel_plan.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    return json_path, md_path


def main() -> None:
    global DRY_RUN
    travel_date, dry = parse_args()
    DRY_RUN = dry
    check_api_keys()

    print("[1/3] 1차 추천 생성 중(LLM)...")
    recommendation = get_recommendation(travel_date)
    print(f'    - recommended_city: "{recommendation.get("recommended_city")}"')

    print("[2/3] 맛집 검색 중(지도/장소 API)...")
    restaurants = search_restaurants(recommendation.get("recommended_city", ""))

    print("[3/3] 최종 리포트 생성 중(LLM)...")
    report_md = generate_report(travel_date, recommendation, restaurants)
    report_md = append_error_section(report_md)
    print("    - 리포트 생성 완료")

    json_path, md_path = save_results(travel_date, recommendation, restaurants, report_md)
    print(f"\n완료! {md_path} 를 확인하세요. (원본 데이터: {json_path})")


if __name__ == "__main__":
    main()
