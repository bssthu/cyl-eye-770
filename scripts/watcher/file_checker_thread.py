#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : file_checker_thread.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 
# 

import datetime
import threading
import time
import log
import warn
from watcher.heartbeat_sender_thread import HeartbeatSenderThread


class FileCheckerThread(threading.Thread):
    """通过文件系统检查报警信息、心跳信息的线程"""

    def __init__(self, http_config, file_config):
        """构造函数

        Args:
            http_config: 服务器配置信息
            file_config: 文件监视信息
        """

        super().__init__()
        self.server_url = 'http://%s:%d/' % (http_config['ipAddress'], http_config['port'])
        self.alarm_path = file_config['alarmPath']
        self.heartbeat_path = file_config['heartbeatPath']
        self.date_format = file_config.get('dateFormat', '%Y/%m/%d %H:%M:%S')
        self.interval = file_config.get('interval', 40)

        self.alarm_check_time = datetime.datetime.now()     # 最近一次检查的时刻
        self.heartbeat_check_time = self.alarm_check_time
        self.running = True

    def run(self):
        """线程主函数

        循环运行，每隔一定时间，检查报警信息、心跳信息文件。

        文件中带有时间戳。比较文件中的时间戳与上次检查时间，可以判断是否收到了新的信息。
        """

        log.info('file checker: start')

        last_heartbeat_check_ok = True
        last_alarm_check_ok = True

        # loop & check
        while self.running:
            # heartbeat
            if not self.check_heartbeat() and last_heartbeat_check_ok:  # 刚刚失败
                warn.push('file checker: 心跳包查询失败')
                last_heartbeat_check_ok = False
            else:
                last_heartbeat_check_ok = True

            # alarm
            if not self.check_alarm() and last_alarm_check_ok:
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
        """检查心跳信息

        检查文件中的时间戳，如果文件中的比较新，则发送心跳包。

        Returns:
            是否成功
        """
        try:
            with open(self.heartbeat_path, 'r') as fp:
                line = fp.readline()
            if line is not None:
                date = datetime.datetime.strptime(line, self.date_format)
                # 文件中的时间戳较新，则向 server 发送心跳
                if date > self.heartbeat_check_time:
                    HeartbeatSenderThread(self.server_url).start()
                # update timestamp
                self.heartbeat_check_time = datetime.datetime.now()
                return True
        except Exception as e:
            log.error('file checker error when check heartbeat: %s' % e)
        return False

    def check_alarm(self):
        """检查报警信息

        检查每条警报的时间戳

        Returns:
            是否成功
        """
        try:
            alarms = []
            with open(self.alarm_path, 'r') as fp:
                for line in fp:
                    line = line.strip()
                    if line == '':
                        continue
                    words = line.split('\t', 1)
                    if len(words) == 2:
                        date = datetime.datetime.strptime(words[0], self.date_format)
                        # 这条警报的时间戳较新，则向 server 发送该警报
                        if date > self.alarm_check_time:
                            alarms.append(words[1].strip())
            # 发送新的警报信息
            if len(alarms) > 0:
                # update timestamp
                self.alarm_check_time = datetime.datetime.now()
                # send
                alarms.reverse()
                for alarm in alarms:
                    warn.push(alarm)
        except Exception as e:
            log.error('file checker error when check alarm: %s' % e)
            return False
        return True
