#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : receive_thread.py
# Author        : bssthu
# Project       : rtk_trans
# Description   :
#

import socket
import threading
import log
import warn


class ReceiveThread(threading.Thread):
    """负责与一个客户端通信，接收心跳包的线程"""

    def __init__(self, client_socket, _id, timeout_limit):
        """构造函数

        Args:
            client_socket: 与客户端通信的 socket
            _id: 客户端编号
            timeout_limit: 超时时间
        """
        super().__init__()
        self.client_socket = client_socket
        self.client_id = _id
        self.timeout_limit = timeout_limit
        self.timeout_count = 0
        self.running = True

    def run(self):
        """线程主函数

        循环运行，接收来自客户端的心跳包，当超时时报告。
        """
        log.info('receive thread %d: start' % self.client_id)
        self.client_socket.settimeout(1)
        while self.running:
            try:
                # rcv useless data
                data = self.client_socket.recv(4096)
                if data is None or len(data) == 0:
                    # 连接被关闭，报警
                    log.warning('receive thread %d: socket closed' % self.client_id)
                    warn.push('server: 与客户端的连接被关闭')
                    self.running = False
                self.timeout_count = 0
            except socket.timeout:
                self.timeout_count += 1
                if self.timeout_count >= self.timeout_limit:
                    # 超时报警，只报一次
                    log.warning('receive thread %d: timeout' % self.client_id)
                    warn.push('server: 与客户端通信超时')
                    self.running = False
            except Exception as e:
                # 发生异常，报警
                log.error('receive thread %d error: %s' % (self.client_id, e))
                warn.push('server: 服务器异常')
                self.running = False
        self.disconnect()
        log.info('receive thread %d: bye' % self.client_id)

    def disconnect(self):
        """断开连接"""
        try:
            self.client_socket.close()
        except socket.error:
            pass
        except Exception as e:
            log.error('sender thread %d exception when close: %s' % (self.client_id, e))
