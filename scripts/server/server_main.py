#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : server.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : server main
# 

import json
import os.path
import log
import warn
import server
from server.http_thread import HttpThread


def load_config(config_file_name):
    """载入配置文件并检查

    Args:
        config_file_name: 配置文件名
    """

    # load
    try:
        with open(config_file_name) as config_data:
            configs = json.load(config_data)
    except Exception as e:
        print('failed to load config from %s.' % config_file_name)
        print(e)
        return None

    # check
    if 'httpServer' in configs \
            and 'port' in configs['httpServer']:
        return configs
    else:
        print('missing element(s) in %s.' % config_file_name)
        return None


def main():
    """主函数"""

    # config
    script_dir = os.path.join(os.path.dirname(server.__file__), os.path.pardir)
    root_dir = os.path.abspath(os.path.join(script_dir, os.path.pardir))
    config_file_name = os.path.abspath(os.path.join(os.path.join(root_dir, 'conf'), 'server_config.json'))
    configs = load_config(config_file_name)
    if configs is None:
        return

    # log init
    enable_log = configs.get('enableLog', 'True').lower() == 'true'
    log_path = os.path.abspath(os.path.join(root_dir, 'logs'))
    log.initialize_logging('server', log_path, enable_log)
    log.info('server main: start')
    warn_server_config = {'ipAddress': '127.0.0.1', 'port': configs['httpServer']['port']}
    warn.initialize_warn(warn_server_config)

    # threads
    http_server = HttpThread(configs['httpServer'])
    http_server.start()

    # keyboard
    try:
        print("enter 'q' to quit")
        while input() != 'q':
            print("enter 'q' to quit.")
    except KeyboardInterrupt:
        pass

    # quit & clean up
    warn.stop_warn()
    http_server.running = False
    http_server.shutdown()
    http_server.join()

    log.info('server main: bye')
