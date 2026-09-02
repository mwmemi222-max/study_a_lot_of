from fastapi import FastAPI, Request
import requests

app = FastAPI()

MOBILIFE_API_KEY = "ml_6471f90f6c06_6tsbiZSudxwNo7GBWGvq3u9ry4kFXiYIkhiThoi0tG0"

@app.post("/api/price")



# 카카오톡 챗봇 스킬 엔드포인트
@app.post("/api/skill")
async def kakao_skill_handler(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # userRequest나 utterance가 없어도 에러가 나지 않도록 처리
    user_request = payload.get("userRequest") or {}
    user_utterance = user_request.get("utterance", "")

    # 조건에 따른 응답 분기
    if "잔영" in user_utterance or "세트" in user_utterance:
        return build_set_price_response()
    else:
        # 단일 아이템 검색 (기본값 예시)
        target_item = (
            user_utterance.strip() if user_utterance else "허상의 마력석"
        )
        return build_item_detail_response(target_item)


async def get_price(request: Request):
    # 1. 카카오톡이 전달한 데이터 확인
    body = await request.json()
    
    # 2. 모비라이프 API 호출 (시세 정보 조회)
    headers = {"Authorization": f"Bearer {MOBILIFE_API_KEY}"}
    response = requests.get("https://api.mobilife.example/v1/market/ticker", headers=headers)
    price_data = response.json()
    
    current_price = price_data.get("price", "정보 없음")

    # 3. 카카오톡 챗봇 전용 JSON 포맷으로 응답 반환
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f" 현재 모비라이프 시세: {current_price}원입니다."
                    }
                }
            ]
        }
    }

