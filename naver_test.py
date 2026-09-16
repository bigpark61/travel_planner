import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY_ID = os.getenv("NCP_APIGW_API_KEY_ID") or os.getenv("NAVER_CLIENT_ID")
API_KEY = os.getenv("NCP_APIGW_API_KEY") or os.getenv("NAVER_CLIENT_SECRET")
API_URL = os.getenv("NAVER_API_URL")
USE_API_HUB = bool(os.getenv("NCP_APIGW_API_KEY_ID") or os.getenv("NCP_APIGW_API_KEY"))

headers = {
    "X-NCP-APIGW-API-KEY-ID": API_KEY_ID,
    "X-NCP-APIGW-API-KEY": API_KEY,
}

params = {
    "query": "해운대 맛집",
    "display": 5
}

if not API_URL:
    raise SystemExit(".env에 NAVER_API_URL을 설정하세요. API HUB 콘솔의 호출 URL을 사용합니다.")

response = requests.get(API_URL, headers=headers, params=params, timeout=10)

print("HTTP 상태코드:", response.status_code)
print("응답내용:")
print(response.text)