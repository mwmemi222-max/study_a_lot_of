import os
from fastapi import FastAPI, Request
import httpx


app = FastAPI()

MOBILIFE_API_KEY = os.getenv("MOBILIFE_API_KEY", "ml_6471f90f6c06_6tsbiZSudxwNo7GBWGvq3u9ry4kFXiYIkhiThoi0tG0")
BASE_URL = "https://open.mabimobi.life/v1"

def get_headers():
    return {
        "Authorization": f"Bearer {MOBILIFE_API_KEY}",
        "Content-Type": "application/json"
    }

# 입력된 아이템 이름에서 'ZZ' 및 명령어 제거 정리
def clean_item_name(text: str) -> str:
    cleaned = text.replace("/시세", "").replace("ZZ", "").replace("zz", "").strip()
    return cleaned

# 단일 아이템 상세 시세 및 7일 추이 조회
async def fetch_single_item_detail(item_name: str) -> str:
    headers = get_headers()
    target_name = clean_item_name(item_name)
    
    async with httpx.AsyncClient() as client:
        try:
            price_url = f"{BASE_URL}/market/prices"
            price_params = {"search": target_name, "limit": 1, "min_count": 1}
            price_resp = await client.get(price_url, headers=headers, params=price_params)
            
            if price_resp.status_code == 401:
                return "⚠️ API 토큰 인증에 실패했습니다."
            elif price_resp.status_code != 200:
                return f"⚠️ 시세 조회 실패 (코드: {price_resp.status_code})"
                
            price_data = price_resp.json()
            items = price_data.get("items") or price_data.get("data") or []
            if not items:
                return f"🔍 '{target_name}' 아이템의 검색 결과를 찾을 수 없습니다."
            
            target_item = items[0]
            name = target_item.get("name", target_name)
            min_price = target_item.get("min_price", 0)
            count = target_item.get("count", 0)
            pct_24h = target_item.get("pct_change_24h", 0)
            pct_1h = target_item.get("pct_change_1h", 0)
            kind_id = target_item.get("kind_id") or target_item.get("id")

            history_text = ""
            if kind_id:
                history_url = f"{BASE_URL}/market/prices/history"
                history_params = {"kind_id": kind_id, "days": 7}
                history_resp = await client.get(history_url, headers=headers, params=history_params)
                
                if history_resp.status_code == 200:
                    h_data = history_resp.json()
                    h_list = h_data.get("history") or h_data.get("data") or []
                    if h_list:
                        latest = h_list[-1]
                        high_price = latest.get("high_price", 0) or latest.get("high", 0)
                        low_price = latest.get("low_price", 0) or latest.get("low", 0)
                        if high_price or low_price:
                            history_text = f"\n\n📊 최근 7일 시세 추이:\n- 최고가: {high_price:,} 골드\n- 최저가: {low_price:,} 골드"

            return (
                f"🔍 [{name} 실시간 시세]\n\n"
                f"💰 현재 최저가: {min_price:,} 골드\n"
                f"📦 등록 수량: {count:,}개\n\n"
                f"📈 가격 변동률:\n"
                f"- 1시간 전 대비: {pct_1h:+.1f}%\n"
                f"- 24시간 전 대비: {pct_24h:+.1f}%"
                f"{history_text}\n\n"
                f"Data based on 모비라이프 OpenAPI"
            )
        except Exception:
            return "⚠️ 서버 통신 중 오류가 발생했습니다."

# 그룹 아이템 최저가 목록 조회
async def fetch_group_item_summary(group_title: str, item_list: list) -> str:
    headers = get_headers()
    summary_results = []
    
    async with httpx.AsyncClient() as client:
        for item_name in item_list:
            try:
                price_url = f"{BASE_URL}/market/prices"
                price_params = {"search": item_name, "limit": 1}
                resp = await client.get(price_url, headers=headers, params=price_params)
                
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items") or data.get("data") or []
                    if items:
                        target = items[0]
                        min_price = target.get("min_price", 0)
                        count = target.get("count", 0)
                        summary_results.append(f"• {item_name}: {min_price:,} 골드 ({count:,}개)")
                    else:
                        summary_results.append(f"• {item_name}: 정보 없음")
                else:
                    summary_results.append(f"• {item_name}: 조회 실패")
            except Exception:
                summary_results.append(f"• {item_name}: 통신 오류")

    lines = "\n".join(summary_results)
    return (
        f"⚔️ [{group_title} 실시간 최저가 현황]\n\n"
        f"{lines}\n\n"
        f"💡 아이템 풀네임 입력 시(ZZ 제외) 7일 시세 추이를 확인할 수 있습니다!\n"
        f"Data based on 모비라이프 OpenAPI"
    )

