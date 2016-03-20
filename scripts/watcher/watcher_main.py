#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : watcher.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : watcher main
# 

import json
import os.path
import log
import watcher
from watcher.heartbeat_thread import HeartbeatThread
from watcher.mail_sender_thread import MailSenderThread


def load_config(config_file_name):
    """载入配置文件并检查

    Args:
        config_file_name: 配置文件名
    """

    # load
    try:
        with open(config_file_name) as config_data:
            configs = json.load(config_data)
    except:
        print('failed to load config from %s.' % config_file_name)
        return None

    # check
    if 'heartBeatServer' in configs \
            and 'ipAddress' in configs['heartBeatServer'] \
            and 'port' in configs['heartBeatServer'] \
            and 'interval' in configs['heartBeatServer'] \
            and 'email' in configs \
            and 'name' in configs['email'] \
            and 'password' in configs['email'] \
            and 'smtpServer' in configs['email'] \
            and 'interval' in configs['email'] \
            and 'watchPath' in configs['email'] \
            and 'fileExt' in configs['email'] \
            and 'fileNum' in configs['email'] \
            and 'jpush' in configs \
            and 'appKey' in configs['jpush'] \
            and 'masterSecret' in configs['jpush'] \
            and 'enableLog' in configs:
        return configs
    else:
        print('missing element(s) in %s.' % config_file_name)
        return None


def main():
    """主函数"""

    # config
    script_dir = os.path.join(os.path.dirname(watcher.__file__), os.path.pardir)
    root_dir = os.path.abspath(os.path.join(script_dir, os.path.pardir))
    config_file_name = os.path.abspath(os.path.join(os.path.join(root_dir, 'conf'), 'watcher_config.json'))
    configs = load_config(config_file_name)
    if configs is None:
        return

    # log init
    log_path = os.path.abspath(os.path.join(root_dir, 'logs'))
    log.initialize_logging('watcher', log_path, configs['enableLog'].lower() == 'true')
    log.info('watcher main: start')

    # threads
    heartbeat = HeartbeatThread(configs['heartBeatServer'])
    mail_sender = MailSenderThread(configs['email'])

    heartbeat.start()
    mail_sender.start()

    # keyboard
    try:
        print("enter 'q' to quit")
        while input() != 'q':
            print("enter 'q' to quit.")
    except KeyboardInterrupt:
        pass

    # quit & clean up
    heartbeat.running = False
    heartbeat.join()
    mail_sender.running = False
    mail_sender.join()

    log.info('watcher main: bye')
