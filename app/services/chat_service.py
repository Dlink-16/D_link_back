import json
import os
import random
from pathlib import Path
from openai import AsyncOpenAI
from app.schemas.chat import ChatRequest, ChatResponse
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 최상위의 data 폴더 경로 지정
DATA_DIR = Path(__file__).parent.parent.parent / "data"

def load_all_regional_data() -> dict:
    """서버 시작 시 data 폴더의 주요 JSON 데이터를 카테고리별로 로드하여 메모리에 저장"""
    loaded_data = {}
    if not DATA_DIR.exists():
        print(f"데이터 폴더를 찾을 수 없습니다: {DATA_DIR}")
        return loaded_data
        
    for file_path in DATA_DIR.glob("대전_충청권_*.json"):
        # 파일명에서 카테고리 추출 (예: 대전_충청권_관광지.json -> 관광지)
        category = file_path.stem.split("_")[-1]
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 데이터 형식이 리스트인지 딕셔너리인지 확인하여 아이템 추출
                items = data if isinstance(data, list) else data.get("items", [])
                loaded_data[category] = items
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
            
    print(f"[OK] 지역 데이터 로드 완료. 카테고리: {list(loaded_data.keys())}")
    return loaded_data

# 딕셔너리 형태로 모든 데이터를 메모리에 로드
REGIONAL_DATA = load_all_regional_data()

def filter_data(message: str) -> str:
    """사용자의 질문에서 키워드를 파악하여 관련 카테고리 데이터를 랜덤하게 최대 15개 추출"""
    # 1. 키워드 매핑
    keywords_mapping = {
        # 관광지
        "관광": "관광지", "명소": "관광지", "볼거리": "관광지", "여행지": "관광지", "구경": "관광지",
        # 음식점
        "맛집": "음식점", "식당": "음식점", "음식": "음식점", "먹을": "음식점", "밥": "음식점", "카페": "음식점",
        # 쇼핑
        "쇼핑": "쇼핑", "시장": "쇼핑", "마트": "쇼핑", "백화점": "쇼핑", "살곳": "쇼핑",
        # 문화시설
        "문화": "문화시설", "미술관": "문화시설", "박물관": "문화시설", "도서관": "문화시설", "전시": "문화시설",
        # 레포츠
        "레포츠": "레포츠", "액티비티": "레포츠", "운동": "레포츠", "체험": "레포츠", "놀거리": "레포츠",
        # 숙박
        "숙소": "숙박", "호텔": "숙박", "모텔": "숙박", "펜션": "숙박", "숙박": "숙박", "잠": "숙박",
        # 여행코스
        "코스": "여행코스", "루트": "여행코스", "일정": "여행코스", "동선": "여행코스",
        # 축제공연행사
        "축제": "축제공연행사", "행사": "축제공연행사", "공연": "축제공연행사", "이벤트": "축제공연행사", "페스티벌": "축제공연행사"
    }
    
    selected_category = None
    for keyword, category in keywords_mapping.items():
        if keyword in message:
            selected_category = category
            break
            
    # 키워드가 없으면 기본값으로 관광지 선택
    if not selected_category:
        selected_category = "관광지"
        
    items = REGIONAL_DATA.get(selected_category, [])
    
    if not items:
        return "해당 카테고리의 데이터가 없습니다."

    # 2. 지역 키워드 필터링 추가
    # 대전 및 충청권 주요 지역 키워드
    location_keywords = [
        "유성구", "서구", "중구", "동구", "대덕구", "둔산동", "은행동", "봉명동", "도안동", "궁동", "탄방동", "월평동", "관평동",
        "세종", "청주", "천안", "공주", "보령", "아산", "서산", "논산", "계룡", "당진", "금산", "부여", "서천", "청양", "홍성", "예산", "태안"
    ]
    
    # 사용자의 질문에 지역 키워드가 포함되어 있는지 확인
    matched_locations = [loc for loc in location_keywords if loc in message]
    
    if matched_locations:
        # 질문에 지역 키워드가 있다면 해당 지역이 주소(addr1)에 포함된 장소만 필터링
        filtered_items = []
        for item in items:
            addr = item.get("addr1", "") or ""
            # 매칭된 지역 키워드 중 하나라도 주소에 포함되어 있으면 추가
            if any(loc in addr for loc in matched_locations):
                filtered_items.append(item)
                
        items = filtered_items
        
        # 만약 필터링 후 데이터가 없다면, AI에게 이 사실을 그대로 알려주기 위해 문자열 반환
        if not items:
            return f"사용자가 요청한 지역({', '.join(matched_locations)})에 해당하는 {selected_category} 데이터가 존재하지 않습니다."

    # 3. 필터링된 결과 중에서 무작위로(랜덤) 최대 4개 추출
    sample_size = min(4, len(items))
    selected_items = random.sample(items, sample_size)
    
    # 3. OpenAI에게 넘겨줄 텍스트로 가공
    result_text = f"[{selected_category} 정보]\n"
        
    for item in selected_items:
        title = item.get("title", "")
        addr = item.get("addr1", "")
        tel = item.get("tel", "번호 없음")
        if not tel or not tel.strip():
            tel = "번호 없음"
        result_text += f"- 이름: {title}, 주소: {addr}, 전화번호: {tel}\n"
        
    return result_text, selected_items

