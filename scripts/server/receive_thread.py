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


class ReceiveThread(threading.Thread):
    """负责与一个客户端通信，接收心跳包的线程"""

    def __init__(self, client_socket, _id, timeout, get_heartbeat_cb):
        """构造函数

        Args:
            client_socket: 与客户端通信的 socket
            _id: 客户端编号
            timeout: 超时时间
            get_heartbeat_cb: 收到心跳时的回调函数
        """
        super().__init__()
        self.client_socket = client_socket
        self.client_id = _id
        self.timeout_limit = timeout
        self.get_heartbeat_cb = get_heartbeat_cb
        self.timeout_count = 0
        self.running = True

    def run(self):
        """线程主函数

        循环运行，接收来自客户端的心跳包
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
                    self.running = False
                else:
                    # 收到数据
                    if is_heartbeat(data):
                        # 正常收到心跳包
                        self.timeout_count = 0
                        self.get_heartbeat_cb()
            except socket.timeout:
                self.timeout_count += 1
                # 超时退出
                if self.timeout_count >= self.timeout_limit:
                    log.warning('receive thread %d: timeout' % self.client_id)
                    self.running = False
            except Exception as e:
                # 发生异常
                log.error('receive thread %d error: %s' % (self.client_id, e))
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


def is_heartbeat(data):
    data_string = data.decode('utf-8', errors='ignore')
    if data_string.startswith('@'*10):
        return True
    else:
        return False
