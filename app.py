from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import travel_planner as tp

load_dotenv()

NAVER_API_KEY_ID = os.getenv("NCP_APIGW_API_KEY_ID") or os.getenv("NAVER_CLIENT_ID")
NAVER_API_KEY = os.getenv("NCP_APIGW_API_KEY") or os.getenv("NAVER_CLIENT_SECRET")
NAVER_API_URL = os.getenv("NAVER_API_URL")
USE_NAVER_API_HUB = bool(
    os.getenv("NCP_APIGW_API_KEY_ID") or os.getenv("NCP_APIGW_API_KEY")
)

# Debug: show whether keys are loaded (masked). Do not print secrets in full.
if NAVER_API_KEY_ID:
    print("NAVER API key ID loaded: ", NAVER_API_KEY_ID[:4] + "***")
else:
    print("NAVER API key ID not set")

if NAVER_API_KEY:
    print("NAVER API key loaded: ", NAVER_API_KEY[:4] + "***")
else:
    print("NAVER API key not set")


app = Flask(__name__, static_folder="web", static_url_path="/web")
CORS(app)  # 개발용: 모든 오리진 허용. 운영 시에는 특정 오리진만 허용하세요.


@app.route("/api/search")
def local_search():
    q = request.args.get("query", "")
    if not q:
        return jsonify({"error": "query required"}), 400

    if not NAVER_API_KEY_ID or not NAVER_API_KEY:
        return jsonify({"error": "NCP_APIGW_API_KEY_ID or NCP_APIGW_API_KEY not set"}), 500
    if not NAVER_API_URL:
        return jsonify({"error": "NAVER_API_URL not set in .env"}), 500

    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_API_KEY_ID,
        "X-NCP-APIGW-API-KEY": NAVER_API_KEY,
    }
    params = {"query": q, "display": 5}

    try:
        r = requests.get(NAVER_API_URL, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        detail = r.text[:300] if "r" in locals() else ""
        return jsonify({"error": str(e), "api_response": detail}), 500


@app.route("/api/plan")
def plan_route():
    """Run the travel planning flow: LLM recommendation -> place search -> report.
    Query params: date=YYYY-MM-DD (required), dry_run=1|0 (optional)
    """
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date parameter is required (YYYY-MM-DD)"}), 400

    dry = request.args.get("dry_run", "0")
    tp.DRY_RUN = dry.lower() in ("1", "true", "yes")

    # Run recommendation (may raise if LLM client missing when not dry-run)
    try:
        recommendation = tp.get_recommendation(date)
    except Exception as e:
        tp.log_error("api.plan", "LLM_ERROR", str(e))
        return jsonify({"error": "LLM recommendation failed", "detail": str(e)}), 500

    # Search restaurants
    try:
        restaurants = tp.search_restaurants(recommendation.get("recommended_city", ""))
    except Exception as e:
        tp.log_error("api.plan", "SEARCH_ERROR", str(e))
        restaurants = []

    # Generate report (LLM or dry-run)
    try:
        report_md = tp.generate_report(date, recommendation, restaurants)
    except Exception as e:
        tp.log_error("api.plan", "REPORT_ERROR", str(e))
        report_md = tp.append_error_section(f"# {date} 국내 여행 추천 리포트\n\n리포트 생성 실패: {e}\n")

    # Save results
    json_path, md_path = tp.save_results(date, recommendation, restaurants, report_md)

    return jsonify({
        "recommendation": recommendation,
        "restaurants": restaurants,
        "report_md": report_md,
        "json_path": json_path,
        "md_path": md_path,
    })


@app.route("/")
def index():
    # Serve the frontend index
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    # 개발용: 5000 포트에서 실행
    app.run(host="0.0.0.0", port=5000, debug=True)
