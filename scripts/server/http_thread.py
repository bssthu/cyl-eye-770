#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : http_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse
import log
import warn


heartbeat_timeout_count = 0


class HttpThread(threading.Thread):
    """http 服务器，接收 POST 请求"""

    def __init__(self, http_config):
        """构造函数

        Args:
            http_config: 服务器配置信息
        """
        super().__init__()
        self.port = http_config['port']
        self.heartbeat_timeout_limit = http_config['heartbeatTimeout']

        self.server = None
        self.running = True

        global heartbeat_timeout_count
        heartbeat_timeout_count = 0

    def run(self):
        """线程主函数

        启动定时器，用于检查心跳超时
        循环运行，接受新的客户端的连接。
        """
        log.info('http thread: start, port: %d' % self.port)

        self.server = HTTPServer(('', self.port), RequestHandler)

        self.start_heartbeat_timer()
        self.server.serve_forever()

        log.info('http thread: bye')

    def start_heartbeat_timer(self):
        """启动心跳检查定时器，每秒检查是否超时"""
        heartbeat_timer = threading.Timer(1.0, self.heartbeat_count_increase)
        heartbeat_timer.start()

    def heartbeat_count_increase(self):
        """检查心跳超时的定时器函数"""
        # 计数
        global heartbeat_timeout_count
        heartbeat_timeout_count += 1
        # 超时判断与处理
        if heartbeat_timeout_count == self.heartbeat_timeout_limit:
            log.warning('listen thread: heartbeat timeout')
            warn.push('与客户端的连接超时')
        # 继续定时检查
        if self.running:
            self.start_heartbeat_timer()

    def shutdown(self):
        """退出"""
        if self.server is not None:
            self.server.shutdown()
        self.running = False


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理"""

    alarm_history = []

    def do_GET(self):
        try:
            self.send_response(200, message=None)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # header
            self.wfile.write(b'<html><head>')
            self.wfile.write(b'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
            self.wfile.write(b'</head><body>')
            self.wfile.write(datetime.datetime.now().strftime('<div>current time: %Y-%m-%d, %H:%M:%S</div>').encode())
            self.wfile.write(b'<div>server running...</div>')
            self.wfile.write(b'<div>...</div>')
            self.wfile.write(b'<div>alarm history:</div>')
            # alarm body
            alarm_history = self.alarm_history.copy()
            alarm_history.reverse()
            for timestamp, alarm_msg in alarm_history:
                time_string = timestamp.strftime('%Y-%m-%d, %H:%M:%S')
                self.wfile.write(('<div>%s, %s</div>' % (time_string, alarm_msg)).encode())
            self.wfile.write(b'<div>...</div>')
            self.wfile.write(b'</body></html>')
        except IOError:
            self.send_error(404, message=None)

    def do_POST(self):
        try:
            self.send_response(200, message=None)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        except IOError:
            self.send_error(404, message=None)

        length = int(self.headers['Content-Length'])
        # 解码及处理
        push_msg, heartbeat_msg = decode_post_data(self.rfile.read(length))
        if push_msg is not None:
            # is push message
            self.alarm_history.append((datetime.datetime.now(), push_msg))
            warn.push_jpush(push_msg)
        if heartbeat_msg is not None and str(heartbeat_msg).startswith('@'*10):
            # is heartbeat message
            global heartbeat_timeout_count
            heartbeat_timeout_count = 0

    def log_request(self, code='-', size='-'):
        """覆盖基类方法，不输出到屏幕

        This is called by send_response().

        Args:
            code: 状态码
            size:
        """
        log.debug('%s - - "%s" %s %s' % (self.address_string(), self.requestline, str(code), str(size)))


def decode_post_data(raw_data):
    """HTTP POST 内容解析

        Args:
            raw_data: 要解析的内容

        Returns:
            push_msg, heartbeat_msg.
    """

    post_data = None
    try:
        # 先尝试解码
        post_data = urllib.parse.parse_qs(raw_data.decode(encoding='utf-8'))
    except UnicodeDecodeError:
        # 解码失败时，忽略错误再次解码，查找 encoding 字段
        post_data_force_decode = urllib.parse.parse_qs(raw_data.decode(encoding='utf-8', errors='ignore'))
        if 'encoding' in post_data_force_decode:
            # 尝试用指定的字符编码解码
            encoding = post_data_force_decode['encoding'][0]
            post_data = urllib.parse.parse_qs(raw_data.decode(encoding=encoding))

    # 判断解码是否成功、内容是否合理
    push_msg = None
    heartbeat_msg = None
    if post_data is not None and 'push_msg' in post_data:
        push_msg = post_data['push_msg'][0]
    if post_data is not None and 'heartbeat_msg' in post_data:
        heartbeat_msg = post_data['heartbeat_msg'][0]

    return push_msg, heartbeat_msg
