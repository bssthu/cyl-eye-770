#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : heartbeat_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import socket
import threading
import time
import log


class HeartbeatThread(threading.Thread):
    """向服务器发送心跳包的线程"""

    def __init__(self, server_config):
        """构造函数

        Args:
            server_config: 服务器配置信息
        """
        super().__init__()
        self.server_ip = server_config['ipAddress']
        self.server_port = server_config['port']
        self.interval = server_config['interval']
        self.running = True

    def run(self):
        """线程主函数

        循环运行，建立连接、发送心跳包，并在连接出错时重连。
        """
        log.info('heartbeat: start')
        while self.running:
            try:
                self.send_data()
            except Exception as e:      # 发生异常时重连
                log.error('heartbeat error: %s' % e)
                time.sleep(5)
        log.info('heartbeat: bye')

    def send_data(self):
        """建立连接并循环发送心跳包

        在超时时重连，在出错时返回。
        """
        client = self.connect()
        log.info('heartbeat: connected')
        timeout_count = 0
        while self.running:
            try:
                # 发送数据
                client.sendall(b'@')
                timeout_count = 0
                # 延时
                for i in range(0, self.interval):
                    time.sleep(1)
                    if not self.running:
                        break
            except socket.timeout:
                # 超时处理，超时5次时主动重连
                # 超时时间短是为了在需要时能快速退出
                timeout_count += 1
                if timeout_count >= 5:
                    timeout_count = 0
                    client = self.reconnect(client)
                    log.debug('heartbeat timeout, reconnect')
        try:
            client.close()
        except socket.error:
            pass
        except Exception as e:
            log.error('heartbeat exception when close: %s' % e)

    def connect(self):
        """尝试建立连接并设置超时参数"""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)
        try:
            client.connect((self.server_ip, self.server_port))
        except socket.timeout as e:
            raise socket.timeout('%s when connect' % e)
        client.settimeout(5)
        return client

    def reconnect(self, client):
        """重连 socket

        Args:
            client: 之前的 socket
        """
        try:
            client.close()
        except:
            log.error('heartbeat exception when close.')
        return self.connect()
