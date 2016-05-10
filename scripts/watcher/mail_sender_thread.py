#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : mail_sender_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import threading
import time
import log
import warn
import watcher.mail_util as mail_util


class MailSenderThread(threading.Thread):
    """查找待发文件并发送邮件的线程"""

    def __init__(self, email_config):
        """构造函数

        Args:
            email_config: 邮件发送设置
        """
        super().__init__()
        self.email_name = email_config['name']
        self.email_password = email_config['password']
        self.smtp_server = email_config['smtpServer']
        self.watch_path = email_config['watchPath']
        self.file_ext = email_config['fileExt']
        self.file_num = email_config['fileNum']
        self.interval = email_config.get('interval', 40)
        self.extra_watch_files = email_config.get('extraWatchFiles', [])
        self.running = True

    def run(self):
        """线程主函数

        循环运行，每隔一定时间，寻找观察目录下最新的几个文件，打包发送邮件附件。
        """

        # check
        log.info('mail sender: start')

        last_send_ok = True

        # send & wait
        while self.running:
            # 发送
            try:
                self.send_data()
            except Exception as e:
                log.error('mail sender error: %s' % e)
                if last_send_ok:
                    warn.push('watcher: 邮件发送失败')
                    last_send_ok = False
            else:
                last_send_ok = True
            # 延时
            for i in range(0, self.interval):
                time.sleep(1)
                if not self.running:
                    break
        log.info('mail sender: bye')

    def send_data(self):
        """打包并发送邮件"""

        # 查找文件
        files_to_send = mail_util.find_files(self.watch_path, self.file_ext, self.file_num)
        files_to_send.extend(self.extra_watch_files)
        if len(files_to_send) == 0:
            return
        # 压缩打包
        zip_file = mail_util.zip_files(self.watch_path, files_to_send)
        # 发送邮件
        mail_util.send_mail(zip_file, self.email_name, self.email_password, self.smtp_server)
        log.info('email sent.')
