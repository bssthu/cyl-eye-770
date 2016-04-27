#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : http_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import urllib.parse
import log
import warn


class HttpThread(threading.Thread):
    """http 服务器，接收 POST 请求"""

    heartbeat_timeout_count = 0
    heartbeat_timeout_limit = 1
    last_heartbeat_time = ''

    def __init__(self, http_config):
        """构造函数

        Args:
            http_config: 服务器配置信息
        """
        super().__init__()
        self.port = http_config['port']
        HttpThread.heartbeat_timeout_limit = http_config['heartbeatTimeout']

        self.server = None
        self.running = True

    def run(self):
        """线程主函数

        启动定时器，用于检查心跳超时
        循环运行，接受新的客户端的连接。
        """
        log.info('http thread: start, port: %d' % self.port)

        self.server = ThreadingHTTPServer(('', self.port), RequestHandler)

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
        HttpThread.heartbeat_timeout_count += 1
        # 超时判断与处理
        if HttpThread.heartbeat_timeout_count == HttpThread.heartbeat_timeout_limit:
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


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """支持多线程"""
    pass


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理"""

    alarm_history = []

    def __init__(self, request, client_address, server):
        """设置超时"""
        self.timeout = 20
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        try:
            self.send_response(200, message=None)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # header
            self.wfile.write(b'<html><head>')
            self.wfile.write(b'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
            self.wfile.write(b'</head><body>')
            self.wfile.write(('<div>server time: %s</div>' % get_time_string()).encode())
            self.wfile.write(b'<div>server running...</div>')
            self.wfile.write(b'<div>...</div>')
            # heartbeat status
            if HttpThread.heartbeat_timeout_count < HttpThread.heartbeat_timeout_limit:
                self.wfile.write(b'<div>heartbeat state: ok</div>')
            else:
                self.wfile.write(b'<div>heartbeat state: timeout</div>')
            self.wfile.write(('<div>last heartbeat time: %s</div>' % HttpThread.last_heartbeat_time).encode())
            self.wfile.write(b'<div>...</div>')
            # alarm body
            self.wfile.write(b'<div>alarm history:</div>')
            alarm_history = self.alarm_history.copy()
            alarm_history.reverse()
            for timestamp, alarm_msg in alarm_history:
                self.wfile.write(('<div>%s, %s</div>' % (get_time_string(timestamp), alarm_msg)).encode())
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
        if heartbeat_msg is not None and str(heartbeat_msg).startswith('@'*10):
            # is heartbeat message
            if HttpThread.heartbeat_timeout_count >= HttpThread.heartbeat_timeout_limit:
                log.info('listen thread: heartbeat reconnected')
            HttpThread.heartbeat_timeout_count = 0  # clear count
            HttpThread.last_heartbeat_time = get_time_string()

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


def get_time_string(timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now()
    return timestamp.strftime('%Y-%m-%d, %H:%M:%S')
