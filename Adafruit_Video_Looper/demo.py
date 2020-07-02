
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xk'

from flask import Flask, render_template, request, send_from_directory, jsonify
import os


app = Flask(__name__)

 # os.getcwd() 返回当前工作目录。 E:\accept\python\uploadFile\www
# 设置文件的上传目录
upload_file_folder = os.path.join(os.getcwd(),'upload') # E:\accept\python\uploadFile\www\upload

'''
    启动应用打开 index.html
'''
@app.route('/')
def home():
    # return render_template('index.html')
    return "Hello world"

'''
    上传操作
'''
@app.route('/upload', methods=['POST'])
def upload():
    print(request.json)
    file = request.files['file']         # data_post为POST上传的参数名；data_post=
    # token = request.files['token']
    print("filname=", file.filename)

    if not file:
        # return render_template('index.html', status='null')
        return "Hello world: not find file"

    # 检查文件类型
    if check_file_type(file.filename):
        # 一句代码完成保存文件操作
        file.save(os.path.join(upload_file_folder, file.filename))
        # return render_template('index.html', status='OK')
        return 'OK'
    else:
        return 'NO'

@app.route('/setPlaylist', methods=['POST'])
def setPlaylist():
    print(request.json)
    print("key1=", request.json["key1"])
    return "JSON OK"

@app.route('/fetch_files', methods=['POST'])
def fetch_list():
    # 创建一个list作为容器，存放上传目录下的所有文件
    file_link_list = []
    #判断upload_file_folder目录是否存在，如果不存在，创建目录
    if not os.path.exists(upload_file_folder):
        # 创建目录
        os.mkdir(upload_file_folder)
    # 列举目录下的所有文件
    file_list = os.listdir(upload_file_folder)
    # 遍历list集合
    for filename in file_list:
        # 将文件名添加到list集合中
        file_link_list.append(filename)
    return jsonify(file_link_list)

'''
    文件下载操作
'''
@app.route('/download/<filename>')
def download(filename):
    # 中文名的文件无法下载  2017-12-3 14:38:19
    return send_from_directory(upload_file_folder,filename, as_attachment=True)



'''
    检查文件类型
'''
def check_file_type(filename):
    file_type = [ 'jpg', 'doc', 'docx', 'txt', 'pdf', 'PDF','png', 'PNG', 'xls', 'rar', 'exe', 'md', 'zip']
    # 获取文件后缀
    ext = filename.split('.')[1]
    # 判断文件是否是允许上传得类型
    if ext in file_type:
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(debug=True)
