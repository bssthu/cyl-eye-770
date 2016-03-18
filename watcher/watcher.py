#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : watcher.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : main
# 

import json
import log


class Watcher:
    def __init__(self):
        pass

    def main(self):
        # config
        config_file_name = 'config.json'
        try:
            with open(config_file_name) as config_data:
                configs = json.load(config_data)
        except:
            print('failed to load config from config.json.')
            return

        # log init
        log.initialize_logging(configs['enableLog'].lower() == 'true')
        log.info('main: start')


if __name__ == '__main__':
    watcher = Watcher()
    watcher.main()