async def generate_chat_response(request: ChatRequest) -> ChatResponse:
    # API 키가 설정되지 않은 경우
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return ChatResponse(
            reply="[알림] OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    client = AsyncOpenAI(api_key=api_key)

    # 사용자 질문에 맞춰 필요한 데이터 추출
    filtered_info, selected_items = filter_data(request.message)
    
    system_prompt = f"""
당신은 대전-충청권 지역 정보를 안내하는 친절한 AI 어시스턴트입니다.
사용자에게 제공된 아래 [제공된 지역 데이터]를 바탕으로 추천해 주세요.

[답변 작성 규칙]
1. 데이터가 많더라도 모두 나열하지 말고, 가장 어울리는 3~4곳만 엄선하여 추천해 주세요.
2. 각 장소는 글머리 기호(-)를 사용하여 '이름'과 '주소'를 보기 편하게 정리해 주세요.
3. 전화번호나 영업시간 등 데이터에 없는 정보에 대해 굳이 변명하거나 언급하지 마세요. 주어진 정보만 자연스럽게 제공하세요.
4. 친절하고 간결한 말투를 사용하며, 대화의 마지막에는 "더 원하시는 조건(특정 동네, 메뉴 등)이 있다면 말씀해 주세요!"와 같이 가볍게 마무리하세요.

[제공된 지역 데이터]
{filtered_info}
"""

    # 대화 히스토리 구성
    messages = [{"role": "system", "content": system_prompt}]
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})

    try:
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )
        reply_content = response.choices[0].message.content
        
        # 프론트엔드 지도 표시용 좌표 데이터 추출
        locations = []
        for item in selected_items:
            title = item.get("title", item.get("REST_NM", "이름 없음"))
            addr1 = item.get("addr1", item.get("ADDR", "주소 없음"))
            
            # API 데이터 소스(TourAPI 또는 자체 맛집DB)에 따라 키가 다름
            lat = item.get("mapy", item.get("LAT"))
            lng = item.get("mapx", item.get("LOT"))
            
            # None 또는 빈 문자열 체크 후 float 변환
            try:
                lat = float(lat) if lat else None
                lng = float(lng) if lng else None
            except ValueError:
                lat, lng = None, None
                
            if lat and lng:
                locations.append({
                    "name": title,
                    "address": addr1,
                    "lat": lat,
                    "lng": lng
                })
        
        return ChatResponse(reply=reply_content, locations=locations)
    except Exception as e:
        return ChatResponse(reply=f"죄송합니다. 오류가 발생했습니다: {str(e)}")
