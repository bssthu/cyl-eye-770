#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : warn.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 报警推送模块
#   报警信息先通过 http 方式发到服务器，再转发到 jpush 官方的服务器。
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
http_server_url = 'http://localhost/'


def initialize_warn(jpush_config, http_server_config):
    """初始化报警推送系统

    在 log 初始化之后，调用本 package 中其他方法之前调用本方法。

    Args:
        jpush_config: jpush 的配置信息
        http_server_config: http 服务器的配置信息
    """

    global base64_auth_string, http_server_url

    app_key = jpush_config['appKey']
    master_secret = jpush_config['masterSecret']

    k_v = '%s:%s' % (app_key, master_secret)
    base64_auth_string = base64.b64encode(bytes(k_v, 'utf-8')).decode()
    http_server_url = 'http://%s:%d/' % (http_server_config['ipAddress'], http_server_config['port'])


def push(msg):
    """向 server 以 http 方式发送警告

    Args:
        msg: 报警信息
    """
    WarnToServerThread(http_server_url, msg).start()


def push_jpush(msg):
    """server 向 JPush 服务器发送警告

    Args:
        msg: 报警信息
    """
    WarnPushThread(base64_auth_string, msg).start()


class WarnToServerThread(threading.Thread):
    """发送警告到 server 的线程"""

    def __init__(self, server_url, msg):
        """构造函数

        Args:
            server_url: http 服务器地址
            msg: 要推送的消息
        """
        super().__init__()
        self.server_url = server_url
        self.msg = msg

    def run(self):
        """线程主函数

        发送时间及消息到服务器
        """
        try:
            headers = {
                'content-type': 'application/json'
            }
            values = {
                "push_msg": self.msg
            }
            data = urlencode(values).encode()
            req = rq.Request(self.server_url, data=data, headers=headers)
            response = rq.urlopen(req, timeout=5)
            log.debug('post to server: %s %s' % (response.status, response.reason))
        except Exception as e:
            log.error('post to server error: %s' % e)
        else:
            log.debug('post to server, warn msg: %s' % self.msg)


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
            response = rq.urlopen(req, timeout=10)
            log.debug('push: %s %s' % (response.status, response.reason))
        except Exception as e:
            log.error('push error: %s' % e)
        else:
            log.debug('push warn msg: %s' % self.msg)
