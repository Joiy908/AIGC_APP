import logging
import os

from cozepy import COZE_CN_BASE_URL, AsyncCoze, AsyncTokenAuth, ChatEventType, ChatStatus, Message, MessageType
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()  # take environment variables from .env.


COZE_API_TOKEN = os.getenv("COZE_API_TOKEN")
BOT_ID = os.getenv("BOT_ID")
USER_ID = "user id"

# Initialize Coze client
acoze = AsyncCoze(auth=AsyncTokenAuth(token=COZE_API_TOKEN), base_url=COZE_CN_BASE_URL)


async def achat_stream(msg: str, bot_id: str, user_id: str = "user id", conversation_id: str | None = None):
    """
    Initiates chat. The response method is streaming.
    if there's not need to distinguish the context of the conversation(just a question and answer),
    skip the param of conversation_id
    Yields:
        tuple: A tuple containing the type of content and the content itself.
               The type can be "reasoning_start", "reasoning", "reasoning_end", "content", or "usage".
    """
    in_reasoning_block = False

    async for event in acoze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        conversation_id=conversation_id,
        additional_messages=[Message.build_user_question_text(msg)],
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            if event.message.reasoning_content:
                if not in_reasoning_block:
                    yield ("reasoning_start", "----- reasoning_content start -----")
                    in_reasoning_block = True
                yield ("reasoning", event.message.reasoning_content)
            else:
                # 如果之前在 reasoning 块中，结束该块
                if in_reasoning_block:
                    yield ("reasoning_end", "----- reasoning_content end -----")
                    in_reasoning_block = False
                yield ("content", event.message.content)
        elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
            # 确保在聊天完成时关闭 reasoning 块（如果未关闭）
            if in_reasoning_block:
                yield ("reasoning_end", "----- reasoning_content end -----")
            yield ("usage", f"Token usage: {event.chat.usage.token_count}")
            logger.debug(f"Token usage: {event.chat.usage.token_count}")


async def main():
    async for c_type, content in achat_stream("hello, what's your name?", "7485226919554859018"):
        if c_type == "content":
            print(content, end="", flush=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
