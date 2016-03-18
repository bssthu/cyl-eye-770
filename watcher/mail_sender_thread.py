#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : mail_sender_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import os
import threading
import time
import zipfile
import log


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
        self.interval = email_config['interval']
        self.watch_path = email_config['watchPath']
        self.file_ext = email_config['fileExt']
        self.file_num = email_config['fileNum']
        self.running = True

    def run(self):
        """线程主函数

        循环运行，每隔一定时间，寻找观察目录下最新的几个文件，打包发送邮件附件。
        """

        # check
        log.info('mail sender: start')

        # send & wait
        while self.running:
            # 发送
            try:
                self.send_data()
            except Exception as e:      # TODO: 发生异常时报警
                log.error('mail sender error: %s' % e)
            # 延时
            for i in range(0, self.interval):
                time.sleep(1)
                if not self.running:
                    break
        log.info('mail sender: bye')

    def send_data(self):
        """打包并发送邮件"""

        # 查找文件
        files_to_send = self.find_files(self.watch_path, self.file_ext, self.file_num)
        # 压缩打包
        self.zip_files(self.watch_path, files_to_send)

    def find_files(self, watch_path, file_ext, file_num):
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
        files_to_send = [os.path.abspath(pair[1]) for pair in files_with_ext[:self.file_num]]
        return files_to_send

    def zip_files(self, watch_path, files_to_send):
        """打包文件

        Args:
            watch_path: 监视的目录
            files_to_send: 要发送的文件

        Raises:
            Exception if watch_path is not dir
        """
        if not os.path.isdir(watch_path):
            raise Exception('%s is not a dir.' % watch_path)

        zip_name = os.path.join(self.watch_path, files_to_send[0] + '.zip')
        f = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        for file_name in files_to_send:
            f.write(file_name, os.path.basename(file_name))
        f.close()

