import json
import os
from pathlib import Path
from openai import AsyncOpenAI
from app.schemas.chat import ChatRequest, ChatResponse
from dotenv import load_dotenv

load_dotenv()

# OpenAI 클라이언트 초기화 (API Key는 환경변수에서 로드)
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# JSON 데이터 로드
DATA_PATH = Path(__file__).parent.parent / "data" / "regional_data.json"

def load_regional_data() -> str:
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error loading regional data: {e}")
        return "{}"

REGIONAL_DATA_STR = load_regional_data()

SYSTEM_PROMPT = f"""
당신은 지역 정보를 안내하는 친절한 어시스턴트입니다.
사용자에게 제공된 아래 JSON 데이터를 바탕으로 정확하고 상세하게 답변해야 합니다.
데이터에 없는 내용이라면 "제공된 데이터에서 관련 정보를 찾을 수 없습니다"라고 정중하게 안내하세요.
주요 질의 유형(권역별 관광지 추천, 축제 일정, 모범음식점 위치, 커뮤니티 게시글 검색)을 처리할 수 있어야 합니다.

[제공된 지역 데이터]
{REGIONAL_DATA_STR}
"""

async def generate_chat_response(request: ChatRequest) -> ChatResponse:
    # API 키가 설정되지 않은 경우 모의 응답 반환
    if not client.api_key:
        return ChatResponse(
            reply="[알림] OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.\n\n사용자 메시지: " + request.message
        )

    # 대화 히스토리 구성
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 이전 대화 내역 추가
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})
        
    # 현재 질문 추가
    messages.append({"role": "user", "content": request.message})
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", # 또는 gpt-4o 등 사용 가능한 모델
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        reply_content = response.choices[0].message.content
        return ChatResponse(reply=reply_content)
    except Exception as e:
        return ChatResponse(reply=f"죄송합니다. 오류가 발생했습니다: {str(e)}")
