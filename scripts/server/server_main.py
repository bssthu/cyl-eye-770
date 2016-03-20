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
import server


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
    if 'port' in configs \
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
    script_dir = os.path.join(os.path.dirname(server.__file__), os.path.pardir)
    root_dir = os.path.abspath(os.path.join(script_dir, os.path.pardir))
    config_file_name = os.path.abspath(os.path.join(os.path.join(root_dir, 'conf'), 'server_config.json'))
    configs = load_config(config_file_name)
    if configs is None:
        return

    # log init
    log_path = os.path.abspath(os.path.join(root_dir, 'logs'))
    log.initialize_logging('server', log_path, configs['enableLog'].lower() == 'true')
    log.info('server main: start')

    # quit & clean up
    log.info('server main: bye')
