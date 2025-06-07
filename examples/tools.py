import functools
import json
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Literal, Optional

import requests
from cozepy import Message
from llama_index.core.schema import NodeWithScore
from pydantic import BaseModel

from .coze_llm import (
    BOT_ID,
    USER_ID,
    chat_no_stream,
    coze,
)
from .vector_store_index import retriever as grape_retriever


class ToolResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str = ""
    format: Literal["json", "text", "markdown"]
    call: str



def json_response(format: Literal["json", "text", "markdown"]):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_str = ", ".join(repr(a) for a in args)
            kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
            call_str = f"{func.__name__}({', '.join(filter(None, [args_str, kwargs_str]))})"
            try:
                result = func(*args, **kwargs)
                return ToolResponse(
                    success=True, data=result, message="", format=format, call=call_str
                ).model_dump_json()
            except Exception as e:
                return ToolResponse(
                    success=False, data=None, message=str(e), format=format, call=call_str
                ).model_dump_json()

        return wrapper
    return decorator


@json_response(format='markdown')
def get_grape_docs(query: str) -> list[str]:
    """Get grape docs."""
    res = []
    node_with_scores: list[NodeWithScore] = grape_retriever.retrieve(query)
    for node_s in node_with_scores:
        node = node_s.node  # 获取内部 node
        text = getattr(node, "text", "") or getattr(node, "get_text", lambda: "")()
        metadata = getattr(node, "metadata", {})

        # 只保留感兴趣的字段
        useful_metadata_keys = ["file_path", "header_path"]
        useful_metadata = {k: v for k, v in metadata.items() if k in useful_metadata_keys}

        node_str = "📁 Metadata:\n"
        for k, v in useful_metadata.items():
            node_str += f"- {k}: {v}\n"

        node_str += "📝 Text:\n" + text
        res.append(node_str)
    return '\n---\n'.join(res)

@json_response(format="text")
def get_now_local_datetime() -> str:
    return (datetime.now(tz=timezone.utc) + timedelta(hours=8)).isoformat()[:-6] + "+08:00"


@json_response(format='json')
def execute_api_call(use_https: bool, domain: str, api_call: dict[str, Any], vorbose: bool) -> dict[str, any]:
    """
    执行API调用，并返回响应结果。

    :param use_https: 是否使用 HTTPS
    :param domain: API 服务器的域名（不包含协议前缀）
    :param api_call: API 调用格式，包含 path、method、query_args、path_args、data_args、headers 等字段
    :return: 包含响应状态码、响应头和响应数据的字典

    下面是可以调用的api:
    http://localhost:8080
    {"openapi":"3.1.0","info":{"title":"FastAPI","version":"0.1.0"},"paths":{"/api/v1/sensors/values":{"get":{"summary":"Get All Sensor Values","operationId":"get_all_sensor_values_api_v1_sensors_values_get","responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{}}}}}}},"/api/v1/irrigation_events":{"post":{"summary":"Create Irrigation Event","operationId":"create_irrigation_event_api_v1_irrigation_events_post","requestBody":{"required":true,"content":{"application/json":{"schema":{"$ref":"#/components/schemas/IrrigationEvent"}}}},"responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{}}}},"422":{"description":"Validation Error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/HTTPValidationError"}}}}}},"get":{"summary":"Get Irrigation Events","operationId":"get_irrigation_events_api_v1_irrigation_events_get","parameters":[{"name":"start_time","in":"query","required":false,"schema":{"type":"string","format":"date-time","title":"Start Time"}},{"name":"end_time","in":"query","required":false,"schema":{"type":"string","format":"date-time","title":"End Time"}},{"name":"outlet","in":"query","required":false,"schema":{"type":"string","title":"Outlet"}},{"name":"vineyard_id","in":"query","required":false,"schema":{"type":"string","title":"Vineyard Id"}},{"name":"limit","in":"query","required":false,"schema":{"type":"integer","maximum":1000,"minimum":1,"default":99,"title":"Limit"}}],"responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{}}}},"422":{"description":"Validation Error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/HTTPValidationError"}}}}}}},"/api/v1/events":{"post":{"summary":"Create Event","operationId":"create_event_api_v1_events_post","requestBody":{"required":true,"content":{"application/json":{"schema":{"$ref":"#/components/schemas/Event"}}}},"responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{}}}},"422":{"description":"Validation Error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/HTTPValidationError"}}}}}},"get":{"summary":"Get Events","operationId":"get_events_api_v1_events_get","parameters":[{"name":"start_time","in":"query","required":false,"schema":{"type":"string","format":"date-time","title":"Start Time"}},{"name":"end_time","in":"query","required":false,"schema":{"type":"string","format":"date-time","title":"End Time"}},{"name":"event_type","in":"query","required":false,"schema":{"type":"string","title":"Event Type"}},{"name":"vineyard_id","in":"query","required":false,"schema":{"type":"string","title":"Vineyard Id"}},{"name":"limit","in":"query","required":false,"schema":{"type":"integer","maximum":1000,"minimum":1,"default":99,"title":"Limit"}}],"responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{}}}},"422":{"description":"Validation Error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/HTTPValidationError"}}}}}}}},"components":{"schemas":{"Event":{"properties":{"vineyard_id":{"type":"string","title":"Vineyard Id"},"event_type":{"type":"string","title":"Event Type"},"details":{"anyOf":[{"type":"string"},{"type":"null"}],"title":"Details"},"timestamp":{"anyOf":[{"type":"string","format":"date-time"},{"type":"null"}],"title":"Timestamp"}},"type":"object","required":["vineyard_id","event_type"],"title":"Event"},"HTTPValidationError":{"properties":{"detail":{"items":{"$ref":"#/components/schemas/ValidationError"},"type":"array","title":"Detail"}},"type":"object","title":"HTTPValidationError"},"IrrigationEvent":{"properties":{"outlet":{"type":"string","title":"Outlet"},"vineyard_id":{"type":"string","title":"Vineyard Id"},"amount":{"type":"number","title":"Amount"},"area":{"type":"number","title":"Area"},"timestamp":{"anyOf":[{"type":"string","format":"date-time"},{"type":"null"}],"title":"Timestamp"}},"type":"object","required":["outlet","vineyard_id","amount","area"],"title":"IrrigationEvent"},"ValidationError":{"properties":{"loc":{"items":{"anyOf":[{"type":"string"},{"type":"integer"}]},"type":"array","title":"Location"},"msg":{"type":"string","title":"Message"},"type":{"type":"string","title":"Error Type"}},"type":"object","required":["loc","msg","type"],"title":"ValidationError"}}}}
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
