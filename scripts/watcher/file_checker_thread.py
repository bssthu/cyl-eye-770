#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : file_checker_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import threading
import time
import log
import warn


class FileCheckerThread(threading.Thread):
    """查找待发文件并发送邮件的线程"""

    def __init__(self, http_config, file_config):
        """构造函数

        Args:
            http_config: 服务器配置信息
            file_config: 文件监视信息
        """
        super().__init__()
        self.server_url = 'http://%s:%d/' % (http_config['ipAddress'], http_config['port'])
        self.interval = file_config['interval']
        self.alarm_path = file_config['alarmPath']
        self.heartbeat_path = file_config['heartbeatPath']
        self.running = True

    def run(self):
        """线程主函数

        循环运行，每隔一定时间，检查报警信息、心跳信息文件。
        """

        # check
        log.info('file checker: start')

        last_heartbeat_check_ok = True
        last_alarm_check_ok = True

        # send & wait
        while self.running:
            try:
                self.check_heartbeat()
            except Exception as e:
                log.error('file checker error: %s' % e)
                if last_heartbeat_check_ok:
                    warn.push('file checker: 心跳包查询失败')
                    last_heartbeat_check_ok = False
            else:
                last_heartbeat_check_ok = True

            try:
                self.check_alarm()
            except Exception as e:
                log.error('file checker error: %s' % e)
                if last_alarm_check_ok:
                    warn.push('file checker: 报警信息查询失败')
                    last_alarm_check_ok = False
            else:
                last_alarm_check_ok = True

            # 延时
            for i in range(0, self.interval):
                time.sleep(1)
                if not self.running:
                    break
        log.info('file checker: bye')

    def check_heartbeat(self):
        """检查心跳信息"""
        with open(self.heartbeat_path, 'r') as fp:
            # TODO: check heartbeat
            pass

    def check_alarm(self):
        """检查报警信息"""
        with open(self.alarm_path, 'r') as fp:
            # TODO: check alarm
            pass
