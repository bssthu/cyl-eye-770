#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : load_parser_config.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   :
# 

import os
import json


def load_parser_config():
    """载入配置文件

    Args:
        config_file_name: 配置文件名
    """

    # path
    script_dir = os.path.join(os.path.dirname(__file__), os.path.pardir)
    root_dir = os.path.abspath(os.path.join(script_dir, os.path.pardir))
    config_file_name = os.path.abspath(os.path.join(os.path.join(root_dir, 'conf'), 'parser_config.json'))

    # load
    try:
        with open(config_file_name) as config_data:
            configs = json.load(config_data)
    except Exception as e:
        print('failed to load config from %s.' % config_file_name)
        print(e)
        return None

    return configs


if __name__ == '__main__':
    config = load_parser_config()
