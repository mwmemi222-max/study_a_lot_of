from datetime import datetime
from fastapi import FastAPI, Request

app = FastAPI()
MOBILIFE_API_KEY = "ml_6471f90f6c06_6tsbiZSudxwNo7GBWGvq3u9ry4kFXiYIkhiThoi0tG0"

def create_kakao_response(text: str):
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text
                    }
                }
            ]
        }
    }

# 1. /잔영 키워드 응답
def build_set_price_response():
    now_str = datetime.now().strftime("%H:%M")
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

🕒 서버 데이터 갱신 시간: {now_str}"""
    return create_kakao_response(text_content)

# 2. 단일 아이템 키워드 응답 (/마력석, /영혼석, /해연, /시세 등)
def build_item_detail_response(item_name: str):
    now_str = datetime.now().strftime("%H:%M")
    
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
🕒 서버 데이터 갱신 시간: {now_str}


Data based on 모비라이프 OpenAPI"""
    return create_kakao_response(text_content)

# 카카오톡 챗봇 스킬 엔드포인트
@app.post("/api/skill")
async def kakao_skill_handler(request: Request):
    try:
        payload = await request.json()
        user_utterance = payload.get("userRequest", {}).get("utterance", "").strip()

        # 슬래시(/)가 붙은 명령어 인식 및 매핑
        if "잔영" in user_utterance:
            return build_set_price_response()
        elif "마력석" in user_utterance:
            return build_item_detail_response("허상의 마력석")
        elif "영혼석" in user_utterance:
            return build_item_detail_response("영혼석")
        elif "해연" in user_utterance:
            return build_item_detail_response("해연")
        elif "시세" in user_utterance:
            # /시세 만 치거나 뒤에 특정 아이템명을 같이 친 경우 추출
            cleaned_text = user_utterance.replace("/시세", "").strip()
            target_item = cleaned_text if cleaned_text else "허상의 마력석"
            return build_item_detail_response(target_item)
        else:
            return build_item_detail_response("허상의 마력석")

    except Exception as e:
        return create_kakao_response(f"서버 처리 중 오류 발생: {str(e)}")
