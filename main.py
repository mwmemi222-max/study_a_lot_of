import os
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

# Render 환경변수에서 불러오거나 직접 입력 (Bearer 토큰)
MOBILIFE_API_KEY = os.getenv("ml_6471f90f6c06_6tsbiZSudxwNo7GBWGvq3u9ry4kFXiYIkhiThoi0tG0")
BASE_URL = "https://open.mabimobi.life/v1"

def get_headers():
    return {
        "Authorization": f"Bearer {MOBILIFE_API_KEY}",
        "Content-Type": "json"
    }

async def fetch_item_info(item_name: str) -> str:
    headers = get_headers()
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. 거래소 시세 조회 API 호출
            price_url = f"{BASE_URL}/market/prices"
            price_params = {
                "search": item_name,
                "limit": 1,
                "min_count": 1
            }
            
            price_resp = await client.get(price_url, headers=headers, params=price_params)
            
            if price_resp.status_code == 401:
                return "⚠️ API 토큰 인증에 실패했습니다. 키를 확인해 주세요."
            elif price_resp.status_code != 200:
                return f"⚠️ 시세 조회 실패 (에러 코드: {price_resp.status_code})"
                
            price_data = price_resp.json()
            
            # API 응답 구조에 맞춰 아이템 목록 가져오기 (items 또는 data)
            items = price_data.get("items") or price_data.get("data") or []
            if not items:
                return f"🔍 '{item_name}' 아이템의 검색 결과를 찾을 수 없습니다."
            
            target_item = items[0]
            name = target_item.get("name", item_name)
            min_price = target_item.get("min_price", 0)
            count = target_item.get("count", 0)
            pct_24h = target_item.get("pct_change_24h", 0)
            pct_1h = target_item.get("pct_change_1h", 0)
            kind_id = target_item.get("kind_id") or target_item.get("id")

            # 2. 시세 이력(가격 추이) 조회 API 호출 (kind_id가 있는 경우)
            history_text = ""
            if kind_id:
                history_url = f"{BASE_URL}/market/prices/history"
                history_params = {
                    "kind_id": kind_id,
                    "days": 7
                }
                history_resp = await client.get(history_url, headers=headers, params=history_params)
                
                if history_resp.status_code == 200:
                    h_data = history_resp.json()
                    h_list = h_data.get("history") or h_data.get("data") or []
                    if h_list:
                        # 가장 최근 이력 가져오기
                        latest = h_list[-1]
                        high_price = latest.get("high_price", 0) or latest.get("high", 0)
                        low_price = latest.get("low_price", 0) or latest.get("low", 0)
                        
                        if high_price or low_price:
                            history_text = f"\n\n📊 최근 시세 추이:\n- 최고가: {high_price:,} 골드\n- 최저가: {low_price:,} 골드"

            # 최종 카카오톡 출력 메시지 구성
            response_text = (
                f"🔍 [{name} 실시간 시세 정보]\n\n"
                f"💰 현재 최저가: {min_price:,} 골드\n"
                f"📦 등록 수량: {count:,}개\n\n"
                f"📈 가격 변동률:\n"
                f"- 1시간 전 대비: {pct_1h:+.1f}%\n"
                f"- 24시간 전 대비: {pct_24h:+.1f}%"
                f"{history_text}\n\n"
                f"Data based on 모비라이프 OpenAPI"
            )
            return response_text

        except Exception as e:
            return "⚠️ 시세 정보를 불러오는 중 서버 통신 오류가 발생했습니다."

@app.post("/api/skill")
async def kakao_skill(request: Request):
    payload = await request.json()
    utterance = payload.get("userRequest", {}).get("utterance", "").strip()
    
    # 키워드 매핑 및 명령어 파싱
    target_item = ""
    if "마력석" in utterance:
        target_item = "허상의 마력석"
    elif "잔영" in utterance:
        target_item = "잔영"
    elif "해연" in utterance:
        target_item = "해연"
    elif "영혼석" in utterance:
        target_item = "영혼석"
    else:
        # /시세 [아이템명] 으로 쳤을 때 파싱
        clean_text = utterance.replace("/시세", "").strip()
        target_item = clean_text if clean_text else "허상의 마력석"

    reply_text = await fetch_item_info(target_item)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": reply_text
                    }
                }
            ]
        }
    }
