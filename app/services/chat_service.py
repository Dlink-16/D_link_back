import json
import os
import random
from pathlib import Path
from openai import AsyncOpenAI
from app.schemas.chat import ChatRequest, ChatResponse
from dotenv import load_dotenv

load_dotenv()

# OpenAI 클라이언트 초기화 (API Key는 환경변수에서 로드)
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

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

    # 2. 필터링된 결과 중에서 무작위로(랜덤) 최대 15개 추출
    sample_size = min(15, len(items))
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
        
    return result_text

async def generate_chat_response(request: ChatRequest) -> ChatResponse:
    # API 키가 설정되지 않은 경우
    if not client.api_key:
        return ChatResponse(
            reply="[알림] OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    # 사용자 질문에 맞춰 필요한 데이터 추출
    filtered_info = filter_data(request.message)
    
    system_prompt = f"""
당신은 대전-충청권 지역 정보를 안내하는 친절한 AI 어시스턴트입니다.
사용자에게 제공된 아래 [제공된 지역 데이터]를 바탕으로 추천 및 안내를 진행해주세요.
데이터에 없는 내용이라면 "제공된 데이터에서 관련 정보를 찾을 수 없습니다"라고 정중하게 안내하세요.

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
        return ChatResponse(reply=reply_content)
    except Exception as e:
        return ChatResponse(reply=f"죄송합니다. 오류가 발생했습니다: {str(e)}")
