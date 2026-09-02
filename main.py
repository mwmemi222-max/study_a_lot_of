from fastapi import FastAPI, Request
import requests

app = FastAPI()

MOBILIFE_API_KEY = "ml_6471f90f6c06_6tsbiZSudxwNo7GBWGvq3u9ry4kFXiYIkhiThoi0tG0"

@app.post("/api/price")
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

