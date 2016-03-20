#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : mail_util.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   :
#

import os
import zipfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


def find_files(watch_path, file_ext, file_num):
    """寻找要发送的文件，按修改时间排序，取最新的几个返回

    Args:
        watch_path: 监视的目录
        file_ext: 文件扩展名
        file_num: 要发送的文件数

    Returns:
        list of files to send.

    Raises:
        Exception if watch_path is not dir
    """
    if not os.path.isdir(watch_path):
        raise Exception('%s is not a dir.' % watch_path)

    files = [os.path.join(watch_path, f) for f in os.listdir(watch_path)]
    files_with_ext = [(os.path.getmtime(f), f)
                      for f in files if os.path.isfile(f) and f.lower().endswith('.%s' % file_ext)]
    files_with_ext.sort()
    files_with_ext.reverse()
    files_to_send = [os.path.abspath(pair[1]) for pair in files_with_ext[:file_num]]
    return files_to_send


def zip_files(watch_path, files_to_send):
    """打包文件

    Args:
        watch_path: 监视的目录
        files_to_send: 要发送的文件

    Raises:
        Exception if watch_path is not dir
    """
    if not os.path.isdir(watch_path):
        raise Exception('%s is not a dir.' % watch_path)

    zip_file = os.path.abspath(os.path.join(watch_path, files_to_send[0] + '.zip'))
    f = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
    for file_name in files_to_send:
        f.write(file_name, os.path.basename(file_name))
    f.close()
    return zip_file


def send_mail(file_to_send, user, password, server):
    """发送邮件

    Args:
        file_to_send: 要发送的文件
        user: 用户名
        password: 密码
        server: SMTP 服务器
    """

    msg = MIMEMultipart()   # 带附件

    att1 = MIMEText(open(file_to_send, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    att1["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(file_to_send)
    msg.attach(att1)

    # 邮件头
    msg['to'] = user
    msg['from'] = user
    msg['subject'] = file_to_send

    # 发邮件
    conn = smtplib.SMTP_SSL(server)
    conn.login(user, password)
    conn.sendmail(msg['from'], msg['to'], msg.as_string())
    conn.quit()