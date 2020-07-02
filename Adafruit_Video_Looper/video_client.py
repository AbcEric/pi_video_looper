# !/usr/bin/python3.7
# -*- coding: utf-8 -*-

# Copyright 2020 ABC-CY
# Author: Eric Lee
# POST inquary to video_serv:

import requests, json
server_list = ["127,0,0,1", ]

if __name__ == "__main__":
    # 用于json传递
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        "user": "Raspi-1",
        'token': '',
    }
    # 用于文件上传
    headers_file = {
         # 'Content-Type': 'multipart/form-data',  # boundary自动计算！
        "user": "Raspi-1",
        'token': '',
    }

    url = 'http://127.0.0.1:5000/get_token'

    # r = requests.post(url=url, json=data, headers=headers, timeout=5)
    r = requests.post(url=url, headers=headers, timeout=5)
                      # , verify=False, allow_redirects=False).json()

    # r = requests.post(url="http://127.0.0.1:5000/get_token", data=json.dumps({'user': 'Raspi-1', 'expire': 60}),)
                  # headers={'Content-Type': 'application/json'})
    token = r.text

    # 更新Token
    headers["token"] = token
    headers_file["token"] = token
    print("generate_token [", token, "]")

    url = "http://127.0.0.1:5000/get_filelist"
    r = requests.post(url=url, headers=headers, timeout=5)
    print("get_filelist:", r.text)

    url = "http://127.0.0.1:5000/delete_file"
    filename = eval(r.text)
    data = {
        "filename": [filename[0]+"test"]
    }
    r = requests.post(url=url, json=data, headers=headers, timeout=5)

    # r = requests.post(url="http://127.0.0.1:5000/delete_file", data=json.dumps({'filename': filename[0]}),
    #                   headers={'Content-Type': 'application/json'})
    print("delete_file:", r.text)

    url = "http://127.0.0.1:5000/get_filelist"
    r = requests.post(url=url, headers=headers, timeout=5)
    print("get_filelist:", r.text)

    url = "http://127.0.0.1:5000/upload_file"
    # 上传文件：files固定，multipart/form-data; boundary=d22e04ed8f9ce980a7182cbed70cc1ac。boundary如何计算出来的？
    r = requests.post(url=url, headers=headers_file, files={'file': open('circle.mp4', 'rb')})
    print("upload_file:", r.text)

    # 传入JSON文本：也支持xml文本上传
    url = "http://127.0.0.1:5000/set_playlist"
    data = {
           'terminal_info': {
               'name': 'Raspi-1',
               'resolution': '1920x1080',
               'random': 'true',
               'direction': 'horizon',
               'position': 'C zone',
               'working-time': '8:00-22:00',
               'description': ''
            },
            'play_list': {
               '9:00': 'video1.mp4',
               '14:00': 'video2.mp4'
            }
    }
    r = requests.post(url=url, headers=headers, json=data, timeout=5)
    print("set_playlist:", r.text)

    url = "http://127.0.0.1:5000/get_playlist"
    r = requests.post(url=url, headers=headers, timeout=5)
    print("get_playlist:", r.text)

