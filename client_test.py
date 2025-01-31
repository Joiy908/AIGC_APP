import os
import requests


def get_token():
    # Define API endpoint
    url = "http://127.0.0.1:8000/token"  # Replace with actual FastAPI server URL

    # Define login credentials
    data = {
        "grant_type": "password",
        "username": os.get_,
        "password": password,
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

# Example usage:
# err, token = get_token("admin", "password123")
# if not err:
#     err, result = create_course(token, "CS101", "Intro to CS", 3, "Computer Science")
#     print("Error:" if err else "Success:", result)



if __name__ == '__main__':
    _, token = get_token('root', 'abc')
    s_code, result = create_course(token, "11110140", "大数据存储与管理", 3, "人工智能学院")
    print(s_code, result)
    