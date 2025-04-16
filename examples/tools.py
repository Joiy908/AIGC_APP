import json
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from cozepy import Message

from .coze_llm import (
    BOT_ID,
    USER_ID,
    chat_no_stream,
    coze,
)


def get_now_local_datetime() -> str:
    return (datetime.now(tz=timezone.utc) + timedelta(hours=8)).isoformat()[:-6] + "+08:00"


def execute_api_call(use_https: bool, domain: str, api_call: dict[str, Any], vorbose: bool) -> dict[str, any]:
    """
    执行API调用，并返回响应结果。

    :param use_https: 是否使用 HTTPS
    :param domain: API 服务器的域名（不包含协议前缀）
    :param api_call: API 调用格式，包含 path、method、query_args、path_args、data_args、headers 等字段
    :return: 包含响应状态码、响应头和响应数据的字典

    下面是可以调用的api:
    http://localhost:8000
    {
        "openapi": "3.1.0",
        "info": {
            "title": "FastAPI",
            "version": "0.1.0"
        },
        "paths": {
            "/api/v1/sensors/values": {
                "get": {
                    "summary": "Get All Sensor Values",
                    "operationId": "get_all_sensor_values_api_v1_sensors_values_get",
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/records": {
                "post": {
                    "summary": "Create Record",
                    "operationId": "create_record_api_v1_records_post",
                    "requestBody": {
                        "required": true,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Record"
                                }
                            }
                        }
                    },
                },
                "get": {
                    "summary": "Get Records",
                    "operationId": "get_records_api_v1_records_get",
                    "parameters": [
                        {
                            "name": "start_time",
                            "in": "query",
                            "required": true,
                            "schema": {
                                "type": "string",
                                "format": "date-time",
                                "title": "应该包含时区，like 2024-03-06T00:00:00Z"
                            }
                        },
                        {
                            "name": "end_time",
                            "in": "query",
                            "required": false,
                            "schema": {
                                "anyOf": [
                                    {
                                        "type": "string",
                                        "format": "date-time"
                                    },
                                    {
                                        "type": "null"
                                    }
                                ],
                                "title": "可以不传，默认为now; 应该包含时区，like 2024-03-06T00:00:00Z"
                            }
                        },
                        {
                            "name": "type",
                            "in": "query",
                            "required": true,
                            "schema": {
                                "enum": [
                                    "irrigation",
                                    "fertilizer"
                                ],
                                "type": "string",
                                "title": "Type"
                            }
                        }
                    ],
                }
            }
        },
        "components": {
            "schemas": {
                "Record": {
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "irrigation",
                                "fertilizer"
                            ],
                            "title": "Type"
                        },
                        "amount": {
                            "type": "number",
                            "title": "Amount"
                        },
                        "details": {
                            "anyOf": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "null"
                                }
                            ],
                            "title": "Details"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Timestamp"
                        }
                    },
                    "type": "object",
                    "required": [
                        "type",
                        "amount",
                        "timestamp"
                    ],
                    "title": "Record"
                },
    }
    """
    # 构建 URL
    if vorbose:
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
        if vorbose:
            print(f"WebClient sending request: {request_kwargs}")
        response = requests.request(**request_kwargs)

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.json() if response.content else None,
        }
    except requests.exceptions.RequestException as e:
        return {"status_code": None, "headers": {}, "data": {"error": str(e)}}


def execute_python_code(code):
    try:
        result = subprocess.run(["python", "-c", code], capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()
        if result.stderr:
            output += f"\nerr: {result.stderr.strip()}"
    except Exception as e:
        output = f"执行错误: {str(e)}"
    return output


def do_prompt(conversation_id, msg, vorbose: bool):
    for _ in range(10):
        if vorbose:
            print("sending msg: ", msg.content)
        res = chat_no_stream(msg, BOT_ID, USER_ID, conversation_id)
        try:
            res_dict = json.loads(res)
        except json.JSONDecodeError as e:
            print("json decode error: ", e)
            msg = Message.build_user_question_text("json decode error: " + e)
            continue

        print(f"WebClient: {res_dict if vorbose else res_dict['info']} ...")

        if res_dict["python_code"]:
            print(">> 请求执行pyton代码: \n", res_dict["python_code"], "\n是否执行(y/n): ", end="")
            if input() != "y":
                print("代码未执行, 请调整prompt 或 改进项目代码")
                break
            else:
                result = execute_python_code(res_dict["python_code"])
                print("执行结果: ", result)
                break

        if res_dict["status"] == "error" or res_dict["status"] == "completed":
            print("end of conversation: ", res_dict if vorbose else res_dict["info"])
            break

        msg_list = []
        for api_call in res_dict["api_calls"]:
            call_res = execute_api_call(False, "127.0.0.1:8000", api_call)
            msg_list.append(call_res)
        msg = Message.build_user_question_text(json.dumps(msg_list))


def main():
    conversation = coze.conversations.create()
    while True:
        print("> ", end="")
        user_prompt = input()
        msg = Message.build_user_question_text(user_prompt)
        do_prompt(conversation.id, msg)


if __name__ == "__main___":
    main()
