#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : watcher.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : main
# 

import json
import log
from heartbeat_thread import HeartbeatThread


def load_config(config_file_name):
    """载入配置文件并检查"""

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
            and 'watchPath' in configs \
            and 'email' in configs \
            and 'name' in configs['email'] \
            and 'password' in configs['email'] \
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
    configs = load_config('config.json')
    if configs is None:
        return

    # log init
    log.initialize_logging(configs['enableLog'].lower() == 'true')
    log.info('main: start')

    # threads
    heartbeat = HeartbeatThread(configs['heartBeatServer'])

    heartbeat.start()

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


if __name__ == '__main__':
    main()
