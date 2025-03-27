import os

from cozepy import (
    COZE_CN_BASE_URL,
    ChatEventType,
    Coze,
    Message,
    MessageType,
    TokenAuth,
)
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


COZE_API_TOKEN = os.getenv("COZE_API_TOKEN")
BOT_ID = os.getenv("BOT_ID")
USER_ID = "user id"

# Initialize Coze client
coze = Coze(auth=TokenAuth(token=COZE_API_TOKEN), base_url=COZE_CN_BASE_URL)


def chat_stream(msg: str, bot_id:str, user_id:str = 'user id',
        conversation_id: str | None = None):
    """
    Initiates chat. The response method is streaming.
    if there's not need to distinguish the context of the conversation(just a question and answer),
    skip the param of conversation_id
    Yields:
        tuple: A tuple containing the type of content and the content itself.
               The type can be "reasoning_start", "reasoning", "reasoning_end", "content", or "usage".
    """
    in_reasoning_block = False

    for event in coze.chat.stream(
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


def chat_no_stream(msg: str, bot_id:str, user_id:str = 'user id',
        conversation_id: str | None = None):
    """
    initiate a chat, The response method is non-streaming.
    if there's not need to distinguish the context of the conversation(just a question and answer),
    skip the param of conversation_id
    """
    chat_poll = coze.chat.create_and_poll(
        bot_id=bot_id,
        user_id=user_id,
        conversation_id=conversation_id,
        additional_messages=[Message.build_user_question_text(msg)],
    )
    for message in chat_poll.messages:
        if message.type == MessageType.ANSWER:
            return message.content





if __name__ == '__main__':
    # for c_type, content in chat_stream("hello, what's your name?", '7485226919554859018'):
    #     if c_type == "content":
    #         print(content, end='', flush=True)
    res = chat_no_stream("What's your name?", BOT_ID)
    print(res)



