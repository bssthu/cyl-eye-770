#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : get_attachments.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 从邮件中下载附件
# 

import imaplib
import email
from load_parser_config import *


def load_config(config_file_name):
    """载入配置文件

    Args:
        config_file_name: 配置文件名
    """

    # load
    try:
        with open(config_file_name) as config_data:
            configs = json.load(config_data)
    except Exception as e:
        print('failed to load config from %s.' % config_file_name)
        print(e)
        return None

    return configs


def get_mail(host, port, user, password):
    """收取邮件，遍历解析

    Args:
        host: imap 服务器
        port: imap 端口
        user: 用户名
        password: 密码
    """

    # 建立连接
    try:
        conn = imaplib.IMAP4_SSL(host, port)
        conn.login(user, password)
    except Exception as e:
        print('connect failed: %s' % e)
        return

    # 获取列表
    try:
        conn.select('INBOX', False)
        typ, data = conn.search(None, 'ALL')
        mail_ids = [i for i in data[0].split()]
    except Exception as e:
        print('failed to get mail id: %s' % e)
        return

    # 遍历列表
    for mail_id in mail_ids:
        try:
            typ, data = conn.fetch(mail_id, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            parse_email(msg)
        except Exception as e:
            print('failed to get attachment(s) from mail %s: %s' % (mail_id, e))
            continue


def parse_email(msg):
    """解析一封邮件

    Args:
        msg: 邮件内容
    """
    for part in msg.walk():
        if not part.is_multipart():
            filename = part.get_filename()
            content = part.get_payload(decode=True)

            if filename:
                # is attachment
                print(filename)
                # TODO: download attachment


def main():
    # config
    configs = load_parser_config()
    if configs is None:
        return
    if 'email' not in configs \
            or 'name' not in configs['email'] \
            or 'password' not in configs['email'] \
            or 'imapServer' not in configs['email'] \
            or 'attachmentPath' not in configs:
        print('missing element(s) in parser config.')
        return None
    get_mail(configs['email']['imapServer'], 993,
             configs['email']['name'], configs['email']['password'])

if __name__ == '__main__':
    main()
