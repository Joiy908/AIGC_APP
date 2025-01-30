import os
import time

from cozepy import (
    COZE_CN_BASE_URL,
    Coze,
    TokenAuth,
    Message,
    ChatStatus,
    MessageContentType
)

# Retrieve API token from environment variables
coze_api_token = os.getenv("COZE_API_TOKEN")
coze_api_base = COZE_CN_BASE_URL

# Initialize Coze client
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Define bot and user IDs
bot_id = "7402079039265226789"
user_id = "user id"

# Create a chat session
chat = coze.chat.create(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[
        Message.build_user_question_text("QPS 5w, 容量: 1G"),
    ],
)

# Polling for chat completion
start = int(time.time())
timeout = 600  # Timeout in seconds

while chat.status == ChatStatus.IN_PROGRESS:
    if int(time.time()) - start > timeout:
        # Cancel chat if it takes too long
        coze.chat.cancel(conversation_id=chat.conversation_id, chat_id=chat.id)
        break

    time.sleep(1)
    # Retrieve latest chat status
    chat = coze.chat.retrieve(conversation_id=chat.conversation_id, chat_id=chat.id)

# Retrieve and print messages when chat is completed
messages = coze.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.id)
for message in messages:
    print(f"role={message.role}, content={message.content}")
    break

# Alternative approach using `create_and_poll` for simplification
# chat_poll = coze.chat.create_and_poll(
#     bot_id=bot_id,
#     user_id=user_id,
#     additional_messages=[
#         Message.build_user_question_text("QPS 5w, 容量: 1G"),
#     ],
# )
# for message in chat_poll.messages:
#     print(message.content)
#     break

# if chat_poll.chat.status == ChatStatus.COMPLETED:
#     print("\nToken usage:", chat_poll.chat.usage.token_count)
