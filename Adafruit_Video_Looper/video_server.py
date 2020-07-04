# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 ABC-CY
# Author: Eric Lee

'''
# 响应远程控制指令（文件清单，播放列表，时间，分辨率等），接受传输文件，发送目录变更信息给video_looper.py，安全控制等；
# /boot/video_looper.ini

或者采用Flask构建web应用程序的Python微框架，是一个轻量级的WSGI web应用程序框架。

指令格式json，均采用POST方式
1. 播放设置：get_playlist(), set_playlist()。包括何时播放什么，顺序还是随机播放，何时待机等；
2. 下载、上传文件, 屏幕截屏：download_file(), upload_file()，get_filelist(), delete_file();
3. 终端信息：get_runinginfo(), set_info()。包括当前时间，分辨率，横屏竖屏等；
4. 安全控制：指定终端才有权限？每次动态变化？增加token, 读取设备信息和运行状态；

Q:
1. 大文件传输效率？
2. 远程控制Raspi：启停

'''

from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import time
import base64
import hmac
import configparser
import platform
import pyscreenshot as ImageGrab

app = Flask(__name__)


# 设置文件的上传目录
# upload_file_folder = '/home/pi/Videos'
upload_file_folder = os.path.join(os.getcwd(), 'upload')

# 配置文件：注意里面不能有中文等，否则configparser出错！
# config_path = '/boot/video_looper.ini'
config_path = '../assets/video_looper.ini'

config = configparser.ConfigParser()
if len(config.read(config_path)) == 0:
    raise RuntimeError("没有找到配置文件：" + config_path)


# 检查文件类型：避免非法上传！
def check_file_type(filename):
    file_type = ['jpg', 'png', 'mov', 'mp4', 'avi', 'h264']        # 不区分大小写
    ext = filename.split('.')[1]

    # 转换ext为小写
    if ext in file_type:
        return True

    return False


# Token验证：
def certify_token_by_request(request):
    try:
        key = request.headers["user"]
        token = request.headers["token"]
    except:
        print("输入参数有误：请检查headers设置！")
        return False
    else:
        return certify_token(key, token)


def certify_token(key, token):
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        return False
    known_sha1_tsstr = token_list[1]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_tsstr = sha1.hexdigest()
    if calc_sha1_tsstr != known_sha1_tsstr:
        # token certification failed
        return False
    # token certification success
    return True


@app.route('/')
def home():
    # return render_template('index.html')
    return "欢迎使用多媒体云平台！"


# 上传文件：将文件传给requests.post()的files参数，采用multipart/form-data
@app.route('/upload_file', methods=['POST'])
def upload():
    if not certify_token_by_request(request):
        return "ERROR - 权限验证失败 ..."

    # print("upload Header=", request.headers)
    file = request.files['file']         # data_post为POST上传的参数名；data_post=
    print("upload_file: ", file.filename)

    if not file:
        return "ERROR - 没有待上传的文件!"

    # 检查文件类型
    if not check_file_type(file.filename):
        return 'ERROR - 上传文件的类型不支持! 支持的类型包括jpg、png、mp4、h264和avi。'

    file.save(os.path.join(upload_file_folder, file.filename))

    return 'OK'


# 设置播放列表：放在ini文件中整合
@app.route('/set_playlist', methods=['POST'])
def set_playlist():
    if not certify_token_by_request(request):
        return "ERROR - 权限验证失败 ..."

    # 定义在/boot/video_looper.ini中[terminal]部分
    for name in request.json:
        if name not in ('t_name', 't_resolution', 't_direction', 'is_random', 't_working_time', 't_description', 't_playlist'):
            return "ERROR - 不支持的设置选项[%s]" % name

        if name == 'is_random':
            config.set('video_looper', name, request.json[name])
        else:
            config.set('terminal', name, request.json[name])

    with open(config_path, 'w') as configfile:
        config.write(configfile)

    print("set_playlist: Done")
    return "OK"