@app.post("/api/skill")
async def kakao_skill(request: Request):
    payload = await request.json()
    raw_utterance = payload.get("userRequest", {}).get("utterance", "").strip()
    utterance = clean_item_name(raw_utterance)

    # 1. 영혼석 & 마력석
    soul_stones = ["야생의 영혼석", "삼림의 영혼석", "공명의 영혼석", "파동의 영혼석", "망령의 영혼석", "원념의 영혼석"]
    magic_stones = ["허상의 마력석", "포식의 마력석", "심해의 마력석"]
    
    # 2. 잔영 시리즈
    remnant_weapons = [
        "잔영의 숏소드", "잔영의 숏보우", "잔영의 우드 완드", "잔영의 마블 힐링 완드", "잔영의 플랫대거",
        "잔영의 켈틱 류트", "잔영의 크리스탈 스태프", "잔영의 그레이드 소드", "잔영의 라이트 롱보우",
        "잔영의 스노우 오브", "잔영의 듀얼소드", "잔영의 라우드헤드 케인", "잔영의 라운드 코일",
        "잔영의 서펜트 의식용 단검", "잔영의 블런트 쿼터스태프", "잔영의 론 엣지소드", "잔영의 크로스보우",
        "잔영의 꽃잎 접부채", "잔영의 커브드 하프", "잔영의 라이트 너클", "잔영의 라이트 핼버드"
    ]
    remnant_armors = [
        "잔영의 비늘 갑옷 투구", "잔영의 비늘 갑옷 상의", "잔영의 비늘 갑옷 장갑", "잔영의 비늘 갑옷 하의", "잔영의 비늘 갑옷 신발",
        "잔영의 가죽 갑옷 투구", "잔영의 가죽 갑옷 상의", "잔영의 가죽 갑옷 장갑", "잔영의 가죽 갑옷 하의", "잔영의 가죽 갑옷 신발",
        "잔영의 전투복 투구", "잔영의 전투복 상의", "잔영의 전투복 장갑", "잔영의 전투복 하의", "잔영의 전투복 신발"
    ]
    remnant_accs = ["잔영의 페리도트 링", "잔영의 페리도트 네크리스"]

    # 3. 해연 시리즈
    abyssal_weapons = [
        "해연의 숏소드", "해연의 숏보우", "해연의 우드 완드", "해연의 마블 힐링 완드", "해연의 플랫대거",
        "해연의 켈틱 류트", "해연의 크리스탈 스태프", "해연의 그레이드 소드", "해연의 라이트 롱보우",
        "해연의 스노우 오브", "해연의 듀얼소드", "해연의 라우드헤드 케인", "해연의 라운드 코일",
        "해연의 서펜트 의식용 단검", "해연의 블런트 쿼터스태프", "해연의 론 엣지소드", "해연의 크로스보우",
        "해연의 꽃잎 접부채", "해연의 커브드 하프", "해연의 라이트 너클", "해연의 라이트 핼버드"
    ]
    abyssal_armors = [
        "해연의 비늘 갑옷 투구", "해연의 비늘 갑옷 상의", "해연의 비늘 갑옷 장갑", "해연의 비늘 갑옷 하의", "해연의 비늘 갑옷 신발",
        "해연의 가죽 갑옷 투구", "해연의 가죽 갑옷 상의", "해연의 가죽 갑옷 장갑", "해연의 가죽 갑옷 하의", "해연의 가죽 갑옷 신발",
        "해연의 전투복 투구", "해연의 전투복 상의", "해연의 전투복 장갑", "해연의 전투복 하의", "해연의 전투복 신발"
    ]
    abyssal_accs = ["해연의 페리도트 링", "해연의 페리도트 네크리스"]

    # 키워드 처리 분기
    if utterance in ["잔영 무기", "잔영무기"]:
        reply_text = await fetch_group_item_summary("잔영 무기 시리즈", remnant_weapons)
    elif utterance in ["잔영 방어", "잔영방어"]:
        reply_text = await fetch_group_item_summary("잔영 방어구 시리즈", remnant_armors)
    elif utterance in ["잔영 악세", "잔영악세", "해연 악세", "해연악세"]:
        # 해연 악세 검색 요청 시 해연 악세 목록 출력 (기존 잔영 악세 교체/통합)
        reply_text = await fetch_group_item_summary("해연/잔영 악세서리 시리즈", list(set(remnant_accs + abyssal_accs)))
    elif utterance in ["해연 무기", "해연무기"]:
        reply_text = await fetch_group_item_summary("해연 무기 시리즈", abyssal_weapons)
    elif utterance in ["해연 방어", "해연방어"]:
        reply_text = await fetch_group_item_summary("해연 방어구 시리즈", abyssal_armors)
        
    # 해연 부위별 검색 (투구, 상의, 장갑, 하의, 신발)
    elif utterance in ["해연 투구", "해연투구"]:
        items = ["해연의 비늘 갑옷 투구", "해연의 가죽 갑옷 투구", "해연의 전투복 투구"]
        reply_text = await fetch_group_item_summary("해연 투구 3종", items)
    elif utterance in ["해연 상의", "해연상의"]:
        items = ["해연의 비늘 갑옷 상의", "해연의 가죽 갑옷 상의", "해연의 전투복 상의"]
        reply_text = await fetch_group_item_summary("해연 상의 3종", items)
    elif utterance in ["해연 장갑", "해연장갑"]:
        items = ["해연의 비늘 갑옷 장갑", "해연의 가죽 갑옷 장갑", "해연의 전투복 장갑"]
        reply_text = await fetch_group_item_summary("해연 장갑 3종", items)
    elif utterance in ["해연 하의", "해연하의"]:
        items = ["해연의 비늘 갑옷 하의", "해연의 가죽 갑옷 하의", "해연의 전투복 하의"]
        reply_text = await fetch_group_item_summary("해연 하의 3종", items)
    elif utterance in ["해연 신발", "해연신발"]:
        items = ["해연의 비늘 갑옷 신발", "해연의 가죽 갑옷 신발", "해연의 전투복 신발"]
        reply_text = await fetch_group_item_summary("해연 신발 3종", items)

    # 기본 키워드 검색
    elif utterance in ["영혼석"]:
        reply_text = await fetch_group_item_summary("영혼석 시리즈", soul_stones)
    elif utterance in ["마력석"]:
        reply_text = await fetch_group_item_summary("마력석 시리즈", magic_stones)
    elif utterance in ["용비늘"]:
        reply_text = await fetch_single_item_detail("마력 깃든 용비늘")
    else:
        # 풀네임 검색 (ZZ가 입력되더라도 내부에서 자동 제거)
        reply_text = await fetch_single_item_detail(utterance)

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
