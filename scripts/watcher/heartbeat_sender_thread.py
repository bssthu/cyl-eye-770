#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : heartbeat_sender_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import threading
# try to support python2
try:
    import urllib.request as rq
    from urllib.parse import urlencode
except ImportError:
    import urllib2 as rq
    from urllib import urlencode
import log


class HeartbeatSenderThread(threading.Thread):
    """发送心跳包到 server 的线程"""

    def __init__(self, server_url):
        """构造函数

        Args:
            server_url: http 服务器地址
        """
        super().__init__()
        self.server_url = server_url

    def run(self):
        """线程主函数

        发送时间及消息到服务器
        """
        try:
            headers = {
                'content-type': 'application/json'
            }
            values = {
                "heartbeat_msg": '@'*10
            }
            data = urlencode(values).encode()
            req = rq.Request(self.server_url, data=data, headers=headers)
            response = rq.urlopen(req, timeout=5)
            log.debug('send heartbeat to server: %s %s' % (response.status, response.reason))
        except Exception as e:
            log.error('send heartbeat to server failed: %s' % e)
