import os
from openai import AsyncOpenAI
from app.schemas.chat import ChatRequest, ChatResponse
from dotenv import load_dotenv

load_dotenv()

# OpenAI 클라이언트 초기화 (API Key는 환경변수에서 로드)
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

async def generate_chat_response(request: ChatRequest) -> ChatResponse:
    # API 키가 설정되지 않은 경우
    if not client.api_key:
        return ChatResponse(
            reply="[알림] OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    # 대화 히스토리 구성
    messages = []
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})

    try:
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
        )
        reply_content = response.choices[0].message.content
        return ChatResponse(reply=reply_content)
    except Exception as e:
        return ChatResponse(reply=f"죄송합니다. 오류가 발생했습니다: {str(e)}")
