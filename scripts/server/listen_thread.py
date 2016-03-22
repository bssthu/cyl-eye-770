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
import warn
from server.receive_thread import ReceiveThread


class ListenThread(threading.Thread):
    """监听来自客户端的连接的线程，并计时，当心跳超时时报告。"""

    def __init__(self, server_config):
        """构造函数

        Args:
            server_config: 服务器配置信息
        """
        super().__init__()
        self.port = server_config['port']
        self.timeout_limit = server_config['timeout']
        self.client_thread = None   # 接收心跳包的线程，单例
        self.client_id = 0
        self.timeout_count = 0
        self.running = True

    def get_heartbeat_cb(self):
        self.timeout_count = 0

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
                    # 等待新的连接接入
                    conn, address = server.accept()
                    conn.settimeout(3)
                    log.debug('new client %d from: %s' % (self.client_id, str(address)))
                    # stop old receive thread
                    self.stop_client_thread()
                    # start receive thread
                    self.client_thread = ReceiveThread(conn, self.client_id, self.timeout_limit, self.get_heartbeat_cb)
                    self.client_thread.start()
                    self.client_id += 1
                except socket.timeout:
                    # 计数，判断心跳包超时
                    self.timeout_count += 1
                    if self.timeout_count == int(self.timeout_limit / 3):
                        log.warning('listen thread: heartbeat timeout')
                        warn.push('与客户端的连接超时')
            server.close()
            self.stop_client_thread()
            log.info('listen thread: bye')
        except Exception as e:
            log.error('listen thread error: %s' % e)
            self.running = False

    def stop_client_thread(self):
        """停止与客户端通信接收数据的线程"""
        if self.client_thread is not None:
            self.client_thread.running = False
            self.client_thread.join()