# 获取播放列表：
@app.route('/get_playlist', methods=['POST'])
def get_playlist():
    if not certify_token_by_request(request):
        return "ERROR - 权限验证失败 ..."

    print("get_playlist: ")
    return jsonify(
        t_name=config.get('terminal', 't_name'),
        t_resolution=config.get('terminal', 't_resolution'),
        is_random=config.get('video_looper', 'is_random'),
        t_direction=config.get('terminal', 't_direction'),
        t_working_time=config.get('terminal', 't_working_time'),
        t_description=config.get('terminal', 't_description'),
        t_playlist=config.get('terminal', 't_playlist')
    )


# 获取已上传的文件清单：
@app.route('/get_filelist', methods=['POST'])
def getFilelist():
    if not certify_token_by_request(request):
        return "ERROR - 权限验证失败 ..."

    file_link_list = []
    if not os.path.exists(upload_file_folder):
        # 创建目录
        os.mkdir(upload_file_folder)

    print("get_filelist from: ", upload_file_folder)
    file_list = os.listdir(upload_file_folder)
    for filename in file_list:
        file_link_list.append(filename)

    return jsonify(file_link_list)


# 文件下载：返回要下载的文件
@app.route('/download_file', methods=['POST'])
def download():
    if not certify_token_by_request(request):
        return "ERROR - 权限验证失败 ..."

    filename = request.json["filename"]
    print("download_file: ", filename)

    fname = os.path.join(upload_file_folder, filename)
    if os.path.isfile(fname):
        # 中文名的文件无法下载  2017-12-3 14:38:19
        return send_from_directory(upload_file_folder, filename, as_attachment=True)

    return "ERROR - 要下载的文件不存在[" + filename + "]"


# 删除指定的已上传文件：可以删除多个文件，输入为文件列表。
@app.route('/delete_file', methods=['POST'])
def delete():
    if not certify_token_by_request(request):
        return "ERROR - 权限验证失败 ..."

    # print(request.json)
    filename = request.json["filename"]
    print("delete_file: ", filename)

    for f in filename:
        fname = os.path.join(upload_file_folder, f)
        if os.path.isfile(fname):
            os.remove(fname)
        else:
            return "ERROR - 待删除的文件不存在[%s]" % f

    return "OK"


# 生成Token：user可相同，expire最大有效时间，单位为s。返回token（字符串）
@app.route('/get_token', methods=['POST'])
def get_token():
    try:
        key = request.headers.get("user")
    except:
        return "ERROR - 请检查输入参数headers的设置"

    expire = 30*60    # 30分钟超时
    print("get_token: 终端[%s]登录获取Token,expire=[%d]" % (key, expire))
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_tshex_str = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
    token = ts_str+':'+sha1_tshex_str
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))

    return b64_token.decode("utf-8")


# 获取当前运行状态：日期，时间，运行状态（runing，exit），温度，截屏
@app.route('/get_running_info', methods=['POST'])
def get_running_info():
    if not certify_token_by_request(request):
        return "ERROR - 权限验证失败 ..."

    # r = os.popen('python -V').read()
    if platform.system() == "Windows":
        cpu = mem = temperature = run = "Unknown"
    else:
        # 温度：
        # temperature = os.popen('cat /sys/class/thermal/thermal_zone0/temp').read()
        temperature = os.popen('vcgencmd measure_temp').read()

        # CPU使用：
        cpu = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").read

        # 内存：
        mem = os.popen('free -h').read()

        # video_looper的运行状态：
        run = os.popen("sudo supervisorctl status").read

    # 截屏：
    im = ImageGrab.grab()
    im.save(os.path.join(upload_file_folder, 'screen.jpg'))
    im.close()

    print("get_running_info: ")
    return jsonify(
        r_date=time.strftime('%Y-%m-%d', time.localtime(time.time())),
        r_time=time.strftime('%H:%M:%S', time.localtime(time.time())),
        r_status=run,
        r_cpu=cpu,
        r_memory=mem,
        r_temperature=temperature,
        r_screenshot='screen.jpg'
        # r_screenshot=config.get('terminal', 't_resolution'),
    )


# 自定义的异常处理函数：捕获404异常错误
@app.errorhandler(404)
def handle_404_error(err_msg):
    return "ERROR - 请检查输入，错误信息[%s]" % err_msg


if __name__ == '__main__':
    # server = "172.16.0.143"
    server = "192.168.31.158"
    port = 5000
    print("Server[%s:%d] is running ..." % (server, port))
    app.run(host=server, port=port, debug=False)
