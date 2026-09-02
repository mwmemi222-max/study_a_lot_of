from datetime import datetime
from fastapi import FastAPI, Request
import requests

app = FastAPI()

MOBILIFE_API_KEY = "ml_6471f90f6c06_6tsbiZSudxwNo7GBWGvq3u9ry4kFXiYIkhiThoi0tG0"  # 발급받은 API 키 입력
MOBILIFE_API_URL = "https://api.mobilife.example.com/v1"  # 모비라이프 API 실제 Endpoint


# 1. 첫 번째 이미지 형태: [카테고리/세트 최저가 요약 메세지]
def build_set_price_response():
    # 실제 구현 시: 모비라이프 API 호출하여 각 부위별 최저가 및 매물 조회
    # headers = {"Authorization": f"Bearer {MOBILIFE_API_KEY}"}
    # res = requests.get(f"{MOBILIFE_API_URL}/items/search", headers=headers)

    now_str = datetime.now().strftime("%I:%M").lstrip("0")  # 현재 시간 예: 8:23

    text_content = f"""[잔영 무기 시세]
Data based on 모비라이프 OpenAPI

💰 최저가 검색
:: 무기: 커브드 하프 1005 데카

:: 투구: 비늘 갑옷 투구 686 데카
:: 상의: 비늘 갑옷 상의 697 데카
:: 하의: 비늘 갑옷 하의 700 데카
:: 장갑: ❌ 매물 없음
:: 신발: ❌ 매물 없음

:: 목걸이: ❌ 매물 없음
:: 반지: ❌ 매물 없음

🕒 서버 데이터 갱신 시간: 오후 {now_str}"""

    return {
        "version": "2.0",
        "template": {"outputs": [{"simpleText": {"text": text_content}}]},
    }


# 2. 두 번째 이미지 형태: [단일 아이템 상세 시세 정보]
def build_item_detail_response(item_name: str):
    # 실제 구현 시: 사용자가 입력한 item_name으로 모비라이프 API 조회
    # headers = {"Authorization": f"Bearer {MOBILIFE_API_KEY}"}
    # res = requests.get(f"{MOBILIFE_API_URL}/market/{item_name}", headers=headers)

    now_str = datetime.now().strftime("%I:%M").lstrip("0")

    # API에서 받아온 값을 변수로 바인딩
    current_price = 101
    stock_count = 121
    stock_change = -91.6
    h1_change = +20.2
    h24_change = +24.7
    d7_change = +40.3
    max_price = 101
    min_price = 67
    remaining_api_calls = 9875

    text_content = f"""[🔍 {item_name} 시세 정보]

💰 현재 최저가: {current_price} 데카
📦 등록 수량: {stock_count}개 (24시간 전 대비 {stock_change}%)


📈 가격 변동률:
- 1시간 전 대비: {h1_change:+0.1f}%
- 24시간 전 대비: {h24_change:+0.1f}%
- 7일 전 대비: {d7_change:+0.1f}%


📊 최근 24시간 시세 추이 (OHLC):
- 최고가: {max_price} 데카
- 최저가: {min_price} 데카


⌛ 오늘 남은 검색 가능 횟수: {remaining_api_calls}회
🕒 서버 데이터 갱신 시간: 오후 {now_str}


Data based on 모비라이프 OpenAPI"""

    return {
        "version": "2.0",
        "template": {"outputs": [{"simpleText": {"text": text_content}}]},
    }


# 카카오톡 챗봇 스킬 엔드포인트
@app.post("/api/skill")
async def kakao_skill_handler(request: Request):
    payload = await request.json()

    # 카카오톡에서 발화자(사용자)가 입력한 메시지/파라미터 가져오기
    user_utterance = payload.get("userRequest", {}).get("utterance", "")

    # 조건에 따른 응답 분기
    if "잔영" in user_utterance or "세트" in user_utterance:
        return build_set_price_response()
    else:
        # 단일 아이템 검색 (기본값 예시)
        target_item = (
            user_utterance.strip() if user_utterance else "허상의 마력석"
        )
        return build_item_detail_response(target_item)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
