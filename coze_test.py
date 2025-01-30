import os
import time

from cozepy import (
    COZE_CN_BASE_URL,
    Coze,
    TokenAuth,
    Message,
    MessageRole,
    ChatStatus,
    MessageContentType
)

# Retrieve API token from environment variables
coze_api_token = os.getenv("COZE_API_TOKEN")
coze_api_base = COZE_CN_BASE_URL

# Initialize Coze client
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Define bot and user IDs
bot_id = "7465179263470321698"
user_id = "user id"


def send_msg(conversation_id, msg):
    chat_poll = coze.chat.create_and_poll(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            msg
        ],
        conversation_id=conversation_id
    )
    for message in chat_poll.messages:
        print(message.content)
        break

conversation = coze.conversations.create()
msg1 = Message.build_user_question_text("self.user_prompt : '添加一个课程：CNO: 11110140, Name: 大数据存储与管理, Credit: 3, Dept: 人工智能学院'")

msg2 = Message.build_user_question_text("Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyb290IiwiZXhwIjoxNzM4MjA0Mjc1fQ.MiP72x8KLu-M10hI16UrSFIkfggcltrjWwh6UV0c8lw")
msg3 = Message.build_user_question_text("409{\"detail\":\"Course with cno '11110140' already exists.\"}")
send_msg(conversation.id, msg1)
send_msg(conversation.id, msg2)
send_msg(conversation.id, msg3)

