#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : http_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import datetime
import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse
import log
import warn


class HttpThread(threading.Thread):
    """http 服务器，接收 POST 请求"""

    def __init__(self, http_config):
        """构造函数

        Args:
            http_config: 服务器配置信息
        """
        super().__init__()
        self.port = http_config['port']
        self.server = None
        self.running = True

    def run(self):
        """线程主函数

        循环运行，接受新的客户端的连接。
        """
        log.info('http thread: start, port: %d' % self.port)

        self.server = HTTPServer(('', self.port), RequestHandler)
        self.server.serve_forever()

        log.info('http thread: bye')

    def shutdown(self):
        if self.server is not None:
            self.server.shutdown()


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理"""

    def do_GET(self):
        try:
            self.send_response(200, message=None)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'server running. ')
            self.wfile.write(datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S').encode())
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
        post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        if 'push_msg' in post_data:
            warn.push(post_data['push_msg'][0])
