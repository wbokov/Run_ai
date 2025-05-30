import time
import requests
import json


def create_request(key, mode, content):
    url = "https://chatinfo.ru/api/gpt/create_request"
    parameters = {"key": key, "mode": mode, "content": content}
    payload = json.dumps(parameters)
    response = requests.post(url, data=payload)

    return response.json()


def get_response(key, id):
    url = "https://chatinfo.ru/api/gpt/get_response"
    parameters = {"key": key, "id": id}
    payload = json.dumps(parameters)
    response = requests.post(url, data=payload)

    return response.json()


def solve(key, mode, content):
    # Шаг 1: создаем запрос
    request_info = create_request(key, mode, content)

    if "id" not in request_info:
        print("Failed to create request. Error: " + request_info["error"] + ".")
        return None

    request_id = request_info["id"]

    print("Created request with id " + str(request_id) + ".")
    time.sleep(2)

    # Шаг 2: ждем ответа
    max_attempts = 80
    attempts = 0

    while attempts < max_attempts:
        response_info = get_response(key, request_id)

        if "success" in response_info and response_info["success"]:
            return response_info["result"]
        elif "solving" in response_info and response_info["solving"]:
            time.sleep(2)
            attempts += 1
        else:
            print("Failed to get response. Error: " + response_info["error"] + ".")
            return None

    print("Timed out waiting for response.")
    return None
