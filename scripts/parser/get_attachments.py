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


def get_mail(host, port, user, password, criteria, attachment_path):
    """收取邮件，遍历解析

    Args:
        host: imap 服务器
        port: imap 端口
        user: 用户名
        password: 密码
        criteria: 邮件搜索准则
        attachment_path: 附件存放路径
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
        typ, data = conn.search(None, criteria)
        mail_ids = [i for i in data[0].split()]
        mail_ids.reverse()      # 从最新的邮件开始
    except Exception as e:
        print('failed to get mail id: %s' % e)
        return

    # 遍历列表
    for mail_id in mail_ids:
        try:
            typ, data = conn.fetch(mail_id, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            parse_email_and_save_attachments(msg, attachment_path)   # 解析，下载附件
        except Exception as e:
            print('failed to get attachment(s) from mail %s: %s' % (mail_id, e))
            continue


def parse_email_and_save_attachments(msg, path):
    """解析一封邮件，下载附件

    Args:
        msg: 邮件内容
        path: 附件保存路径
    """
    for part in msg.walk():
        if not part.is_multipart():
            filename = part.get_filename()

            # if is attachment
            if filename is not None:
                print(filename)
                # download attachment
                content = part.get_payload(decode=True)
                # save file
                fp = open(os.path.join(path, filename), 'wb')
                fp.write(content)
                fp.close()


def main():
    # config
    configs = load_parser_config()
    if configs is None:
        return
    if 'email' not in configs \
            or 'name' not in configs['email'] \
            or 'password' not in configs['email'] \
            or 'imapServer' not in configs['email'] \
            or 'criteria' not in configs['email'] \
            or 'attachmentPath' not in configs:
        print('missing element(s) in parser config.')
        return None

    get_mail(configs['email']['imapServer'], 993,
             configs['email']['name'], configs['email']['password'],
             configs['email']['criteria'], configs['attachmentPath'])


if __name__ == '__main__':
    main()
