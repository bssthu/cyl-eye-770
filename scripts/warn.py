#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : warn.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 报警推送模块
#

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
    try:
        url = 'https://api.jpush.cn/v3/push'
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % base64_auth_string
        }
        values = {
            "platform": "all",
            "audience": "all",
            "notification": {
                "alert": msg
            }
        }
        data = urlencode(values).encode()
        req = rq.Request(url, data=data, headers=headers)
        response = rq.urlopen(req)
        log.debug('push: %s %s' % (response.status, response.reason))
    except Exception as e:
        log.error('push error: %s' % e)
    else:
        log.debug('push warn msg: %s' % msg)
