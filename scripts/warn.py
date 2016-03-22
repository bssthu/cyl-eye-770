#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : warn.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 报警推送模块
#

import datetime
import threading
# try to support python2
try:
    import urllib.request as rq
    from urllib.parse import urlencode
except ImportError:
    import urllib2 as rq
    from urllib import urlencode
import base64
import log


base64_auth_string = ''


def initialize_warn(jpush_config):
    """初始化报警推送系统

    在 log 初始化之后，调用本 package 中其他方法之前调用本方法。

    Args:
        jpush_config: jpush 的配置信息
    """

    app_key = jpush_config['appKey']
    master_secret = jpush_config['masterSecret']

    global base64_auth_string
    k_v = '%s:%s' % (app_key, master_secret)
    base64_auth_string = base64.b64encode(bytes(k_v, 'utf-8')).decode()


def push(msg):
    WarnPushThread(base64_auth_string, msg).start()


class WarnPushThread(threading.Thread):
    """发送 jpush 的线程"""

    def __init__(self, auth_string, msg):
        """构造函数

        Args:
            auth_string: 身份验证字符串
            msg: 要推送的消息
        """
        super().__init__()
        self.auth_string = auth_string
        time_string = datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')
        self.msg = '%s, %s' % (time_string, msg)

    def run(self):
        """线程主函数

        用 https 方式发送推送
        """
        try:
            url = 'https://api.jpush.cn/v3/push'
            headers = {
                'content-type': 'application/json',
                'Authorization': 'Basic %s' % self.auth_string
            }
            values = {
                "platform": "all",
                "audience": "all",
                "notification": {
                    "alert": self.msg
                }
            }
            data = urlencode(values).encode()
            req = rq.Request(url, data=data, headers=headers)
            response = rq.urlopen(req)
            log.debug('push: %s %s' % (response.status, response.reason))
        except Exception as e:
            log.error('push error: %s' % e)
        else:
            log.debug('push warn msg: %s' % self.msg)
