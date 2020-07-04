# !/usr/bin/python3.7
# -*- coding: utf-8 -*-

# Copyright 2020 ABC-CY
# Author: Eric Lee
# POST inquary to video_serv:

import requests, json

# 终端列表：通过连接相同Wifi热点访问（不同的AP也可以，可能速度有点影响）
# terminal_list = [["172.16.0.143", 5000]]
terminal_list = [["192.168.31.158", 5000]]
user_id = "Raspi-1"

def gen_url(server, opt):
    return "http://%s:%d/%s" % (server[0], server[1], opt)


if __name__ == "__main__":
    # 用于json传递：token获得后更新
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        "user": user_id,
        'token': '',
    }

    try:
        # 取token：
        r = requests.post(url=gen_url(terminal_list[0], "get_token"), headers=headers, timeout=5)
    except Exception as e:
        print("访问失败：", str(e))
        exit(0)

    token = r.text

    # 更新Token
    headers["token"] = token
    print("get_token：", token)

    # 等效的调用：
    # requests.post(url="http://127.0.0.1:5000/get_filelist",
    #               json={"filename": "xxx.mp4"},
    #               headers={"Content-Type": 'application/json;charset=UTF-8', "user": "Raspi-1", "token": "xxxxx"}
    #               )

    r = requests.post(url=gen_url(terminal_list[0], "get_filelist"), headers=headers, timeout=5)
    print("get_filelist: ", r.text)

    # 删除文件：可以删除多个，输入参数为文件名列表
    filename = eval(r.text)
    data = {
        "filename": [filename[0]+"not delete"]
    }
    r = requests.post(url=gen_url(terminal_list[0], "delete_file"), json=data, headers=headers, timeout=5)
    print("delete_file:", r.text)

    # 取得已上传的文件清单：
    r = requests.post(url=gen_url(terminal_list[0], "get_filelist"), headers=headers, timeout=5)
    print("get_filelist:", r.text)

    # 文件上传：files指定上传的文件，采用multipart/form-data，不设置Content-Type，自动计算boundary
    r = requests.post(url=gen_url(terminal_list[0], "upload_file"), headers={"user": user_id, "token": token}, files={'file': open('circle.mp4', 'rb')})
    print("upload_file:", r.text)

    # 取终端信息和播放列表：
    r = requests.post(url=gen_url(terminal_list[0], "get_playlist"), headers=headers, timeout=5)
    print("get_playlist:", r.text)

    # 修改设置后重新设置：
    data = eval(r.text)
    data['is_random'] = 'true'
    r = requests.post(url=gen_url(terminal_list[0], "set_playlist"), headers=headers, json=data, timeout=5)
    print("set_playlist:", r.text)

    r = requests.post(url=gen_url(terminal_list[0], "get_playlist"), headers=headers, timeout=5)
    print("get_playlist after edit:", r.text)

    r = requests.post(url=gen_url(terminal_list[0], "get_running_info"), headers=headers, timeout=5)
    print("get_runninginfo:", r.text)

    # 下载截屏文件：
    info = eval(r.text)
    data = {
        "filename": info["r_screenshot"]
    }
    r = requests.post(url=gen_url(terminal_list[0], "download_file"), json=data, headers=headers, timeout=5)
    with open(data["filename"], "wb") as code:
        code.write(r.content)
    print("download_file:", data["filename"])


