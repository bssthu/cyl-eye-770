#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : warn.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 报警推送模块
#   报警信息先通过 http 方式发到服务器，再转发到 jpush 官方的服务器。
#

import threading
import time
import queue
# try to support python2
try:
    import urllib.request as rq
    from urllib.parse import urlencode
except ImportError:
    import urllib2 as rq
    from urllib import urlencode
import log


warn_thread = None


def initialize_warn(http_server_config):
    """初始化报警推送系统

    在 log 初始化之后，调用本 package 中其他方法之前调用本方法。

    Args:
        http_server_config: http 服务器的配置信息
    """

    global warn_thread
    http_server_url = 'http://%s:%d/' % (http_server_config['ipAddress'], http_server_config['port'])
    retry_interval = http_server_config['retryInterval'] if 'retryInterval' in http_server_config else 40
    warn_thread = WarnToServerThread(http_server_url, retry_interval)
    warn_thread.start()


def stop_warn():
    """关闭报警推送系统"""
    global warn_thread
    if warn_thread is not None:
        warn_thread.running = False
        warn_thread.join()
        warn_thread = None


def push(msg):
    """向 server 以 http 方式发送警告

    Args:
        msg: 报警信息
    """
    if warn_thread is not None:
        warn_thread.add_warn_msg(msg)


class WarnToServerThread(threading.Thread):
    """发送警告到 server 的线程"""

    def __init__(self, server_url, retry_interval):
        """构造函数

        Args:
            server_url: http 服务器地址
            retry_interval: 失败时的重试时间间隔（秒）
        """
        super().__init__()
        self.server_url = server_url
        self.retry_interval = retry_interval
        self.msg_queue = queue.Queue()  # 消息队列
        self.last_msg = None        # 上一条发送失败的消息
        self.running = True

    def run(self):
        """线程主函数"""
        log.info('warn thread: start')

        while self.running:
            try:
                if self.send_msgs():
                    time.sleep(1)
                    continue    # ok
                else:
                    # 失败，延时后再重试
                    for i in range(0, self.retry_interval):
                        time.sleep(1)
                        if not self.running:
                            break
            except Exception as e:
                log.error('warn thread error: %s' % e)
        log.info('warn thread: bye')

    def send_msgs(self):
        """发送队列中的所有消息到服务器

        Returns:
            False: 发送失败
        """
        while not self.msg_queue.empty():
            try:
                if self.last_msg is not None:
                    self.send_msg(self.last_msg)
                    self.last_msg = None
                else:
                    self.last_msg = self.msg_queue.get(False)
                    self.send_msg(self.last_msg)
                    self.last_msg = None
            except queue.Empty:
                break
            except Exception as e:
                log.error('post to server error: %s' % e)
                return False
        return True

    def send_msg(self, msg):
        """发送一条消息到服务器

        Args:
            msg: 消息
        """
        headers = {
            'content-type': 'application/json'
        }
        values = {
            "push_msg": msg
        }
        data = urlencode(values).encode()
        req = rq.Request(self.server_url, data=data, headers=headers)
        response = rq.urlopen(req, timeout=5)
        log.debug('post to server: %s %s' % (response.status, response.reason))
        log.info('post to server, warn msg: %s' % msg)

    def add_warn_msg(self, msg):
        """将警报加入队列"""
        self.msg_queue.put(msg)
