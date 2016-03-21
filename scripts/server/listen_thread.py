#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : listen_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import socket
import threading
import log


class ListenThread(threading.Thread):
    """监听来自客户端的连接的线程"""

    def __init__(self, server_config, timeout_cb):
        """构造函数

        Args:
            server_config: 服务器配置信息
            timeout_cb: 超时时的回调函数
        """
        super().__init__()
        self.port = server_config['port']
        self.timeout = server_config['timeout']
        self.timeout_cb = timeout_cb
        self.client = None
        self.running = True

    def run(self):
        """线程主函数

        循环运行，接受新的客户端的连接。
        """
        log.info('listen thread: start, port: %d' % self.port)
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', self.port))
            server.listen(1)
            server.settimeout(3)    # timeout: 3s
            while self.running:
                try:
                    conn, address = server.accept()
                    conn.settimeout(3)
                    self.client = conn
                    log.debug('new client from: %s' % str(address))
                except socket.timeout:
                    pass
            server.close()
            log.info('listen thread: bye')
        except Exception as e:
            log.error('listen thread error: %s' % e)
            self.running = False
