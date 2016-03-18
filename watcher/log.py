#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : log.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   :
# 

import logging
from logging import handlers


logger = None


def initialize_logging(to_file=True):
    """初始化日志系统

    使用本模块中的其他方法之前必须调用本方法。

    Args:
        to_file: 写入到文件系统 (default True)
    """

    global logger
    logger = logging.getLogger('eye')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # to file
    if to_file:
        fh = logging.handlers.RotatingFileHandler('logs/eye.log', maxBytes=52428800, backupCount=10)
        fh.setLevel(logging.DEBUG)
        fh.doRollover()
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # to screen
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)


def log(lvl, msg, *args, **kwargs):
    logger.log(lvl, msg, *args, **kwargs)
