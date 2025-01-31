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
        return message.content

# conversation = coze.conversations.create()
# msg1 = Message.build_user_question_text("self.user_prompt : '添加一个课程：CNO: 11110140, Name: 大数据存储与管理, Credit: 3, Dept: 人工智能学院'")

# msg2 = Message.build_user_question_text("Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyb290IiwiZXhwIjoxNzM4MjA0Mjc1fQ.MiP72x8KLu-M10hI16UrSFIkfggcltrjWwh6UV0c8lw")
# msg3 = Message.build_user_question_text("409{\"detail\":\"Course with cno '11110140' already exists.\"}")
# send_msg(conversation.id, msg1)
# send_msg(conversation.id, msg2)
# send_msg(conversation.id, msg3)


import requests
from typing import Dict, Any

debug = True
def execute_api_call(use_https: bool, domain: str, api_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行API调用，并返回响应结果。

    :param use_https: 是否使用 HTTPS
    :param domain: API 服务器的域名（不包含协议前缀）
    :param api_call: API 调用格式，包含 path、method、query_args、path_args、data_args、headers 等字段
    :return: 包含响应状态码、响应头和响应数据的字典
    """
    # 构建 URL
    if debug:
        print(f"WebClient exec http call: {api_call}")
    protocol = "https" if use_https else "http"
    path = api_call["path"]
    method = api_call["method"].upper()
    query_args = api_call.get("query_args", {})
    path_args = api_call.get("path_args", {})
    data_args = api_call.get("data_args", {})
    headers = api_call.get("headers", {})

    # 替换路径参数
    formatted_path = path.format(**path_args)
    full_url = f"{protocol}://{domain}{formatted_path}"

    # 处理请求体格式
    request_kwargs = {
        "method": method,
        "url": full_url,
        "params": query_args,
        "headers": headers,
    }

    # 处理请求体
    if method in ["POST", "PUT", "PATCH"]:
        if headers.get("Content-Type") == "application/x-www-form-urlencoded":
            request_kwargs["data"] = data_args  # 适用于表单数据
        else:
            request_kwargs["json"] = data_args  # 默认 JSON 方式

    # 发送请求
    try:
        if debug:
            print(f"WebClient sending request: {request_kwargs}")
        response = requests.request(**request_kwargs)

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.json() if response.content else None
        }
    except requests.exceptions.RequestException as e:
        return {
            "status_code": None,
            "headers": {},
            "data": {"error": str(e)}
        }

import json

msg1 = Message.build_user_question_text("user_prompt: \
    先获取一个token，by (auth user: root, auth password: abc，添加application/x-www-form-urlencoded header)。\
    然后以后的每次请求都需要在header中加入Authorization: Bearer <token>。\
    然后添加一个课程：CNO: test11, Name: 大数据存储与管理, Credit: 3, Dept: 人工智能学院")

conversation = coze.conversations.create()

# msg2 = Message.build_user_question_text("Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyb290IiwiZXhwIjoxNzM4MjA0Mjc1fQ.MiP72x8KLu-M10hI16UrSFIkfggcltrjWwh6UV0c8lw")
# msg3 = Message.build_user_question_text("409{\"detail\":\"Course with cno '11110140' already exists.\"}")
# send_msg(conversation.id, msg1)
# send_msg(conversation.id, msg2)
# send_msg(conversation.id, msg3)


conversation_id = conversation.id
msg = msg1
for _ in range(5):
    print("sending msg: ", msg)
    res = send_msg(conversation_id, msg)
    res_dict = json.loads(res)
    if res_dict['status'] != 'in_progress':
        print("end of conversation: ", res_dict)
        break
    print(f"webClient response: {res_dict}")
    call_res = execute_api_call(False, '127.0.0.1:8000', res_dict['api_calls'][0])
    msg = Message.build_user_question_text(json.dumps(call_res))


