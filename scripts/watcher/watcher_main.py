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
import warn
import watcher
from watcher.file_checker_thread import FileCheckerThread
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
    if 'httpServer' in configs \
            and 'ipAddress' in configs['httpServer'] \
            and 'port' in configs['httpServer'] \
            and 'email' in configs \
            and 'name' in configs['email'] \
            and 'password' in configs['email'] \
            and 'smtpServer' in configs['email'] \
            and 'watchPath' in configs['email'] \
            and 'fileExt' in configs['email'] \
            and 'fileNum' in configs['email'] \
            and 'files' in configs \
            and 'alarmPath' in configs['files'] \
            and 'heartbeatPath' in configs['files']:
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
    enable_log = configs.get('enableLog', 'True').lower() == 'true'
    log_path = os.path.abspath(os.path.join(root_dir, 'logs'))
    log.initialize_logging('watcher', log_path, enable_log)
    log.info('watcher main: start')
    warn.initialize_warn(configs['httpServer'])

    # threads
    mail_sender = MailSenderThread(configs['email'])
    file_checker = FileCheckerThread(configs['httpServer'], configs['files'])

    mail_sender.start()
    file_checker.start()

    # keyboard
    try:
        print("enter 'q' to quit")
        while input() != 'q':
            print("enter 'q' to quit.")
    except KeyboardInterrupt:
        pass

    # quit & clean up
    mail_sender.running = False
    file_checker.running = False

    mail_sender.join()
    file_checker.join()
    warn.stop_warn()

    log.info('watcher main: bye')
