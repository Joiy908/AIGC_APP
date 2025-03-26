import os
import json


import requests
from typing import Any, Dict


def get_token():
    # Define API endpoint
    url = "http://127.0.0.1:8000/token"  # Replace with actual FastAPI server URL

    # Define login credentials
    data = {
        "grant_type": "password",
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "scope": "",
        "client_id": None,
        "client_secret": None,
    }

    # Send POST request
    response = requests.post(url, data=data)

    # Check response
    if response.status_code == 200:
        token_data = response.json()
        return response.status_code, token_data["access_token"]
    else:
        return response.status_code, response.text


def create_course(token, cno, cname, ccredit, cdept):
    """Creates a course using the FastAPI backend."""
    url = "http://127.0.0.1:8000/courses/"  # Replace with actual FastAPI server URL

    # Define course data
    data = {
        "cno": cno,
        "cname": cname,
        "ccredit": ccredit,
        "cdept": cdept
    }

    # Set headers with Bearer token authentication
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Send POST request
    response = requests.post(url, json=data, headers=headers)

    # Check response
    if response.status_code == 201:
        return response.status_code, response.json()  # Successful course creation
    else:
        return response.status_code, response.text  # Return error message


def execute_api_call(use_https: bool, domain: str, api_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行API调用，并返回响应结果。

    :param use_https: 是否使用 HTTPS
    :param domain: API 服务器的域名（不包含协议前缀）
    :param api_call: API 调用格式，包含 path、method、query_args、path_args、data_args、headers 等字段
    :return: 包含响应状态码、响应头和响应数据的字典
    """
    # 构建 URL
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

# Example usage:
# err, token = get_token("admin", "password123")
# if not err:
#     err, result = create_course(token, "CS101", "Intro to CS", 3, "Computer Science")
#     print("Error:" if err else "Success:", result)



if __name__ == '__main__':
    _, token = get_token()
    