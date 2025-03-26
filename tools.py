from typing import Any
import subprocess
import tempfile
import os


import requests

debug = True

def execute_script(type: str, code: str):
    """
    执行代码，并返回执行结果。
    请把结果打印到标准输出。
    默认非root用户，如果需要root权限，请在脚本中使用sudo。
    @param type: str, 脚本类型，目前支持 "python" 和 "bash"
    @param code: str, 脚本内容。请不要使用管道等开启新进程的操作，会导致读不到输出。
    @return: str, 执行结果
    """
    # confirm
    print(">> 请求执行代码: \n", code, "\n是否执行(y/n): ", end="")
    to_exec = input()
    if to_exec != 'y':
        return "用户取消执行"
    
    try:
        if type == "python":
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
                temp_file.write(code.encode())
                temp_file_path = temp_file.name
            
            result = subprocess.run(["python", temp_file_path], capture_output=True, text=True, timeout=5)
            os.remove(temp_file_path)  # Cleanup
            
        elif type == "bash":
            with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as temp_file:
                temp_file.write(code.encode())
                temp_file_path = temp_file.name
            
            result = subprocess.run(["bash", temp_file_path], capture_output=True, text=True, timeout=5)
            os.remove(temp_file_path)  # Cleanup
        
        else:
            return "不支持的脚本类型"
        
        output = result.stdout.strip()
        if result.stderr:
            output += f"\nerr: {result.stderr.strip()}"
    
    except subprocess.TimeoutExpired:
        output = "执行超时 (timeout)"
    except Exception as e:
        output = f"执行错误: {str(e)}"
    
    return output

def execute_api_call(api_calls: list[dict[str, Any]]) -> dict[str, Any]:
    """
    执行API调用，并返回响应结果。

    :param api_calls: API 调用格式，包含 path、method、query_args、path_args、data_args、headers
    :return: 包含响应状态码、响应头和响应数据的字典
    
    api_call example:
    { "path": "/users/{user_id}",       // API路径（支持路径参数）
      "method": "GET",                  // HTTP方法
      "query_args": {                   // 查询参数
        "verbose": true
      },
      "path_args": {                    // 路径参数
        "user_id": "123"
      },
      "data_args": {                    // 请求体参数（适用于POST/PUT/PATCH）
        "name": "John",
        "age": 30
      },
      "headers": {                      // 自定义请求头
        "Authorization": "Bearer token"
    }
    """
    use_https = False
    domain = "127.0.0.1:8000"
    # 构建 URL
    protocol = "https" if use_https else "http"
    res_list = []
    for api_call in api_calls:
        if debug:
            print(f"WebClient exec http call: {api_call}")
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
            res_list.append({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.content else None
            })
        except requests.exceptions.RequestException as e:
            res_list.append({
                "status_code": None,
                "headers": {},
                "data": {"error": str(e)}
            })
    return res_list

if __name__ == '__main__':
    test_code = """import subprocess
bash_command ='sudo iptables -A INPUT -p tcp --dport 8080 -j DROP'
result = subprocess.run(bash_command, shell=True, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
    """
    print(execute_python_code(test_code))